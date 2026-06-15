# CamShaft SDK & OpenAI Proxy

CamShaft bundles **Graphifyy**, **Graphiti**, **FalkorDB**, and the **Stanford ColBERT Gatekeeper** into an **OpenAI-Compatible Proxy Server**. 

This allows you to bake CamShaft directly into the "brain" of any AI tool (Cursor, Antigravity, Claude, Local LLMs). To your AI assistant, CamShaft *is* the model.

## Why a Proxy Server?

Traditional AI tools use static retrieval or MCP plugins that only run when the AI decides to call them. 

By running CamShaft as an OpenAI Proxy:
1. Every message you send is intercepted.
2. The exact, syntactically-perfect ColBERT code chunks are fetched.
3. Your temporal Graphiti memory is updated.
4. The memory is invisibly merged into your prompt and forwarded to the actual LLM (Claude, Llama, etc.).

## Installation

```bash
pip install -e .
```

*Note: Ensure you have a FalkorDB instance running locally (e.g., `docker run -p 6379:6379 falkordb/falkordb`) or use a cloud URL.*

## Usage: Baking it into your AI

Once installed, simply run the CamShaft proxy server:

```bash
# Start the proxy (default runs on http://127.0.0.1:8000)
camshaft --target-url "https://api.openai.com/v1"
```

### In Cursor / Antigravity
1. Open Settings -> Models.
2. Add a Custom OpenAI URL: `http://127.0.0.1:8000/v1`
3. Enter any API key (or your actual OpenAI key if forwarding to OpenAI).
4. Start chatting! Every message is now intercepted, augmented with ColBERT/Graphiti memory, and forwarded.

### Python SDK Usage

If you prefer to bypass the proxy and use the memory engine in your own scripts (e.g. to wire directly into a LangChain app or Anthropic/OpenAI SDK), you can use the SDK natively. See `example_llm_integration.py` for a full working example of how to inject CamShaft memory into an LLM prompt.

```python
from camshaft import CamShaft

sdk = CamShaft(db_host="localhost", db_port=6379)
results = sdk.query("Where do we authenticate the user?")

for rank, chunk in enumerate(results, 1):
    print(f"Rank {rank}: [Score: {chunk['score']:.4f}]")
    print(chunk['content'])
```

## Running the Precision Tests

An `example.py` file is included to demonstrate the Gatekeeper catching Variable Swapping and Logical Negation bugs. 

```bash
python example.py
```
