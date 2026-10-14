import re
import math
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.ticket import Ticket, TicketStatus
from app.schemas.intelligence import RelatedTicketItem, RelatedTicketsResponse
from app.core.logging import logger

# Lightweight English stop-words list for IT service text processing
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "did",
    "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further",
    "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its",
    "itself", "let's", "me", "more", "most", "my", "myself", "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "she", "should", "so", "some",
    "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then",
    "there", "these", "they", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "we", "were", "what", "when", "where", "which",
    "while", "who", "whom", "why", "with", "won't", "would", "you", "your", "yours",
    "yourself", "yourselves", "please", "help", "issue", "problem", "cannot", "able"
}


class TextVectorizer:
    """
    Pure-Python TF-IDF and Cosine Similarity Engine.
    Designed for zero external ML dependencies, deterministic calculations,
    and clear interview explainability for an Associate Product Engineer.
    """

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Normalize text: lowercase, strip punctuation, filter short tokens and stop words.
        """
        if not text:
            return []
        # Replace non-alphanumeric characters with spaces
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        tokens = cleaned.split()
        # Keep tokens with length >= 2 that are not pure stop words
        return [t for t in tokens if len(t) >= 2 and t not in STOP_WORDS]

    @classmethod
    def compute_tf(cls, tokens: List[str]) -> Dict[str, float]:
        """Term Frequency: normalized count of term occurrences in a document."""
        if not tokens:
            return {}
        counts = Counter(tokens)
        total_tokens = len(tokens)
        return {term: count / total_tokens for term, count in counts.items()}

    @classmethod
    def compute_idf(cls, corpus_tokens: List[List[str]]) -> Dict[str, float]:
        """
        Inverse Document Frequency: smooth formula ln((1 + |D|) / (1 + df(t))) + 1.0.
        Prevents division by zero and provides smooth scaling for rare terms.
        """
        num_docs = len(corpus_tokens)
        doc_freq = defaultdict(int)

        for doc in corpus_tokens:
            unique_terms = set(doc)
            for term in unique_terms:
                doc_freq[term] += 1

        idf = {}
        for term, df in doc_freq.items():
            idf[term] = math.log((1.0 + num_docs) / (1.0 + df)) + 1.0

        return idf

    @classmethod
    def compute_tfidf_vector(cls, tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
        """TF-IDF vector representation for a single document."""
        tf = cls.compute_tf(tokens)
        return {term: tf_val * idf.get(term, 1.0) for term, tf_val in tf.items()}

    @staticmethod
    def cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        """
        Cosine similarity between two sparse vector representations:
        cos(A, B) = (A . B) / (||A|| * ||B||)
        """
        if not vec_a or not vec_b:
            return 0.0

        # Dot product over shared terms
        common_terms = set(vec_a.keys()) & set(vec_b.keys())
        dot_product = sum(vec_a[t] * vec_b[t] for t in common_terms)
        if dot_product <= 0:
            return 0.0

        norm_a = math.sqrt(sum(val * val for val in vec_a.values()))
        norm_b = math.sqrt(sum(val * val for val in vec_b.values()))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        similarity = dot_product / (norm_a * norm_b)
        return min(max(similarity, 0.0), 1.0)


class RelatedTicketService:
    """
    Service responsible for detecting similar historical or active tickets
    using TF-IDF + Cosine Similarity with candidate set pre-filtering.
    """

    DEFAULT_SIMILARITY_THRESHOLD = 0.65
    DEFAULT_MAX_RESULTS = 5
    CANDIDATE_LOOKBACK_DAYS = 90

    def __init__(self, db: Session):
        self.db = db

    def get_candidate_tickets(self, target_ticket: Ticket) -> List[Ticket]:
        """
        Fetch a sensible candidate set rather than scanning the entire historical database:
        - Same category OR active statuses (OPEN, ASSIGNED, IN_PROGRESS, REOPENED)
        - Exclude target ticket itself
        - Order by recent activity
        """
        query = self.db.query(Ticket).filter(Ticket.id != target_ticket.id)

        # Include tickets in the same category or active tickets
        active_statuses = [
            TicketStatus.OPEN,
            TicketStatus.ASSIGNED,
            TicketStatus.IN_PROGRESS,
            TicketStatus.REOPENED,
        ]

        query = query.filter(
            or_(
                Ticket.category_id == target_ticket.category_id,
                Ticket.status.in_(active_statuses),
            )
        )

        # Limit candidate pool for performance and responsiveness
        return query.order_by(Ticket.created_at.desc()).limit(100).all()

    def find_related_tickets(
        self,
        target_ticket: Ticket,
        threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        limit: int = DEFAULT_MAX_RESULTS,
    ) -> RelatedTicketsResponse:
        """
        Execute TF-IDF + Cosine Similarity matching against candidate tickets.
        Only tickets meeting or exceeding the threshold are returned, sorted descending.
        """
        candidates = self.get_candidate_tickets(target_ticket)
        if not candidates:
            return RelatedTicketsResponse(
                target_ticket_id=target_ticket.id,
                threshold_used=threshold,
                total_candidates_analyzed=0,
                related_tickets=[],
            )

        # 1. Combine title & description and tokenize
        target_text = f"{target_ticket.title} {target_ticket.description or ''}".strip()
        target_tokens = TextVectorizer.tokenize(target_text)

        # If target has no meaningful tokens after cleaning, return empty matches
        if not target_tokens:
            return RelatedTicketsResponse(
                target_ticket_id=target_ticket.id,
                threshold_used=threshold,
                total_candidates_analyzed=len(candidates),
                related_tickets=[],
            )

        # Tokenize all candidate documents
        candidate_tokens_map = {}
        all_docs_tokens = [target_tokens]

        for cand in candidates:
            cand_text = f"{cand.title} {cand.description or ''}".strip()
            cand_tokens = TextVectorizer.tokenize(cand_text)
            candidate_tokens_map[cand.id] = (cand, cand_tokens)
            all_docs_tokens.append(cand_tokens)

        # 2. Compute IDF across the corpus
        idf = TextVectorizer.compute_idf(all_docs_tokens)

        # 3. Vectorize target ticket
        target_vec = TextVectorizer.compute_tfidf_vector(target_tokens, idf)

        # 4. Compare each candidate using Cosine Similarity
        matches: List[Tuple[Ticket, float]] = []
        for cand_id, (cand, cand_tokens) in candidate_tokens_map.items():
            if not cand_tokens:
                continue
            cand_vec = TextVectorizer.compute_tfidf_vector(cand_tokens, idf)
            sim_score = TextVectorizer.cosine_similarity(target_vec, cand_vec)

            # Round to 4 decimal places
            sim_rounded = round(sim_score, 4)
            if sim_rounded >= threshold:
                matches.append((cand, sim_rounded))

        # 5. Sort matches by similarity score descending, tie-breaking by created_at desc
        matches.sort(key=lambda item: (item[1], item[0].created_at), reverse=True)

        # 6. Take top K matches
        top_matches = matches[:limit]

        related_items = [
            RelatedTicketItem(
                ticket_id=ticket.id,
                title=ticket.title,
                status=ticket.status,
                priority=ticket.priority,
                category_id=ticket.category_id,
                category_name=ticket.category.name if ticket.category else None,
                similarity_score=score,
                similarity_percentage=int(round(score * 100)),
                created_at=ticket.created_at,
            )
            for ticket, score in top_matches
        ]

        logger.info(
            f"RelatedTicketService: Ticket #{target_ticket.id} evaluated against "
            f"{len(candidates)} candidates. Found {len(related_items)} matches (threshold={threshold})."
        )

        return RelatedTicketsResponse(
            target_ticket_id=target_ticket.id,
            threshold_used=threshold,
            total_candidates_analyzed=len(candidates),
            related_tickets=related_items,
        )
