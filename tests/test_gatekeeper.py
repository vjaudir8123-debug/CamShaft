from graph_gatekeeper.gatekeeper import CrossEncoderGatekeeper

def test_syntax_blindness():
    """Problem A: Variable Swapping Bug"""
    gatekeeper = CrossEncoderGatekeeper()
    
    query = "Create a session for the user ID."
    
    # Chunk 1: The correct logic
    chunk_1 = {
        "id": "correct",
        "content": "def create_session(user_id):\n    # creates a new session\n    pass"
    }
    
    # Chunk 2: The false positive (swapped words)
    chunk_2 = {
        "id": "false_positive",
        "content": "def create_user(session_id):\n    # creates a new user\n    pass"
    }
    
    results = gatekeeper.rank_and_prune(query, [chunk_1, chunk_2], top_k=2)
    
    # The correct one should be ranked higher
    assert results[0]["id"] == "correct"

def test_logical_negation():
    """Problem B: Eliminating Logical Negations"""
    gatekeeper = CrossEncoderGatekeeper()
    
    query = "Show me the error handling path when the user is NOT authenticated."
    
    # Chunk 1: Positive logic (false positive)
    chunk_1 = {
        "id": "false_positive",
        "content": "if (user.isAuthenticated()) {\n    showDashboard();\n}"
    }
    
    # Chunk 2: Negative logic (correct)
    chunk_2 = {
        "id": "correct",
        "content": "if (!user.isAuthenticated()) {\n    showLoginError();\n}"
    }
    
    results = gatekeeper.rank_and_prune(query, [chunk_1, chunk_2], top_k=2)
    
    # The correct one should be ranked higher
    assert results[0]["id"] == "correct"
