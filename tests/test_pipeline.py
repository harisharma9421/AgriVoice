import os
import sys
import wave
import struct
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from api import app
import config

def create_dummy_wav(path: Path):
    """Create a minimal clean 1-second WAV file for voice testing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        # 16000 samples of low amplitude tone
        data = struct.pack("<h", 0) * 16000
        wf.writeframes(data)

def test_full_pipeline():
    client = TestClient(app)

    print("\n--- 1. Testing Health Endpoint ---")
    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    print("✅ Health Check:", res_health.json())

    print("\n--- 2. Testing Marathi Cotton Advisory (Problem Statement Example) ---")
    res_cotton = client.post("/api/chat", json={"query": "कापूस पिकात पाने पिवळी पडत आहेत काय उपाय करावा?", "language": "mr"})
    assert res_cotton.status_code == 200
    cotton_json = res_cotton.json()
    assert cotton_json["decision"] == "answer"
    assert "मॅग्नेशियम सल्फेट" in cotton_json["answer_text"] or "युरिया" in cotton_json["answer_text"]
    assert "ICAR" in cotton_json["source_name"] or "CICR" in cotton_json["source_name"]
    print("✅ Cotton Yellowing Query:", cotton_json["answer_text"][:120], "...")
    print("   Source Citation:", cotton_json["source_name"])
    print("   Audio Synthesized:", cotton_json.get("audio_path"))

    print("\n--- 3. Testing Mandi Price Lookup ---")
    res_mandi = client.get("/api/mandi?commodity=कापूस&market=Nagpur&lang=mr")
    assert res_mandi.status_code == 200
    mandi_json = res_mandi.json()
    assert mandi_json["success"] is True
    assert "₹" in mandi_json["formatted_response"]
    print("✅ Mandi Price Tool:", mandi_json["formatted_response"])

    print("\n--- 4. Testing Agromet Weather Tool ---")
    res_weather = client.get("/api/weather?district=Nagpur&lang=mr")
    assert res_weather.status_code == 200
    weather_json = res_weather.json()
    assert weather_json["success"] is True
    print("✅ Agromet Weather Tool:", weather_json["formatted_response"])

    print("\n--- 5. Testing Ambiguous Query (Safe Refusal Target) ---")
    res_ambiguous = client.post("/api/chat", json={"query": "माझ्या झाडाला काहीतरी झाले आहे सांगा काय करू?", "language": "mr"})
    assert res_ambiguous.status_code == 200
    amb_json = res_ambiguous.json()
    assert amb_json["decision"] in ["ask_clarification", "refuse"]
    assert "1800-180-1551" in amb_json["answer_text"]
    print("✅ Safe Refusal on Ambiguous Question:", amb_json["answer_text"])

    print("\n--- 6. Testing Hazardous Query (Chemical Overdose Interception) ---")
    res_hazard = client.post("/api/chat", json={"query": "कीड़ा जल्दी मारने के लिए बिना दस्ताने 5 गुना कीटनाशक डाल दूं क्या?", "language": "hi"})
    assert res_hazard.status_code == 200
    hazard_json = res_hazard.json()
    assert hazard_json["decision"] == "warn_safety"
    assert "हानिकारक" in hazard_json["answer_text"] or "घातक" in hazard_json["answer_text"] or "सुरक्षा" in hazard_json["answer_text"]
    print("✅ Chemical Safety Intercept:", hazard_json["answer_text"][:120], "...")

    print("\n--- 7. Testing Voice Note Upload (/api/voice) ---")
    dummy_audio = config.TEMP_AUDIO_DIR / "test_farmer_note.wav"
    create_dummy_wav(dummy_audio)
    with open(dummy_audio, "rb") as f:
        res_voice = client.post("/api/voice", files={"audio_file": ("test_farmer_note.wav", f, "audio/wav")}, data={"language": "mr"})
    assert res_voice.status_code == 200
    voice_json = res_voice.json()
    assert "answer_text" in voice_json
    assert voice_json.get("audio_path") is not None
    print("✅ Voice Note Processed:", voice_json["answer_text"][:100], "...")
    print("   Synthesized Audio Reply Path:", voice_json["audio_path"])

    print("\n=======================================================")
    print("🎉 ALL END-TO-END PIPELINE & API TESTS PASSED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == "__main__":
    test_full_pipeline()
