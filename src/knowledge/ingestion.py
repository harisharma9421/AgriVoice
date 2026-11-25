import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import config

class DocumentIngestionPipeline:
    def __init__(self, raw_docs_dir: Path = config.RAW_DOCS_DIR):
        self.raw_docs_dir = Path(raw_docs_dir)

    def load_raw_documents(self) -> List[Dict[str, Any]]:
        documents = []
        for file_path in self.raw_docs_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        documents.extend(data)
                    elif isinstance(data, dict):
                        documents.append(data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        return documents

    def chunk_and_process(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        seen_hashes = set()

        for doc in documents:
            # Blueprint requirement: only verified content is retrievable
            if not doc.get("verified_status", False):
                continue

            doc_id = doc.get("doc_id", "DOC_UNKNOWN")
            crop = doc.get("crop", "general").lower()
            topic = doc.get("topic", "general")
            source = doc.get("source", "Verified Agri Source")
            region = doc.get("region", "India")
            season = doc.get("season", "All")
            last_updated = doc.get("last_updated", "")

            # Create entries for each available language so multilingual queries match directly
            lang_contents = [
                ("mr", doc.get("title_mr", ""), doc.get("content_mr", "")),
                ("hi", doc.get("title_hi", ""), doc.get("content_hi", "")),
                ("en", doc.get("topic", ""), doc.get("content_en", ""))
            ]

            for lang, title, content in lang_contents:
                if not content:
                    continue

                # Keep complete advisory per language intact so symptoms and remedy are retrieved together
                full_text = f"{title}: {content}" if title else content
                chunk_hash = hashlib.sha256((doc_id + lang + full_text).encode("utf-8")).hexdigest()
                if chunk_hash not in seen_hashes:
                    seen_hashes.add(chunk_hash)
                    chunks.append({
                        "chunk_id": f"{doc_id}_{lang}",
                        "doc_id": doc_id,
                        "crop": crop,
                        "topic": topic,
                        "language": lang,
                        "title": title,
                        "source": source,
                        "region": region,
                        "season": season,
                        "last_updated": last_updated,
                        "text": full_text,
                        "raw_content": content
                    })

        return chunks

    def run(self) -> List[Dict[str, Any]]:
        raw_docs = self.load_raw_documents()
        chunks = self.chunk_and_process(raw_docs)
        print(f"Ingestion complete: Loaded {len(raw_docs)} verified documents, generated {len(chunks)} multilingual chunks.")
        return chunks
