import os
import subprocess
from typing import List, Dict, Any
from .pipeline import GatekeeperPipeline

class CamShaft:
    def __init__(self, db_host="localhost", db_port=6379, model_name="colbert-ir/colbertv2.0"):
        """
        Initializes the CamShaft SDK.
        Connects to the underlying FalkorDB and loads the ColBERT ranking pipeline.
        """
        self.pipeline = GatekeeperPipeline(db_host, db_port, model_name)
        
    def ingest(self, directory_path: str = ".") -> bool:
        """
        Ingests a directory into the Graph/Vector database.
        Runs Graphifyy to analyze the code structure and push to Graphiti/FalkorDB.
        """
        print(f"Starting Graphifyy ingestion for: {directory_path}")
        
        # Graphifyy is a CLI tool. We wrap it for the SDK.
        try:
            result = subprocess.run(
                ["graphify", directory_path],
                capture_output=True,
                text=True,
                check=True
            )
            print("Ingestion complete!")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print("Ingestion failed!")
            print(e.stderr)
            return False

    def query(self, text: str, initial_k: int = 15, final_k: int = 2) -> List[Dict[str, Any]]:
        """
        Queries the knowledge graph and applies token-level ColBERT MaxSim reranking
        to ensure logical precision (e.g., catching '!' operators).
        """
        print(f"Querying CamShaft memory: '{text}'")
        results = self.pipeline.run(text, initial_top_k=initial_k, final_top_k=final_k)
        return results
