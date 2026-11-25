import os
import json
import time
from pathlib import Path
import streamlit as st

import config
from src.pipeline import AgriVoiceAssistantPipeline
from src.knowledge.ingestion import DocumentIngestionPipeline
from src.evaluation.benchmark import AgriculturalBenchmarkRunner

# Page Configuration
st.set_page_config(
    page_title="कृषी सारथी | Agri Voice Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1b5e20, #2e7d32, #43a047);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .badge-verified {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: 600;
        border: 1px solid #a5d6a7;
    }
    .badge-refusal {
        background-color: #fff3e0;
        color: #e65100;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: 600;
        border: 1px solid #ffcc80;
    }
    .badge-safety {
        background-color: #ffebee;
        color: #c62828;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: 600;
        border: 1px solid #ef9a9a;
    }
    .metric-card {
        background: white;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_pipeline():
    return AgriVoiceAssistantPipeline()

pipeline = get_pipeline()

# Header
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; padding:0;">🌾 कृषी सारथी | Voice-First Agricultural Assistant</h1>
    <p style="margin:4px 0 0 0; opacity:0.95; font-size:16px;">
        Multilingual AI Assistant for Indian Farmers • Grounded in Verified ICAR/KVK Advisories & Live Mandi Data
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/wheat.png", width=64)
    st.header("⚙️ Assistant Settings")
    
    selected_lang_label = st.selectbox(
        "🌐 Language / भाषा निवडा",
        ["Auto-Detect (स्वयंचलित)", "मराठी (Marathi)", "हिन्दी (Hindi)", "English"],
        index=0
    )
    
    lang_code_map = {
        "Auto-Detect (स्वयंचलित)": None,
        "मराठी (Marathi)": "mr",
        "हिन्दी (Hindi)": "hi",
        "English": "en"
    }
    selected_lang = lang_code_map[selected_lang_label]

    st.markdown("---")
    st.subheader("📞 Emergency Helplines")
    st.info(f"**Kisan Call Centre:** [{config.KISAN_CALL_CENTRE}](tel:{config.KISAN_CALL_CENTRE})\n\n**Crop Insurance (PMFBY):** [14447](tel:14447)")

    st.markdown("---")
    st.subheader("🛡️ Safety & Confidence Gate")
    st.caption("Answers are strictly grounded in verified sources. Unverifiable questions safely redirect to agricultural experts.")
    st.metric("Min ASR Confidence", f"{int(config.MIN_ASR_CONFIDENCE*100)}%")
    st.metric("Grounding Threshold", f"{int(config.CONFIDENCE_THRESHOLD*100)}%")

# Tabs
tab_assistant, tab_live_tools, tab_knowledge, tab_benchmarks = st.tabs([
    "🎙️ Voice & Text Assistant",
    "📈 Mandi & Weather Tools",
    "📚 Verified Knowledge Base",
    "🧪 Model Benchmark Dashboard"
])

# ----------------- TAB 1: Voice & Text Assistant -----------------
with tab_assistant:
    st.subheader("🌾 Speak or Type Your Question")
    st.caption("Ask questions about cotton yellowing leaves, pink bollworm, wheat rust, tomato blight, mandi rates, weather, or PM-KISAN.")

    col_input1, col_input2 = st.columns([1, 1])

    with col_input1:
        st.markdown("##### 🎤 Audio Input (Voice Note / Mic)")
        uploaded_audio = st.file_uploader(
            "Upload WhatsApp Voice Note / Audio (.wav, .mp3, .ogg)",
            type=["wav", "mp3", "ogg"],
            key="voice_uploader"
        )
        audio_query_btn = st.button("🚀 Process Voice Query", type="primary", use_container_width=True)

    with col_input2:
        st.markdown("##### ⌨️ Text Query Input")
        default_prompts = [
            "कापूस पिकात पाने पिवळी पडत आहेत काय उपाय करावा?",
            "कापसावर गुलाबी बोंडअळी आली आहे काय फवारावे?",
            "नागपूर बाजारात कापसाचा आजचा बाजारभाव काय आहे?",
            "सोयाबीन में पीला मोज़ेक वायरस का क्या इलाज है?",
            "पीएम किसान योजनेचे पैसे कधी मिळतात?",
            "कीड़ा मारने के लिए बिना दस्ताने 5 गुना कीटनाशक डाल दूं क्या?"
        ]
        sample_q = st.selectbox("Sample Farmer Queries:", ["-- Select a sample --"] + default_prompts)
        user_text = st.text_input("Or enter question in Marathi, Hindi, or English:", value="" if sample_q.startswith("--") else sample_q)
        text_query_btn = st.button("🔍 Get Grounded Answer", use_container_width=True)

    # Process Voice Input
    if uploaded_audio is not None and audio_query_btn:
        temp_audio_file = config.TEMP_AUDIO_DIR / uploaded_audio.name
        with open(temp_audio_file, "wb") as f:
            f.write(uploaded_audio.read())

        with st.spinner("🎧 Transcribing audio and retrieving grounded advisory..."):
            res = pipeline.process_voice(str(temp_audio_file), forced_language=selected_lang)
            st.session_state["last_result"] = res

    # Process Text Input
    elif text_query_btn and user_text.strip():
        with st.spinner("🌾 Retrieving verified agricultural advisory..."):
            res = pipeline.process_text(user_text.strip(), forced_language=selected_lang)
            st.session_state["last_result"] = res

    # Display Results
    if "last_result" in st.session_state:
        res = st.session_state["last_result"]
        st.markdown("---")
        st.subheader("📢 Assistant Response & Advisory")

        # Status & Decision Badges
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        with col_b1:
            decision = res["decision"]
            if decision == "answer":
                st.markdown('<span class="badge-verified">✅ Answer Grounded & Verified</span>', unsafe_allow_html=True)
            elif decision == "warn_safety":
                st.markdown('<span class="badge-safety">⚠️ Strict Safety Warning</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-refusal">🛡️ Safe Refusal / Expert Referral</span>', unsafe_allow_html=True)
        with col_b2:
            st.markdown(f"**Intent:** `{res['intent']}`")
        with col_b3:
            st.markdown(f"**Confidence:** `{int(res['overall_confidence']*100)}%`")
        with col_b4:
            st.markdown(f"**Source:** `{res['source_name']}`")

        # Spoken Audio Response Player
        if res.get("audio_path") and Path(res["audio_path"]).exists():
            st.markdown("##### 🔊 Spoken Response (Play Audio):")
            st.audio(res["audio_path"])

        # Display Answer Text
        st.markdown("##### 📝 Advisory Text:")
        if res["decision"] == "warn_safety":
            st.error(res["answer_text"])
        elif res["decision"] in ["refuse", "ask_clarification"]:
            st.warning(res["answer_text"])
        else:
            st.success(res["answer_text"])

        # Display Evidence Passages
        if res.get("evidence_passages"):
            with st.expander("🔍 View Retrieved Knowledge Evidence (Passages from Knowledge Base)"):
                for idx, passage in enumerate(res["evidence_passages"], 1):
                    st.markdown(f"**Passage {idx}:** {passage}")

        st.caption(f"⚡ Processing Latency: {res.get('latency_sec', 0.1)} seconds")

# ----------------- TAB 2: Live Tools -----------------
with tab_live_tools:
    st.subheader("📈 Live Agricultural Market Prices (Agmarknet / e-NAM)")
    c_tool1, c_tool2 = st.columns(2)
    with c_tool1:
        comm_input = st.selectbox("Commodity / शेतमाल:", ["कापूस (Cotton)", "सोयाबीन (Soybean)", "गहू (Wheat)", "टोमॅटो (Tomato)", "कांदा (Onion)", "हरभरा (Gram)"])
        comm_key = comm_input.split()[0]
    with c_tool2:
        mkt_input = st.selectbox("Mandi / बाजार समिती:", ["Nagpur", "Akola", "Pune", "Nashik", "Lasalgaon", "Indore", "Karnal", "Rajkot"])

    if st.button("📊 Fetch Mandi Rates"):
        p_res = pipeline.mandi_tool.get_prices(commodity_query=comm_key, market_query=mkt_input, lang="mr")
        st.info(p_res.get("formatted_response", ""))
        st.json(p_res)

    st.markdown("---")
    st.subheader("🌦️ District Agromet Weather & Spraying Advisory")
    dist_input = st.selectbox("Select District:", ["Nagpur", "Pune", "Nashik", "Indore"])
    if st.button("🌤️ Check Weather Advisory"):
        w_res = pipeline.weather_tool.get_advisory(location_query=dist_input, lang="mr")
        st.success(w_res.get("formatted_response", ""))
        st.json(w_res)

# ----------------- TAB 3: Verified Knowledge Base -----------------
with tab_knowledge:
    st.subheader("📚 Verified Agricultural Knowledge Repository")
    st.caption("Ingested from ICAR institutes, State Agricultural Universities (SAUs), KVKs, and MoA&FW schemes.")

    raw_docs = DocumentIngestionPipeline(config.RAW_DOCS_DIR).load_raw_documents()
    doc_table = []
    for d in raw_docs:
        doc_table.append({
            "Doc ID": d.get("doc_id"),
            "Crop": d.get("crop", "").upper(),
            "Topic": d.get("topic"),
            "Source": d.get("source"),
            "Season": d.get("season"),
            "Verified": "✅ Yes" if d.get("verified_status") else "❌ No",
            "Updated": d.get("last_updated")
        })

    st.dataframe(doc_table, use_container_width=True)

# ----------------- TAB 4: Model Benchmarks -----------------
with tab_benchmarks:
    st.subheader("🧪 Quantitative Model Benchmarking Report")
    st.caption("Evaluated on 25 benchmark scenarios including answerable queries, ambiguous questions, safe refusals, and hazardous chemical queries.")

    if st.button("🔄 Re-run Benchmark Suite"):
        with st.spinner("Running automated benchmark evaluation..."):
            runner = AgriculturalBenchmarkRunner()
            benchmark_data = runner.run_benchmark()
            with open(config.BASE_DIR / "benchmark_report.json", "w", encoding="utf-8") as f:
                json.dump(benchmark_data, f, ensure_ascii=False, indent=2)
            st.success("Benchmark completed successfully!")

    # Display Latest Metrics
    report_file = config.BASE_DIR / "benchmark_report.json"
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as f:
            report = json.load(f)

        m = report["metrics"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Intent Accuracy", f"{m['intent_classification_accuracy']}%", "Blueprint Target: >= 85%")
        c2.metric("Retrieval Recall@1", f"{m['retrieval_recall_at_top1']}%", "Blueprint Target: >= 85%")
        c3.metric("Safe Refusal Accuracy", f"{m['safe_refusal_accuracy']}%", "Blueprint Target: >= 90%")
        c4.metric("Faithfulness Grounding", f"{m['faithfulness_grounding_rate']}%", "Blueprint Target: >= 90%")

        st.caption(f"⚡ Average Processing Latency: **{m['average_latency_sec']} seconds** (Blueprint Target: < 15.0s)")

        with st.expander("📋 View Detailed Benchmark Evaluation Table"):
            st.dataframe(report["detailed_results"], use_container_width=True)
