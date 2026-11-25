import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import config

class AgriculturalGlossary:
    def __init__(self, glossary_file: Path = config.GLOSSARY_DIR / "agri_glossary.json"):
        self.glossary_file = Path(glossary_file)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.glossary_file.exists():
            with open(self.glossary_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract agricultural entities (crop, pest/disease, symptom, scheme, chemical)."""
        t = text.lower()
        extracted = {
            "crop": None,
            "pest_disease": None,
            "symptom": None,
            "scheme": None,
            "chemical": None
        }

        # Check crops
        for item in self.data.get("crops", []):
            aliases = [item["en"]] + item.get("hi", []) + item.get("mr", [])
            for alias in aliases:
                if alias.lower() in t:
                    extracted["crop"] = item["canonical"]
                    break
            if extracted["crop"]:
                break

        # Check pests and diseases
        for item in self.data.get("pests_and_diseases", []):
            aliases = [item["en"]] + item.get("hi", []) + item.get("mr", [])
            for alias in aliases:
                if alias.lower() in t:
                    extracted["pest_disease"] = item["canonical"]
                    break
            if extracted["pest_disease"]:
                break

        # Check symptoms
        for item in self.data.get("symptoms", []):
            aliases = [item["en"]] + item.get("hi", []) + item.get("mr", [])
            for alias in aliases:
                if alias.lower() in t:
                    extracted["symptom"] = item["canonical"]
                    break
            if extracted["symptom"]:
                break

        # Check schemes
        for item in self.data.get("schemes", []):
            aliases = [item["en"]] + item.get("hi", []) + item.get("mr", [])
            for alias in aliases:
                if alias.lower() in t:
                    extracted["scheme"] = item["canonical"]
                    break
            if extracted["scheme"]:
                break

        # Check chemicals
        for item in self.data.get("inputs_and_chemicals", []):
            aliases = [item["en"]] + item.get("hi", []) + item.get("mr", [])
            for alias in aliases:
                if alias.lower() in t:
                    extracted["chemical"] = item["canonical"]
                    break
            if extracted["chemical"]:
                break

        return extracted
