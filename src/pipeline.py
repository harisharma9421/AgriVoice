import time
from pathlib import Path
from typing import Dict, Any, Optional

from src.audio.asr import SpeechRecognizer
from src.audio.tts import TextToSpeechSynthesizer
from src.language.intent_classifier import AgriculturalIntentClassifier
from src.knowledge.vector_store import HybridVectorStore
from src.tools.mandi_tool import MandiPriceTool
from src.tools.weather_tool import WeatherAdvisoryTool
from src.generation.generator import GroundedAnswerGenerator
from src.generation.confidence_gate import ConfidenceGate
from src.generation.safety import AgriculturalSafetyEnforcer
import config

class AgriVoiceAssistantPipeline:
    def __init__(self):
        print("Initializing Agri Voice Assistant Pipeline...")
        self.asr = SpeechRecognizer()
        self.tts = TextToSpeechSynthesizer()
        self.intent_classifier = AgriculturalIntentClassifier()
        self.vector_store = HybridVectorStore()
        self.vector_store.load_index()
        self.mandi_tool = MandiPriceTool()
        self.weather_tool = WeatherAdvisoryTool()
        self.generator = GroundedAnswerGenerator()
        self.confidence_gate = ConfidenceGate()
        self.safety = AgriculturalSafetyEnforcer()
        print("Agri Voice Assistant Pipeline initialized successfully.")

    def process_voice(self, audio_path: str, forced_language: Optional[str] = None) -> Dict[str, Any]:
        """End-to-end voice processing: Voice -> ASR -> Pipeline -> TTS Audio Output."""
        start_time = time.time()
        # 1. Speech-to-Text
        asr_res = self.asr.transcribe(audio_path, forced_language=forced_language)
        if not asr_res.get("success", False):
            lang = forced_language or "hi"
            refusal = self.confidence_gate.get_refusal_message(lang, "low_asr")
            audio_out = self.tts.synthesize(refusal, lang=lang)
            return {
                "success": False,
                "transcript": "",
                "answer_text": refusal,
                "audio_response_path": audio_out,
                "latency_sec": round(time.time() - start_time, 2)
            }

        transcript = asr_res["transcript"]
        asr_conf = asr_res.get("confidence", 0.85)
        detected_lang = forced_language or asr_res.get("language", "hi")

        # 2. Process query text
        res = self.process_text(transcript, asr_confidence=asr_conf, forced_language=detected_lang)
        res["asr_confidence"] = asr_conf
        res["audio_duration_in"] = asr_res.get("duration_sec", 0.0)
        res["latency_sec"] = round(time.time() - start_time, 2)
        return res

    def process_text(self,
                     query: str,
                     asr_confidence: float = 1.0,
                     forced_language: Optional[str] = None) -> Dict[str, Any]:
        """Process text question through intent routing, tools/retrieval, confidence gating, generation, and TTS."""
        start_time = time.time()

        # 1. Language & Intent Classification + Entity Extraction
        intent_info = self.intent_classifier.classify(query)
        lang = forced_language or intent_info.get("language", "mr")
        intent = intent_info.get("intent", "crop_advice")
        entities = intent_info.get("entities", {})

        retrieved_results = []
        retrieval_conf = 0.0
        final_answer = ""
        source_name = "N/A"
        doc_id = None

        # 2. Routing based on Intent
        if intent == "mandi_price":
            tool_res = self.mandi_tool.get_prices(
                commodity_query=query,
                market_query=query,
                lang=lang
            )
            final_answer = tool_res.get("formatted_response", "")
            source_name = tool_res.get("source", "Agmarknet/e-NAM")
            gate_decision = {
                "decision": "answer",
                "reason_code": "MANDI_TOOL_DISPATCH",
                "overall_confidence": 0.92
            }

        elif intent == "weather_advisory":
            tool_res = self.weather_tool.get_advisory(location_query=query, lang=lang)
            final_answer = tool_res.get("formatted_response", "")
            source_name = tool_res.get("source", "IMD Agromet")
            gate_decision = {
                "decision": "answer",
                "reason_code": "WEATHER_TOOL_DISPATCH",
                "overall_confidence": 0.94
            }

        elif intent == "hazardous":
            # Safety intercept
            if lang == "mr":
                final_answer = (
                    "धोकादायक सूचना: कीटकनाशकाचा दुप्पट किंवा अधिक डोस वापरणे पिकासाठी आणि जमिनीसाठी अत्यंत घातक आहे! "
                    "नेहमी CIB&RC प्रमाणित प्रमाणातच औषध वापरावे आणि हातमोजे, मास्क वापरणे बंधनकारक आहे. "
                    f"तातडीच्या मार्गदर्शनासाठी किसान कॉल सेंटरशी ({config.KISAN_CALL_CENTRE}) संपर्क साधा."
                )
            else:
                final_answer = (
                    "चेतावनी: कीटनाशक की अधिक खुराक डालना फसल और भूमि के लिए अत्यंत हानिकारक है! "
                    "हमेशा CIB&RC द्वारा निर्धारित सुरक्षित मात्रा का ही प्रयोग करें और दस्ताने व मास्क अवश्य पहनें। "
                    f"सहायता हेतु किसान कॉल सेंटर ({config.KISAN_CALL_CENTRE}) पर संपर्क करें।"
                )
            gate_decision = {
                "decision": "warn_safety",
                "reason_code": "HAZARDOUS_QUERY_INTERCEPTED",
                "overall_confidence": 0.98
            }

        elif intent in ["out_of_scope", "ambiguous"]:
            gate_decision = self.confidence_gate.evaluate(
                asr_confidence=asr_confidence,
                retrieval_confidence=0.0,
                intent_data=intent_info,
                retrieved_count=0
            )
            final_answer = gate_decision["refusal_message"]

        else:
            # Crop advice, pest/disease, government schemes -> Hybrid RAG Retrieval
            crop_filter = entities.get("crop")
            retrieved_results = self.vector_store.search(query, crop_filter=crop_filter, top_k=config.TOP_K_RETRIEVAL)
            if retrieved_results:
                retrieval_conf = retrieved_results[0]["relevance_confidence"]

            gate_decision = self.confidence_gate.evaluate(
                asr_confidence=asr_confidence,
                retrieval_confidence=retrieval_conf,
                intent_data=intent_info,
                retrieved_count=len(retrieved_results)
            )

            if gate_decision["decision"] == "answer":
                gen_res = self.generator.generate(
                    query=query,
                    retrieved_results=retrieved_results,
                    intent_data=intent_info,
                    lang=lang
                )
                final_answer = gen_res["grounded_text"]
                source_name = gen_res["source"]
                doc_id = gen_res.get("doc_id")
            else:
                final_answer = gate_decision["refusal_message"]

        # 3. Speech Synthesis (TTS) - produce natural audio reply
        audio_filename = f"reply_{int(time.time()*1000)}.mp3"
        audio_path = self.tts.synthesize(final_answer, lang=lang, filename=audio_filename)

        return {
            "query": query,
            "language": lang,
            "intent": intent,
            "entities": entities,
            "decision": gate_decision["decision"],
            "reason_code": gate_decision["reason_code"],
            "overall_confidence": gate_decision["overall_confidence"],
            "retrieval_confidence": retrieval_conf,
            "answer_text": final_answer,
            "source_name": source_name,
            "doc_id": doc_id,
            "audio_path": audio_path,
            "evidence_passages": [r["chunk"]["text"] for r in retrieved_results[:2]],
            "latency_sec": round(time.time() - start_time, 2)
        }
