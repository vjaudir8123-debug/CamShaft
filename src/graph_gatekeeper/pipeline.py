from .db import GraphManager
from .gatekeeper import CrossEncoderGatekeeper

class GatekeeperPipeline:
    def __init__(self, db_host="localhost", db_port=6379, top_k_retrieval=15):
        self.db_manager = GraphManager(host=db_host, port=db_port)
        self.gatekeeper = CrossEncoderGatekeeper()
        self.top_k_retrieval = top_k_retrieval

    def query_context(self, query: str, final_k: int = 2) -> list[dict]:
        """
        1. Retrieves broad candidates from FalkorDB/Graphiti.
        2. Prunes them using the Cross-Encoder.
        """
        print(f"[*] Step 1: Retrieving top {self.top_k_retrieval} candidates from Graph/DB...")
        candidates = self.db_manager.search_chunks(query, top_k=self.top_k_retrieval)
        print(f"    -> Found {len(candidates)} candidates.")

        if not candidates:
            print("    -> No candidates found. Aborting.")
            return []

        print(f"[*] Step 2: Passing through ms-marco-MiniLM-L6-v2 Cross-Encoder...")
        pruned_results = self.gatekeeper.rank_and_prune(query, candidates, top_k=final_k)
        
        print(f"[*] Step 3: Successfully pruned context down to top {len(pruned_results)} matches.")
        return pruned_results
