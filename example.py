from graph_gatekeeper.gatekeeper import CrossEncoderGatekeeper

def main():
    print("Initializing Gatekeeper...")
    gatekeeper = CrossEncoderGatekeeper()
    
    # Problem A: Syntax Blindness / Variable Swapping
    print("\n--- Testing Problem A: Variable Swapping ---")
    query_a = "I need to explicitly create a session for a user id."
    chunks_a = [
        {"id": 1, "content": "def create_user(session_id):\n    db.insert_user(session_id)"},
        {"id": 2, "content": "def create_session(user_id):\n    db.insert_session(user_id)"}
    ]
    
    results_a = gatekeeper.rank_and_prune(query_a, chunks_a, top_k=2)
    for r in results_a:
        print(f"Score: {r['score']:.4f} | Chunk {r['id']}")

    # Problem B: Logical Negation
    print("\n--- Testing Problem B: Logical Negation ---")
    query_b = "Show me the code path when the user is NOT authenticated."
    chunks_b = [
        {"id": 1, "content": "if (user.isAuthenticated()) { grant_access(); }"},
        {"id": 2, "content": "if (!user.isAuthenticated()) { throw new AuthError(); }"}
    ]
    
    results_b = gatekeeper.rank_and_prune(query_b, chunks_b, top_k=2)
    for r in results_b:
        print(f"Score: {r['score']:.4f} | Chunk {r['id']}")

if __name__ == "__main__":
    main()
