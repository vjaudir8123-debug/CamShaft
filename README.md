# CamShaft SDK

CamShaft is a unified Software Development Kit (SDK) that bundles **Graphifyy**, **Graphiti**, **FalkorDB**, and the **Stanford ColBERT Gatekeeper** into a single cohesive ecosystem. It is designed to run on *any machine without installing dependencies* using Docker.

## Why CamShaft?

Traditional retrieval models fail at strict syntactic matching (like `!user.isAuthenticated()`). The ColBERT Gatekeeper solves this via token-level MaxSim matching. By bundling this with Graphifyy (AST parsing) and Graphiti (memory tracking), you get an intelligent, temporally-aware, syntactically-perfect AI memory system.

## Run Anywhere (Zero Install)

Because installing Graphiti, FalkorDB, and PyTorch/ColBERT locally can lead to dependency hell, CamShaft provides a pre-configured Docker ecosystem.

1. Ensure [Docker](https://docs.docker.com/get-docker/) is installed.
2. In the root of this repository, run:
   ```bash
   docker compose up -d
   ```
3. Connect to the SDK container to run scripts:
   ```bash
   docker exec -it camshaft-sdk bash
   ```

## SDK Usage

Inside the Docker container (or if you manually installed it via `pip install -e .`), you can use the unified SDK:

```python
from camshaft import CamShaft

# Initialize the unified client. It automatically connects to FalkorDB.
# In Docker, the DB_HOST is automatically set to "falkordb"
import os
sdk = CamShaft(
    db_host=os.environ.get("DB_HOST", "localhost"),
    db_port=6379
)

# 1. Ingest an entire codebase via Graphifyy -> Graphiti -> FalkorDB
sdk.ingest("/path/to/your/codebase")

# 2. Query the exact syntax you need using the ColBERT Gatekeeper
results = sdk.query("Show me the code path when the user is NOT authenticated.")

for rank, chunk in enumerate(results, 1):
    print(f"Rank {rank}: [Score: {chunk['score']:.4f}]")
    print(chunk['content'])
```

## Running the Precision Tests

An `example.py` file is included to demonstrate the Gatekeeper catching Variable Swapping and Logical Negation bugs. Run it inside the container:

```bash
python example.py
```
