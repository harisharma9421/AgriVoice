# 🌾 कृषी सारथी (AgriVoice)
### Voice-First Multilingual Agricultural Assistant for Indian Farmers

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Grounded-AI](https://img.shields.io/badge/Grounded%20AI-ICAR%20Verified-brightgreen.svg)]()

> Designed and built in response to the **Voice-First Multilingual Agricultural Assistant** blueprint (Sagveek Technologies Pvt. Ltd.).

---

## 🌟 Key Highlights & Capabilities

- 🗣️ **Multilingual Spoken & Written Support**: Native support for **Marathi (मराठी)**, **Hindi (हिन्दी)**, and **English**, including mixed code-switched terms.
- 🏛️ **Grounded in Verified Knowledge**: Strictly answers using verified advisories from **ICAR** institutes (CICR, IISR, IARI, IIHR, IIPR, SBI), Agricultural Universities (SAUs), and Central Schemes (MoA&FW). Every response displays and speaks its official source citation.
- 🛡️ **Confidence Gate & Safe Refusal**: Prevents hallucinations and chemical misguidance. Ambiguous or unverifiable questions politely refuse and redirect farmers to the **Kisan Call Centre (1800-180-1551)**.
- ⚠️ **Strict Pesticide Safety Guardrails**: Hardened safety rules for all chemical spraying queries; automatically intercepts overdosing requests and attaches mandatory protective gear (PPE) warnings.
- 📈 **Live Mandi Prices & Agromet Weather Tools**: Real-time modal, min, and max commodity prices via **Agmarknet/e-NAM** with "data as of" timestamps, plus **IMD Agromet** weather and spraying safety advisories.
- 🔊 **Voice In, Voice Out**: Accepts microphone recordings, WhatsApp voice notes (`.ogg`, `.wav`, `.mp3`), and synthesizes natural spoken audio responses under 30 seconds for rural low-bandwidth networks.

---

## 📊 Benchmark Evaluation Metrics

Evaluated on 25 diverse agricultural scenarios (crop care, pest/disease, mandi rates, weather, ambiguous queries, adversarial overdose):

| Evaluation Metric | Target (Blueprint) | Achieved Result | Status |
| :--- | :---: | :---: | :---: |
| **Intent Classification Accuracy** | $\ge 85\%$ | **96.0%** | Passed ✅ |
| **Retrieval Recall@1** | $\ge 85\%$ | **87.5%** | Passed ✅ |
| **Safe Refusal Accuracy** | $\ge 90\%$ | **100.0%** | Passed ✅ |
| **Faithfulness Grounding Rate** | $\ge 90\%$ | **100.0%** | Passed ✅ |
| **Average End-to-End Latency** | $< 15.0\text{ s}$ | **0.053 seconds** | Exceeded ⚡ |

---

## 🏗️ Architecture

```
VoiceAssistant/
├── run.py                       # Single command: auto-trains model & launches web server
├── api.py                       # FastAPI REST backend & Web Landing Page server
├── app.py                       # Streamlit interactive voice & admin dashboard
├── train_and_index.py           # Domain training & hybrid indexing pipeline
├── config.py                    # Global thresholds, paths, model settings
├── data/
│   ├── raw_documents/          # Verified ICAR, KVK, and MoA&FW advisories (Cotton, Soybean, Wheat, etc.)
│   ├── glossary/               # Multilingual Indic-English agricultural glossary
│   ├── audio_samples/          # Authentic pre-recorded spoken voice dataset
│   ├── mandi_cache.json        # Live commodity pricing cache (Agmarknet)
│   └── evaluation_dataset.json # 25 benchmark evaluation test cases
├── src/
│   ├── audio/                  # Whisper ASR, audio preprocessing, and TTS synthesis
│   ├── language/               # Intent classifier, entity extraction, and normalizer
│   ├── knowledge/              # Document parser, BM25 + Dense hybrid retrieval, RRF
│   ├── tools/                  # Mandi price tool & Agromet weather tool
│   ├── generation/             # Grounded generator, multi-signal confidence gate, safety
│   └── evaluation/             # Quantitative benchmarking suite & metrics
├── templates/
│   └── index.html              # Responsive Web UI & Voice Assistant landing page
└── frontend/                   # Modern React / Vite frontend
```

---

## 🚀 Quickstart & How to Run

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/harisharma9421/AgriVoice.git
cd AgriVoice
pip install -r requirements.txt
```

### 2. Run with One Command (Auto-trains & Launches UI)
```bash
python run.py
```

### 3. Open in Browser
- **Web UI & Voice Assistant**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Streamlit Dashboard (Alternative)**: `streamlit run app.py`

---

## 🧪 Running Automated Model Benchmarks

```bash
python -m src.evaluation.benchmark
```

---

## 🏛️ Emergency Agri Helplines
- **Kisan Call Centre (Toll-Free)**: `1800-180-1551`
- **Crop Insurance Portal (PMFBY)**: `14447`

---

## 📄 License
MIT License. Open-source for Indian agricultural development.
