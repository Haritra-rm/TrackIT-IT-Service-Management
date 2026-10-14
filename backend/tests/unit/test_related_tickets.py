import pytest
from app.services.related_ticket_service import TextVectorizer, RelatedTicketService
from app.models.ticket import Ticket, TicketPriority, TicketStatus


def test_text_vectorizer_normalization_and_tokenization():
    text = "VPN connection failed! Cannot connect to Office VPN (Error: 403)..."
    tokens = TextVectorizer.tokenize(text)
    assert "vpn" in tokens
    assert "connection" in tokens
    assert "failed" in tokens
    assert "connect" in tokens
    assert "office" in tokens
    # Punctuation stripped and lowercased
    assert "403" in tokens
    # Stop words like "to" filtered out
    assert "to" not in tokens


def test_text_vectorizer_empty_and_punctuation_handling():
    assert TextVectorizer.tokenize("") == []
    assert TextVectorizer.tokenize("   ") == []
    assert TextVectorizer.tokenize("!@#$%^&*()") == []
    # Single character tokens filtered
    assert TextVectorizer.tokenize("a b c d e") == []


def test_cosine_similarity_identical_and_orthogonal():
    doc1 = ["vpn", "connection", "error"]
    doc2 = ["vpn", "connection", "error"]
    doc3 = ["printer", "paper", "jam"]

    corpus = [doc1, doc2, doc3]
    idf = TextVectorizer.compute_idf(corpus)

    vec1 = TextVectorizer.compute_tfidf_vector(doc1, idf)
    vec2 = TextVectorizer.compute_tfidf_vector(doc2, idf)
    vec3 = TextVectorizer.compute_tfidf_vector(doc3, idf)

    # Identical documents should have cosine similarity == 1.0
    sim_identical = TextVectorizer.cosine_similarity(vec1, vec2)
    assert round(sim_identical, 4) == 1.0

    # Orthogonal documents with zero shared terms should have similarity == 0.0
    sim_disjoint = TextVectorizer.cosine_similarity(vec1, vec3)
    assert sim_disjoint == 0.0


def test_related_ticket_detection_ranking_and_threshold(db_session, employee_user, sample_category):
    # Create target ticket
    target = Ticket(
        title="VPN connection is not working",
        description="I cannot connect to the office VPN from home.",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )
    db_session.add(target)

    # Candidate 1: Highly similar (same problem, strong overlapping keywords)
    cand_high = Ticket(
        title="Office VPN connection failure",
        description="Cannot connect to office VPN tunnel from remote network.",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,
        status=TicketStatus.IN_PROGRESS,
        created_by=employee_user.id,
    )
    # Candidate 2: Moderately similar
    cand_med = Ticket(
        title="Office VPN authentication error",
        description="VPN login portal rejected credentials.",
        category_id=sample_category.id,
        priority=TicketPriority.MEDIUM,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )
    # Candidate 3: Unrelated ticket
    cand_unrelated = Ticket(
        title="Laptop battery draining very fast",
        description="MacBook battery drops from 100% to 0% in under one hour.",
        category_id=sample_category.id,
        priority=TicketPriority.LOW,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )

    db_session.add_all([cand_high, cand_med, cand_unrelated])
    db_session.commit()
    db_session.refresh(target)

    service = RelatedTicketService(db_session)

    # Test with standard threshold 0.45 to observe ranking
    response = service.find_related_tickets(target, threshold=0.45, limit=5)
    matched_ids = [m.ticket_id for m in response.related_tickets]

    # cand_high must be first, followed by cand_med, unrelated must not be present
    assert cand_high.id in matched_ids
    assert cand_unrelated.id not in matched_ids
    assert response.related_tickets[0].ticket_id == cand_high.id

    # Test ranking: first match score >= second match score
    if len(response.related_tickets) > 1:
        assert response.related_tickets[0].similarity_score >= response.related_tickets[1].similarity_score

    # Test strict threshold 0.95 (should exclude lower scores)
    strict_res = service.find_related_tickets(target, threshold=0.98, limit=5)
    assert len(strict_res.related_tickets) == 0


def test_related_ticket_detection_empty_description_safe(db_session, employee_user, sample_category):
    target = Ticket(
        title="VPN gateway down",
        description="",  # empty description
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )
    cand = Ticket(
        title="VPN gateway unreachable",
        description="",
        category_id=sample_category.id,
        priority=TicketPriority.HIGH,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )
    db_session.add_all([target, cand])
    db_session.commit()

    service = RelatedTicketService(db_session)
    res = service.find_related_tickets(target, threshold=0.5)
    assert len(res.related_tickets) >= 1
    assert res.related_tickets[0].ticket_id == cand.id


def test_related_ticket_no_matches_returns_empty_list(db_session, employee_user, sample_category):
    target = Ticket(
        title="Unique quantum entanglement failure in laboratory server",
        description="Rare superconducting qubit decoherence detected during scheduled calibration.",
        category_id=sample_category.id,
        priority=TicketPriority.LOW,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )
    cand = Ticket(
        title="Need new wireless mouse for desk",
        description="Mouse scroll wheel is broken.",
        category_id=sample_category.id,
        priority=TicketPriority.LOW,
        status=TicketStatus.OPEN,
        created_by=employee_user.id,
    )
    db_session.add_all([target, cand])
    db_session.commit()

    service = RelatedTicketService(db_session)
    res = service.find_related_tickets(target, threshold=0.65)
    assert res.related_tickets == []
