import time
from src.knowledge.ingestion import DocumentIngestionPipeline
from src.knowledge.vector_store import HybridVectorStore
from src.language.intent_classifier import AgriculturalIntentClassifier
import config

def main():
    print("=" * 60)
    print("🌾 AGRI VOICE ASSISTANT: TRAINING & INDEXING PIPELINE")
    print("=" * 60)
    t0 = time.time()

    # Step 1: Ingest verified agricultural documents
    print("\n[Step 1/3] Loading and chunking verified agricultural documents...")
    pipeline = DocumentIngestionPipeline(config.RAW_DOCS_DIR)
    chunks = pipeline.run()

    # Step 2: Build hybrid dense + BM25 vector index with Reciprocal Rank Fusion
    print("\n[Step 2/3] Building multilingual hybrid index (BM25 + Semantic Vectorizer)...")
    store = HybridVectorStore(config.SAVED_MODELS_DIR)
    store.build_index(chunks)

    # Step 3: Train domain agricultural intent & entity classifier
    print("\n[Step 3/3] Training Indic agricultural intent classifier...")
    classifier = AgriculturalIntentClassifier(config.SAVED_MODELS_DIR / "intent_classifier.pkl")
    classifier.train()

    duration = time.time() - t0
    print("\n" + "=" * 60)
    print(f"✅ Training and Indexing Complete in {duration:.2f} seconds!")
    print(f"📦 Total passages indexed: {len(chunks)}")
    print(f"💾 Artifacts saved to: {config.SAVED_MODELS_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
