from transformers import AutoTokenizer, AutoModel
import torch
from torch import nn
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

class ColbertWrapper(nn.Module):
    def __init__(self, model_name):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.linear = nn.Linear(self.bert.config.hidden_size, 128, bias=False)
        
        # AutoModel drops the 'linear.weight' because it's not part of standard BERT.
        # We must manually fetch and apply the linear weights to get exact ColBERT math.
        try:
            model_path = hf_hub_download(repo_id=model_name, filename="model.safetensors")
            state_dict = load_file(model_path)
            self.linear.weight.data = state_dict['linear.weight']
        except Exception as e:
            print(f"Warning: Could not load linear weights: {e}")

    def forward(self, **kwargs):
        out = self.bert(**kwargs).last_hidden_state
        return self.linear(out)

class CrossEncoderGatekeeper:
    def __init__(self, model_name="colbert-ir/colbertv2.0", max_length=512):
        """
        Initializes the Late-Interaction Gatekeeper using Stanford ColBERTv2.0.
        Implemented purely in PyTorch to avoid nested dependency hell.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = ColbertWrapper(model_name)
        self.model.eval()
        self.max_length = max_length

    def rank_and_prune(self, query: str, chunks: list[dict], top_k: int = 2) -> list[dict]:
        """
        Scores them via ColBERT token-level MaxSim and returns the top_k matches.
        """
        if not chunks:
            return []

        # Stanford ColBERT requires [Q] token for queries and [D] for documents.
        # But for raw string matching without custom tokenizers, prepending them works.
        query = "[Q] " + query
        q_inputs = self.tokenizer(query, return_tensors="pt", max_length=self.max_length, truncation=True)
        
        with torch.no_grad():
            q_emb = self.model(**q_inputs)
            q_emb = torch.nn.functional.normalize(q_emb, p=2, dim=-1)

        scored_chunks = []
        for i, chunk in enumerate(chunks):
            doc = "[D] " + chunk["content"]
            d_inputs = self.tokenizer(doc, return_tensors="pt", max_length=self.max_length, truncation=True)
            
            with torch.no_grad():
                d_emb = self.model(**d_inputs)
                d_emb = torch.nn.functional.normalize(d_emb, p=2, dim=-1)
                
            # ColBERT MaxSim: Dot product between query and doc tokens
            sim_matrix = torch.bmm(q_emb, d_emb.transpose(1, 2))
            max_sims = sim_matrix.max(dim=2).values
            score = max_sims.sum().item()
            
            scored_chunks.append({
                "id": chunk.get("id", i),
                "content": chunk["content"],
                "score": score
            })
            
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]
