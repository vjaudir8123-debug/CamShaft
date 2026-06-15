import argparse
import os
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
import httpx
import json
from .client import CamShaft
from .search import perform_deep_search

app = FastAPI(title="CamShaft Proxy Server")

# Global variables for the SDK and target model URL
sdk = None
TARGET_OPENAI_URL = os.environ.get("TARGET_OPENAI_URL", "https://api.openai.com/v1")

@app.on_event("startup")
async def startup_event():
    global sdk
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = int(os.environ.get("DB_PORT", 6379))
    sdk = CamShaft(db_host=db_host, db_port=db_port)
    print("CamShaft SDK initialized in Proxy.")

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    messages = body.get("messages", [])
    
    if not messages:
        return {"error": "No messages provided"}
    
    # Get the last user message safely handling multimodal arrays
    raw_content = messages[-1].get("content", "")
    query_text = ""
    
    if isinstance(raw_content, list):
        for item in raw_content:
            if item.get("type") == "text":
                query_text = item.get("text", "")
                break
    else:
        query_text = str(raw_content)
        
    if not query_text:
        return {"error": "No text content found in the last message to query."}
    # Check for deep search trigger
    deep_search_context = ""
    clean_query_text = query_text
    if query_text.strip().startswith("/search "):
        search_query = query_text.strip()[8:].strip()
        clean_query_text = search_query # Query the codebase with the actual query, not the command
        deep_search_context = await perform_deep_search(search_query, TARGET_OPENAI_URL)
    
    # 1. Query the CamShaft Memory
    results = sdk.query(clean_query_text)
    
    # 2. Augment the System Prompt with Web and/or Memory Context
    combined_context = ""
    
    if deep_search_context:
        combined_context += f"--- DEEP WEB SEARCH CONTEXT ---\n{deep_search_context}\n-------------------------------\n\n"
        
    if results:
        combined_context += "--- GRAPHITI/COLBERT MEMORY CONTEXT ---\n"
        for r in results:
            combined_context += f"{r['content']}\n"
        combined_context += "---------------------------------------\n"
        
    if combined_context:
        # Prepend the context to the last user message safely
        augmented_messages = list(messages)
        if isinstance(raw_content, list):
            for item in augmented_messages[-1]["content"]:
                if item.get("type") == "text":
                    item["text"] = f"{combined_context}\nUser Request: {item.get('text', '').replace('/search ', '', 1)}"
                    break
        else:
            augmented_messages[-1]["content"] = f"{combined_context}\nUser Request: {clean_query_text}"
        
        body["messages"] = augmented_messages
    
    # Remove problematic headers before forwarding
    headers = dict(request.headers)
    for h in ["host", "content-length", "authorization"]:
        headers.pop(h, None)
    
    # 3. Forward to the actual LLM (Streaming support)
    client = httpx.AsyncClient()
    req = client.build_request("POST", f"{TARGET_OPENAI_URL}/chat/completions", headers=headers, json=body)
    
    response = await client.send(req, stream=True)
    
    async def stream_response():
        try:
            async for chunk in response.aiter_bytes():
                yield chunk
        finally:
            await client.aclose()
            
    # Remove problematic response headers
    resp_headers = dict(response.headers)
    for h in ["content-encoding", "content-length", "transfer-encoding"]:
        resp_headers.pop(h, None)
        
    return StreamingResponse(
        stream_response(),
        status_code=response.status_code,
        headers=resp_headers
    )

def main():
    parser = argparse.ArgumentParser(description="Start the CamShaft OpenAI-Compatible Proxy")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the proxy to")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the proxy on")
    parser.add_argument("--db-host", type=str, default="localhost", help="FalkorDB host")
    parser.add_argument("--db-port", type=int, default=6379, help="FalkorDB port")
    parser.add_argument("--target-url", type=str, default="https://api.openai.com/v1", help="Actual OpenAI API URL to forward to (or Ollama/Local LLM URL)")
    
    args = parser.parse_args()
    
    os.environ["DB_HOST"] = args.db_host
    os.environ["DB_PORT"] = str(args.db_port)
    os.environ["TARGET_OPENAI_URL"] = args.target_url
    
    print(f"Starting CamShaft Proxy on http://{args.host}:{args.port}/v1")
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
