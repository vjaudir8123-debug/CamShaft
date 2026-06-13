import os
from falkordb import FalkorDB

class GraphManager:
    def __init__(self, host="localhost", port=6379, graph_name="code_graph"):
        self.host = host
        self.port = port
        self.graph_name = graph_name
        self.db = FalkorDB(host=self.host, port=self.port)
        
        # Ensures graph exists or selects it
        self.graph = self.db.select_graph(self.graph_name)

    def insert_chunk(self, chunk_id, content, metadata=None):
        """Insert a simple node representing a code chunk for testing."""
        metadata_str = str(metadata) if metadata else "{}"
        query = f"""
        CREATE (:Chunk {{id: '{chunk_id}', content: $content, metadata: '{metadata_str}'}})
        """
        self.graph.query(query, {"content": content})

    def search_chunks(self, query_text: str, top_k: int = 15) -> list[dict]:
        """
        Placeholder for Graphiti/FalkorDB Vector/Hybrid Search.
        In reality, this would use Graphiti's hybrid search to fetch top matches.
        For our mock DB, we'll return all chunks up to top_k and let the Cross-Encoder do the heavy lifting.
        """
        result = self.graph.query("MATCH (c:Chunk) RETURN c.id as id, c.content as content")
        chunks = []
        for row in result.result_set:
            chunks.append({"id": row[0], "content": row[1]})
        return chunks[:top_k]
