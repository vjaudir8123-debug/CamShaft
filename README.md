# CamShaft SDK

CamShaft is a unified Software Development Kit (SDK) and Command Line Interface (CLI) that bundles **Graphifyy**, **Graphiti**, **FalkorDB**, and the **Stanford ColBERT Gatekeeper** into a single cohesive ecosystem.

## Why CamShaft?

Traditional retrieval models fail at strict syntactic matching (like `!user.isAuthenticated()`). The ColBERT Gatekeeper solves this via token-level MaxSim matching. By bundling this with Graphifyy (AST parsing) and Graphiti (memory tracking), you get an intelligent, temporally-aware, syntactically-perfect AI memory system.

## Installation

This is a pure Python package. Install it globally or within your virtual environment:

```bash
pip install -e .
```

> **Note:** Because this SDK relies on FalkorDB for its graph/vector database, you must ensure you have a FalkorDB instance running locally (e.g., via Docker `docker run -p 6379:6379 falkordb/falkordb`) or have a cloud URL ready before running ingestion or queries.

## CLI Usage

Installing this package registers the `camshaft` command in your terminal, so you can run it from anywhere.

### 1. Ingest Codebase
To scan an entire codebase via Graphifyy, map the AST to Graphiti, and save it in FalkorDB:
```bash
camshaft ingest /path/to/your/codebase --db-host localhost --db-port 6379
```

### 2. Query Memory
To retrieve candidate chunks and apply the ColBERT Gatekeeper token-level MaxSim logic:
```bash
camshaft query "Show me the code path when the user is NOT authenticated."
```

## Python SDK Usage

You can also use the unified SDK directly in your Python scripts:

```python
from camshaft import CamShaft

sdk = CamShaft(db_host="localhost", db_port=6379)

# 1. Ingest
sdk.ingest("/path/to/your/codebase")

# 2. Query
results = sdk.query("Show me the code path when the user is NOT authenticated.")

for rank, chunk in enumerate(results, 1):
    print(f"Rank {rank}: [Score: {chunk['score']:.4f}]")
    print(chunk['content'])
```

## Running the Precision Tests

An `example.py` file is included to demonstrate the Gatekeeper catching Variable Swapping and Logical Negation bugs. 

```bash
python example.py
```
