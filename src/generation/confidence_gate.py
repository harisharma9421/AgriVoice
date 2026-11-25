from typing import Dict, Any
import config

class ConfidenceGate:
    def __init__(self,
                 min_asr_conf: float = config.MIN_ASR_CONFIDENCE,
                 min_ret_conf: float = config.MIN_RETRIEVAL_SCORE,
                 overall_threshold: float = config.CONFIDENCE_THRESHOLD):
        self.min_asr_conf = min_asr_conf
        self.min_ret_conf = min_ret_conf
        self.overall_threshold = overall_threshold

    def evaluate(self,
                 asr_confidence: float,
                 retrieval_confidence: float,
                 intent_data: Dict[str, Any],
                 retrieved_count: int) -> Dict[str, Any]:
        """
        Combines multi-modal signals into an answer decision:
        - answer: Proceed with grounded answer
        - warn_safety: Hazardous/pesticide overdose attempt
        - ask_clarification: Ambiguous query missing key context (crop/pest)
        - refuse: Insufficient evidence or out of scope
        """
        intent = intent_data.get("intent", "crop_advice")
        intent_conf = intent_data.get("confidence", 0.5)

        # 1. Hazardous check
        if intent == "hazardous":
            return {
                "decision": "warn_safety",
                "reason_code": "HAZARDOUS_QUERY_DETECTED",
                "overall_confidence": 0.95,
                "refusal_message": None
            }

        # 2. Out of scope check
        if intent == "out_of_scope":
            return {
                "decision": "refuse",
                "reason_code": "OUT_OF_SCOPE",
                "overall_confidence": intent_conf,
                "refusal_message": self.get_refusal_message(intent_data.get("language", "hi"), "out_of_scope")
            }

        # 3. Ambiguous check
        if intent == "ambiguous":
            return {
                "decision": "ask_clarification",
                "reason_code": "AMBIGUOUS_QUERY_MISSING_CROP",
                "overall_confidence": intent_conf,
                "refusal_message": self.get_refusal_message(intent_data.get("language", "hi"), "ambiguous")
            }

        # For tool-based intents (mandi_price, weather_advisory), retrieval score is not applicable
        if intent in ["mandi_price", "weather_advisory"]:
            overall_conf = 0.50 * asr_confidence + 0.50 * intent_conf
            return {
                "decision": "answer",
                "reason_code": "TOOL_INVOCATION_APPROVED",
                "overall_confidence": round(overall_conf, 4),
                "refusal_message": None
            }

        # 4. Multi-signal confidence calculation for RAG
        overall_conf = (0.30 * asr_confidence) + (0.50 * retrieval_confidence) + (0.20 * intent_conf)

        if asr_confidence < self.min_asr_conf:
            return {
                "decision": "ask_to_repeat",
                "reason_code": "LOW_ASR_CONFIDENCE",
                "overall_confidence": round(overall_conf, 4),
                "refusal_message": self.get_refusal_message(intent_data.get("language", "hi"), "low_asr")
            }

        if retrieved_count == 0 or retrieval_confidence < self.min_ret_conf or overall_conf < self.overall_threshold:
            return {
                "decision": "refuse",
                "reason_code": "LOW_EVIDENCE_CONFIDENCE",
                "overall_confidence": round(overall_conf, 4),
                "refusal_message": self.get_refusal_message(intent_data.get("language", "hi"), "low_evidence")
            }

        return {
            "decision": "answer",
            "reason_code": "HIGH_CONFIDENCE_GROUNDED",
            "overall_confidence": round(overall_conf, 4),
            "refusal_message": None
        }

    def get_refusal_message(self, lang: str, reason: str) -> str:
        messages = {
            "mr": {
                "out_of_scope": "हा प्रश्न शेतीशी संबंधित नाही. मी फक्त पिके, खते, कीड नियंत्रण, बाजारभाव व सरकारी योजनांवर मदत करू शकतो.",
                "ambiguous": f"कृपया आपल्या पिकाचे नाव किंवा समस्या अधिक स्पष्टपणे सांगा. अधिक माहितीसाठी किसान कॉल सेंटरशी ({config.KISAN_CALL_CENTRE}) संपर्क साधा.",
                "low_asr": "माफ करा, आपला आवाज स्पष्ट ऐकू आला नाही. कृपया प्रश्न पुन्हा सांगा.",
                "low_evidence": f"माफ करा, या प्रश्नासाठी माझ्याकडे खात्रीशीर अधिकृत माहिती उपलब्ध नाही. कृपया जवळच्या कृषी विज्ञान केंद्राशी किंवा किसान कॉल सेंटरशी ({config.KISAN_CALL_CENTRE}) संपर्क साधा."
            },
            "hi": {
                "out_of_scope": "यह प्रश्न कृषि से संबंधित नहीं है। मैं केवल फसलों, कीटनाशक, मौसम, मंडी भाव और सरकारी योजनाओं पर जानकारी दे सकता हूँ।",
                "ambiguous": f"कृपया अपनी फसल का नाम या समस्या स्पष्ट रूप से बताएं। अधिक जानकारी के लिए किसान कॉल सेंटर ({config.KISAN_CALL_CENTRE}) से संपर्क करें।",
                "low_asr": "माफ कीजिए, आपकी आवाज स्पष्ट सुनाई नहीं दी। कृपया अपना प्रश्न दोबारा बोलें।",
                "low_evidence": f"माफ कीजिए, इस प्रश्न के लिए मेरे पास प्रमाणित जानकारी उपलब्ध नहीं है। कृपया नजदीकी कृषि विज्ञान केंद्र (KVK) या किसान कॉल सेंटर ({config.KISAN_CALL_CENTRE}) पर संपर्क करें।"
            },
            "en": {
                "out_of_scope": "This question is not related to agriculture. I can only assist with crop care, pests, mandi prices, weather, and government schemes.",
                "ambiguous": f"Please specify your crop name or symptom clearly. For assistance, contact Kisan Call Centre ({config.KISAN_CALL_CENTRE}).",
                "low_asr": "Sorry, audio was unclear. Please repeat your question.",
                "low_evidence": f"I do not have sufficient verified agricultural data to answer this safely. Please contact Kisan Call Centre at {config.KISAN_CALL_CENTRE} or your local KVK."
            }
        }
        lang_dict = messages.get(lang, messages["hi"])
        return lang_dict.get(reason, lang_dict["low_evidence"])
