import os
import json
import numpy as np
import glob
from sentence_transformers import SentenceTransformer, util
import torch

class LegalSearchEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2', embeddings_dir='embeddings', processed_dir='processed_data'):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Loading embedding model: {model_name} on {self.device}...")
        self.model = SentenceTransformer(model_name, device=self.device)
        
        self.embeddings_dir = embeddings_dir
        self.processed_dir = processed_dir
        
        self.all_embeddings = []
        self.all_metadata = []
        self.id_to_text = {}
        
        self._load_data()

    def _load_data(self):
        print("Loading embeddings and metadata...")
        npy_files = glob.glob(os.path.join(self.embeddings_dir, 'embeddings_*.npy'))
        
        for npy_file in npy_files:
            # e.g., embeddings_constitutional_constitutional.npy
            basename = os.path.basename(npy_file).replace('embeddings_', '').replace('.npy', '')
            meta_file = os.path.join(self.embeddings_dir, f'metadata_{basename}.json')
            
            if os.path.exists(meta_file):
                # Load embeddings
                embs = np.load(npy_file)
                self.all_embeddings.append(embs)
                
                # Load metadata
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    self.all_metadata.extend(meta)
            else:
                print(f"[-] Warning: Missing metadata for {npy_file}")

        if self.all_embeddings:
            self.embeddings_tensor = torch.from_numpy(np.vstack(self.all_embeddings)).to(self.device)
            print(f"Total chunks loaded: {len(self.all_metadata)}")
        else:
            print("[-] No embeddings found!")
            self.embeddings_tensor = None

        # Map IDs to text for retrieval
        print("Mapping text chunks...")
        jsonl_files = glob.glob(os.path.join(self.processed_dir, '**', '*.jsonl'), recursive=True)
        for jsonl_file in jsonl_files:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    self.id_to_text[data['id']] = data.get('text', '')

    def search(self, query, top_k=5):
        if self.embeddings_tensor is None:
            return []
            
        # Embed query
        query_embedding = self.model.encode(query, convert_to_tensor=True, device=self.device)
        
        # Compute cosine similarity
        cos_scores = util.cos_sim(query_embedding, self.embeddings_tensor)[0]
        
        # Get top-k indices
        top_results = torch.topk(cos_scores, k=min(top_k, len(cos_scores)))
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            meta = self.all_metadata[idx]
            results.append({
                'score': float(score),
                'id': meta['id'],
                'case_name': meta['case_name'],
                'legal_issue': meta['legal_issue'],
                'domain': meta['domain'],
                'subdomain': meta['subdomain'],
                'text': self.id_to_text.get(meta['id'], "Text not found"),
                'source': meta['source']
            })
            
        return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Indian Legal Semantic Search Engine")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--top_k", type=int, default=3, help="Number of results to return")
    args = parser.parse_args()

    engine = LegalSearchEngine()
    results = engine.search(args.query, top_k=args.top_k)
    
    print(f"\n--- Search Results for: '{args.query}' ---\n")
    for i, res in enumerate(results, 1):
        print(f"Result #{i} (Score: {res['score']:.4f})")
        print(f"Case: {res['case_name']}")
        print(f"Domain: {res['domain']} | Subdomain: {res['subdomain']}")
        print(f"Issue: {res['legal_issue']}")
        print(f"Snippet: {res['text'][:300]}...")
        print(f"Source: {res['source']}")
        print("-" * 50)

if __name__ == "__main__":
    main()
