import json
import re
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
import config

def tokenize_indic(text: str) -> List[str]:
    """Tokenize Indic (Hindi, Marathi) and English text into words and n-grams."""
    text = text.lower()
    text = re.sub(r"[।,\.!\?\":;\(\)\[\]\-]+", " ", text)
    tokens = [t.strip() for t in text.split() if len(t.strip()) > 1]
    ngrams = []
    for token in tokens:
        if len(token) >= 4:
            ngrams.extend([token[i:i+3] for i in range(len(token)-2)])
    return tokens + ngrams

class HybridVectorStore:
    def __init__(self, index_dir: Path = config.SAVED_MODELS_DIR):
        self.index_dir = Path(index_dir)
        self.index_file = self.index_dir / "hybrid_index.pkl"
        self.chunks: List[Dict[str, Any]] = []
        self.bm25: Optional[BM25Okapi] = None
        self.tokenized_corpus: List[List[str]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.vectorizer = None
        self._init_vectorizer()

    def _init_vectorizer(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(
            tokenizer=tokenize_indic,
            token_pattern=None,
            max_features=2048,
            ngram_range=(1, 2),
            sublinear_tf=True,
            norm='l2'
        )

    def build_index(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        if not chunks:
            print("Warning: No chunks provided to build index.")
            return

        # 1. Sparse BM25 Index
        self.tokenized_corpus = [tokenize_indic(c["text"]) for c in chunks]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        # 2. Multilingual Semantic Dense Embeddings
        texts = [c["text"] for c in chunks]
        self.embeddings = self.vectorizer.fit_transform(texts).toarray().astype(np.float32)

        self.save_index()
        print(f"Hybrid index built and saved with {len(chunks)} passages.")

    def save_index(self):
        self.index_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "chunks": self.chunks,
            "tokenized_corpus": self.tokenized_corpus,
            "embeddings": self.embeddings,
            "vectorizer": self.vectorizer
        }
        with open(self.index_file, "wb") as f:
            pickle.dump(data, f)

    def load_index(self) -> bool:
        if not self.index_file.exists():
            return False
        try:
            with open(self.index_file, "rb") as f:
                data = pickle.load(f)
            self.chunks = data["chunks"]
            self.tokenized_corpus = data["tokenized_corpus"]
            self.bm25 = BM25Okapi(self.tokenized_corpus)
            self.embeddings = data["embeddings"]
            self.vectorizer = data.get("vectorizer")
            print(f"Loaded hybrid index with {len(self.chunks)} chunks.")
            return True
        except Exception as e:
            print(f"Failed to load hybrid index: {e}")
            return False

    def search(self, query: str, crop_filter: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.chunks or self.bm25 is None:
            if not self.load_index():
                return []

        query_tokens = tokenize_indic(query)
        bm25_scores = np.array(self.bm25.get_scores(query_tokens))
        max_bm25 = np.max(bm25_scores) if np.max(bm25_scores) > 0 else 1.0
        norm_bm25 = bm25_scores / max_bm25

        # Dense retrieval
        if self.vectorizer is not None and self.embeddings is not None:
            q_emb = self.vectorizer.transform([query]).toarray()[0]
            norm_q = np.linalg.norm(q_emb)
            if norm_q > 0:
                q_emb = q_emb / norm_q
            dense_scores = np.dot(self.embeddings, q_emb)
        else:
            dense_scores = norm_bm25

        # Reciprocal Rank Fusion (RRF) with k=60
        bm25_ranked_idx = np.argsort(norm_bm25)[::-1]
        dense_ranked_idx = np.argsort(dense_scores)[::-1]

        bm25_ranks = {idx: rank + 1 for rank, idx in enumerate(bm25_ranked_idx)}
        dense_ranks = {idx: rank + 1 for rank, idx in enumerate(dense_ranked_idx)}

        scored_candidates = []
        for i, chunk in enumerate(self.chunks):
            # Metadata filtering
            if crop_filter and crop_filter != "all" and crop_filter != "unknown":
                if chunk.get("crop") not in [crop_filter, "all", "general"]:
                    continue

            rrf_score = (1.0 / (60 + bm25_ranks[i])) + (1.0 / (60 + dense_ranks[i]))
            # Combined relevance confidence score (0 to 1 scale)
            relevance_confidence = float(0.45 * norm_bm25[i] + 0.55 * max(0.0, float(dense_scores[i])))

            scored_candidates.append({
                "chunk": chunk,
                "rrf_score": float(rrf_score),
                "relevance_confidence": round(relevance_confidence, 4),
                "bm25_score": round(float(norm_bm25[i]), 4),
                "dense_score": round(float(dense_scores[i]), 4)
            })

        scored_candidates.sort(key=lambda x: (x["rrf_score"], x["relevance_confidence"]), reverse=True)
        return scored_candidates[:top_k]
