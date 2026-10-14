from app.services.priority_service import PriorityRecommendationEngine
from app.models.ticket import TicketPriority


def test_priority_recommender_security_incident():
    rec = PriorityRecommendationEngine.recommend(
        category_name="Security",
        affected_users=1,
        is_security_incident=True,
    )
    assert rec["recommended_priority"] == TicketPriority.CRITICAL
    assert rec["sla_hours"] == 4


def test_priority_recommender_system_outage():
    rec = PriorityRecommendationEngine.recommend(
        category_name="Hardware",
        affected_users=1,
        is_system_down=True,
    )
    assert rec["recommended_priority"] == TicketPriority.CRITICAL
    assert rec["sla_hours"] == 4


def test_priority_recommender_network_large_blast_radius():
    rec = PriorityRecommendationEngine.recommend(
        category_name="Network",
        affected_users=25,
        business_impact="DEPARTMENT_BLOCKED",
    )
    assert rec["recommended_priority"] == TicketPriority.HIGH
    assert rec["sla_hours"] == 8
    assert "- Network category" in rec["reasoning"]
    assert "- 25 affected users" in rec["reasoning"]
    assert "- Department blocked" in rec["reasoning"]


def test_priority_recommender_team_impact():
    rec = PriorityRecommendationEngine.recommend(
        category_name="Software",
        affected_users=6,
        business_impact="HIGH",
    )
    assert rec["recommended_priority"] == TicketPriority.HIGH
    assert rec["sla_hours"] == 8


def test_priority_recommender_single_user_low():
    rec = PriorityRecommendationEngine.recommend(
        category_name="Other",
        affected_users=1,
        business_impact="LOW",
    )
    assert rec["recommended_priority"] == TicketPriority.LOW
    assert rec["sla_hours"] == 72
