from typing import Dict, Any
from src.language.glossary import AgriculturalGlossary

class DomainTranslator:
    def __init__(self):
        self.glossary = AgriculturalGlossary()

    def translate_query(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate query or preserve canonical terms for retrieval."""
        if source_lang == target_lang:
            return text

        # Preserve canonical agricultural terms
        entities = self.glossary.extract_entities(text)
        translated_text = text
        # If translating to English for dense retrieval:
        if target_lang == "en":
            if entities["crop"]:
                translated_text = f"{entities['crop']} {translated_text}"
            if entities["pest_disease"]:
                translated_text = f"{entities['pest_disease']} {translated_text}"

        return translated_text
