from typing import Dict, Any

class AgriculturalSafetyEnforcer:
    @staticmethod
    def inspect_and_attach_safety(answer_text: str, intent: str, lang: str = "mr") -> str:
        """
        Enforce strict safety guidelines for chemical sprays and pesticides.
        Always attach protective equipment warning.
        """
        chemical_keywords = [
            "कीटकनाशक", "औषध", "फवारणी", "रासायनिक", "बुरशीनाशक", 
            "कीटनाशक", "दवा", "छिड़काव", "केमिकल", "स्प्रे", "फफूंदनाशक",
            "pesticide", "fungicide", "spray", "chemical"
        ]

        needs_safety_warning = (
            intent in ["pest_disease", "hazardous"] or
            any(w in answer_text.lower() for w in chemical_keywords)
        )

        if not needs_safety_warning:
            return answer_text

        # Append safety warning in appropriate language
        if lang == "mr":
            warning = (
                "\n\n⚠️ महत्वाचा सुरक्षा सल्ला: रासायनिक फवारणी करताना मास्क आणि हातमोजे नक्की वापरा. "
                "CIB&RC शिफारशीनुसार अचूक प्रमाणातच औषध वापरावे. माहिती केवळ मार्गदर्शनासाठी आहे."
            )
        elif lang == "hi":
            warning = (
                "\n\n⚠️ आवश्यक सुरक्षा सलाह: रासायनिक छिड़काव करते समय मास्क और दस्ताने अवश्य पहनें। "
                "CIB&RC द्वारा अनुमोदित सटीक मात्रा का ही प्रयोग करें। यह जानकारी केवल मार्गदर्शन हेतु है।"
            )
        else:
            warning = (
                "\n\n⚠️ Mandatory Safety Advisory: Wear protective gloves and face mask when spraying chemicals. "
                "Strictly adhere to CIB&RC approved dosages. Guidance is informational."
            )

        return answer_text + warning
