import os
from camshaft import CamShaft

def main():
    # 1. Initialize the CamShaft SDK (Connects to FalkorDB & Gatekeeper)
    sdk = CamShaft(db_host="localhost", db_port=6379)
    
    user_prompt = "How do we authenticate the user?"
    print(f"User Prompt: {user_prompt}\n")
    
    # 2. Get exact context chunks from CamShaft using ColBERT MaxSim
    print("Fetching relevant context from CamShaft memory...")
    results = sdk.query(user_prompt)
    
    # 3. Build the memory context string
    memory_context = "--- RELEVANT CODEBASE CONTEXT ---\n"
    if not results:
        memory_context += "No context found.\n"
    for chunk in results:
        memory_context += f"{chunk['content']}\n"
    memory_context += "---------------------------------\n"
    
    # 4. Combine memory context and user prompt
    final_prompt = f"{memory_context}\nPlease answer the user's question based on the context above. User question: {user_prompt}"
    
    print("\nFinal Prompt that would be sent to the LLM:")
    print("=" * 50)
    print(final_prompt)
    print("=" * 50)
    
    # 5. Example of sending to an AI (e.g. Anthropic/Claude)
    # Uncomment and use your actual API key to run this live.
    
    """
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    print("\nSending to Claude...")
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": final_prompt}
        ]
    )
    print("Claude's Response:")
    print(response.content[0].text)
    """

if __name__ == "__main__":
    main()
