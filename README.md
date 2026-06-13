# Graph Gatekeeper (CamShaft)

Graph Gatekeeper is a high-precision retrieval and ranking pipeline designed to sit between a Graph/Vector Database (like FalkorDB) and an LLM. It solves the common "vibe-matching" problems of traditional Bi-Encoders and Cross-Encoders by implementing token-level late interaction via Stanford's ColBERTv2.0.

## Why ColBERT?

Traditional retrieval models (Bi-Encoders) and even global rerankers (Cross-Encoders) often fail at strict syntactic matching. For example, they may treat `user.isAuthenticated()` and `!user.isAuthenticated()` identically because the `!` token is drowned out by the semantic weight of the rest of the sentence.

ColBERT solves this by computing a **MaxSim** matrix. It maintains distinct vectors for every token in the query and compares them explicitly to every token in the candidate code chunk. This explicitly preserves logical operators and variable nuances, acting as a highly precise "Gatekeeper".

## Architecture

1. **Graph/Vector DB Retrieval (`src/graph_gatekeeper/db.py`)**
   - Connects to FalkorDB and retrieves a broad list of candidate nodes using standard hybrid search.
2. **Late-Interaction Gatekeeper (`src/graph_gatekeeper/gatekeeper.py`)**
   - Implements a pure PyTorch Stanford ColBERTv2.0 scoring pipeline.
   - Takes the raw database candidates and re-ranks them using token-level matching to prune irrelevant or logically incorrect chunks.
3. **Pipeline Orchestration (`src/graph_gatekeeper/pipeline.py`)**
   - Glues the database retrieval and ColBERT ranking into a single, seamless pipeline.

## Installation

This package requires Python 3.10+.

```bash
pip install -e .
```

Dependencies:
- `falkordb`
- `graphiti-core`
- `graphifyy`
- `torch`
- `transformers`
- `huggingface_hub`
- `safetensors`

## Usage

```python
from graph_gatekeeper import GatekeeperPipeline

# Initialize the pipeline
pipeline = GatekeeperPipeline(
    db_host="localhost", 
    db_port=6379, 
    colbert_model="colbert-ir/colbertv2.0"
)

# Run a query
query = "Show me the code path when the user is NOT authenticated."
results = pipeline.run(query, initial_top_k=15, final_top_k=2)

for rank, chunk in enumerate(results, 1):
    print(f"Rank {rank}: [Score: {chunk['score']:.4f}]")
    print(chunk['content'])
    print("---")
```

## Running the Precision Tests

An `example.py` file is included in the root directory to demonstrate the Gatekeeper's ability to catch Variable Swapping and Logical Negation bugs.

```bash
PYTHONPATH=src python example.py
```
