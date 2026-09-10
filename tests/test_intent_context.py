from app.agents.intent_context_agent import IntentContextAgent, StructuredContext

def test_intent_context_extraction():
    agent = IntentContextAgent()
    query = "I am a fisherman near Ratnagiri. Can I go fishing tomorrow at 6 AM? Find a good PFZ and the safest route."
    ctx = agent.extract_context(query=query, session_id="test_session_1")

    assert ctx.intent == "fishing_safety_and_route"
    assert ctx.user_type == "fisherman"
    assert "Ratnagiri" in ctx.location_name
    assert ctx.departure_hour == 6
    assert ctx.needs_pfz is True
    assert ctx.needs_route is True
    assert ctx.needs_weather is True
    assert ctx.needs_geofence_check is True

def test_multi_turn_context_continuity():
    agent = IntentContextAgent()
    session_id = "multi_turn_test_session"

    # Turn 1: Initial query
    ctx1 = agent.extract_context(
        query="Find a safe fishing zone near Ratnagiri tomorrow.",
        session_id=session_id
    )
    assert "Ratnagiri" in ctx1.location_name
    assert ctx1.needs_pfz is True

    # Turn 2: Follow-up specifying departure hour
    ctx2 = agent.extract_context(
        query="What about 6 AM?",
        session_id=session_id
    )
    # Must preserve Ratnagiri and fishing intent from Turn 1!
    assert "Ratnagiri" in ctx2.location_name
    assert ctx2.departure_hour == 6
    assert ctx2.needs_pfz is True

    # Turn 3: Follow-up modifying departure hour
    ctx3 = agent.extract_context(
        query="What if I leave at 8 AM instead?",
        session_id=session_id
    )
    assert "Ratnagiri" in ctx3.location_name
    assert ctx3.departure_hour == 8
    assert ctx3.needs_pfz is True
