import sys
import subprocess
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import config
from train_and_index import main as train_and_index_main

def start():
    print("=" * 65)
    print("🌾 AGRI VOICE ASSISTANT: INITIALIZING & AUTO-TRAINING")
    print("=" * 65)

    # 1. Automatically train intent classifier and index verified knowledge base
    print("\n[1/2] Ingesting verified ICAR documents and training models...")
    train_and_index_main()

    # 2. Start Web & API Server
    print("\n[2/2] Starting Agri Voice Assistant Server on port 8000...")
    print("=" * 65)
    print("🚀 Landing Page & Web UI: http://127.0.0.1:8000")
    print("📚 Interactive API Docs: http://127.0.0.1:8000/docs")
    print("=" * 65)
    print("Press CTRL+C to stop the server.\n")

    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    start()
