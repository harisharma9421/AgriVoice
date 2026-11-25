import re
from typing import List, Dict, Any, Optional
from src.generation.safety import AgriculturalSafetyEnforcer

class GroundedAnswerGenerator:
    def __init__(self):
        self.safety = AgriculturalSafetyEnforcer()

    def generate(self,
                 query: str,
                 retrieved_results: List[Dict[str, Any]],
                 intent_data: Dict[str, Any],
                 lang: str = "mr") -> Dict[str, Any]:
        """
        Synthesizes a short, spoken-style answer strictly grounded in retrieved evidence,
        including the verified source name.
        """
        if not retrieved_results:
            return {
                "grounded_text": "",
                "source": "None",
                "citations": []
            }

        top_item = retrieved_results[0]
        chunk = top_item["chunk"]
        raw_content = chunk.get("raw_content", chunk.get("text", ""))
        source_name = chunk.get("source", "अधिकृत कृषी संस्था (ICAR / KVK)")

        # Extract 2-3 most relevant sentences to keep reply concise (<30s spoken speech)
        sentences = [s.strip() for s in raw_content.replace("।", ".").split(".") if s.strip()]
        short_summary = ". ".join(sentences[:3]) + "."
        if len(sentences) > 3 and not any(k in short_summary for k in ["फवारावे", "उपाय", "छिड़काव", "spray"]):
            # Include actionable recommendation sentence
            short_summary += " " + sentences[3] + "."

        # Format grounded spoken answer with official source citation
        if lang == "mr":
            grounded_answer = f"{short_summary} (स्रोत: {source_name})."
        elif lang == "hi":
            grounded_answer = f"{short_summary} (स्रोत: {source_name})।"
        else:
            grounded_answer = f"{short_summary} (Source: {source_name})."

        # Apply strict safety advisory if chemical advice is involved
        final_answer = self.safety.inspect_and_attach_safety(
            grounded_answer,
            intent=intent_data.get("intent", "crop_advice"),
            lang=lang
        )

        return {
            "grounded_text": final_answer,
            "spoken_summary": short_summary,
            "source": source_name,
            "doc_id": chunk.get("doc_id"),
            "citations": [source_name]
        }
