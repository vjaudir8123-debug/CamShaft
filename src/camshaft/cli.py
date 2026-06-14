import argparse
import sys
from .client import CamShaft

def main():
    parser = argparse.ArgumentParser(description="CamShaft: Unified Graph/Vector DB Retrieval and ColBERT Gatekeeper SDK")
    
    # Global DB connection arguments
    parser.add_argument("--db-host", type=str, default="localhost", help="FalkorDB host address")
    parser.add_argument("--db-port", type=int, default=6379, help="FalkorDB port")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a directory into FalkorDB via Graphifyy and Graphiti")
    ingest_parser.add_argument("path", type=str, default=".", nargs="?", help="Path to the codebase directory")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query the database using the ColBERT Gatekeeper")
    query_parser.add_argument("text", type=str, help="The query string")
    query_parser.add_argument("--initial-k", type=int, default=15, help="Initial number of chunks to fetch from DB")
    query_parser.add_argument("--final-k", type=int, default=2, help="Final number of chunks to return after ColBERT ranking")
    
    args = parser.parse_args()
    
    # Initialize SDK
    sdk = CamShaft(db_host=args.db_host, db_port=args.db_port)
    
    if args.command == "ingest":
        success = sdk.ingest(args.path)
        if not success:
            sys.exit(1)
            
    elif args.command == "query":
        results = sdk.query(args.text, initial_k=args.initial_k, final_k=args.final_k)
        print("\n--- CamShaft Gatekeeper Results ---")
        for rank, chunk in enumerate(results, 1):
            print(f"Rank {rank} | Score: {chunk['score']:.4f}")
            print(f"Content:\n{chunk['content']}\n")
            print("-" * 40)

if __name__ == "__main__":
    main()
