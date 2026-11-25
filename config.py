import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DOCS_DIR = DATA_DIR / "raw_documents"
GLOSSARY_DIR = DATA_DIR / "glossary"
SAVED_MODELS_DIR = BASE_DIR / "saved_models"
TEMP_AUDIO_DIR = BASE_DIR / "temp_audio"
EVAL_DATASET_PATH = DATA_DIR / "evaluation_dataset.json"

# Ensure directories exist
for path in [DATA_DIR, RAW_DOCS_DIR, GLOSSARY_DIR, SAVED_MODELS_DIR, TEMP_AUDIO_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Supported Languages
SUPPORTED_LANGUAGES = {
    "hi": "Hindi (हिन्दी)",
    "mr": "Marathi (मराठी)",
    "en": "English"
}

# Agricultural helpline and fallback
KISAN_CALL_CENTRE = "1800-180-1551"
DEFAULT_KVK_ADVISORY = "कृषी विज्ञान केंद्र (KVK) किंवा किसान कॉल सेंटरशी (1800-180-1551) संपर्क साधा."

# Confidence and Decision Gate Thresholds
MIN_ASR_CONFIDENCE = 0.55
MIN_RETRIEVAL_SCORE = 0.38
CONFIDENCE_THRESHOLD = 0.50
MAX_AUDIO_DURATION_SEC = 30

# Vector & RAG settings
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 5
RERANK_TOP_N = 3

# Model Settings
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
WHISPER_MODEL_SIZE = "tiny"  # Fast, low-latency for local execution
