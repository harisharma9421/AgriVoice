import re
import pickle
from pathlib import Path
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from src.knowledge.vector_store import tokenize_indic
from src.language.glossary import AgriculturalGlossary
import config

TRAINING_DATA = [
    # Mandi price intent
    ("कापसाचा आजचा बाजारभाव काय आहे", "mandi_price"),
    ("नागपूर मंडी मध्ये सोयाबीनचा भाव सांगा", "mandi_price"),
    ("कांद्याचा काय भाव चालू आहे लासलगाव मध्ये", "mandi_price"),
    ("गेहूं का ताजा मंडी भाव क्या है", "mandi_price"),
    ("इंदौर मंडी में सोयाबीन का रेट बताओ", "mandi_price"),
    ("टमाटर का थोक भाव कितना चल रहा है", "mandi_price"),
    ("cotton price in rajkot market", "mandi_price"),
    ("today soybean mandi rate", "mandi_price"),

    # Weather advisory intent
    ("आज पाऊस पडेल का हवामानाचा अंदाज काय आहे", "weather_advisory"),
    ("नागपूरचे हवामान कसे राहील फवारणी करावी का", "weather_advisory"),
    ("पुण्यात आज पाऊस येईल का", "weather_advisory"),
    ("आज मौसम कैसा रहेगा क्या बारिश होगी", "weather_advisory"),
    ("क्या आज कीटनाशक का छिड़काव कर सकते हैं मौसम बताओ", "weather_advisory"),
    ("will it rain today in nagpur weather forecast", "weather_advisory"),
    ("is weather suitable for spraying today", "weather_advisory"),

    # Government scheme intent
    ("पीएम किसान योजनेचा पुढचा हप्ता कधी जमा होणार", "government_scheme"),
    ("पीक विमा योजनेसाठी अर्ज कसा करावा आणि नियम काय", "government_scheme"),
    ("पंतप्रधान किसान सन्मान निधीची पात्रता काय आहे", "government_scheme"),
    ("प्रधानमंत्री फसल बीमा योजना में क्लेम कैसे करें", "government_scheme"),
    ("पीएम किसान में eKYC कैसे करें और 6000 रुपये कब मिलेंगे", "government_scheme"),
    ("मृदा स्वास्थ्य कार्ड कैसे बनवाएं", "government_scheme"),
    ("how to apply for pm kisan scheme eligibility", "government_scheme"),
    ("crop insurance claim 72 hours deadline rules", "government_scheme"),

    # Pest and disease intent
    ("कापसावर गुलाबी बोंडअळी आली आहे काय फवारावे", "pest_disease"),
    ("पानांवर मावा आणि तुडतुडे झाले आहेत कोणती औषध मारावी", "pest_disease"),
    ("टोमॅटोवर करपा रोग आला आहे फळे काळी पडत आहेत", "pest_disease"),
    ("सोयाबीनमध्ये खोडमाशी आणि गर्डल बीटल नियंत्रण उपाय", "pest_disease"),
    ("गव्हावर पिवळा तांबेरा आला आहे काय फवारावे", "pest_disease"),
    ("कपास में पिंक बॉलवर्म और रस चूसक कीट का नियंत्रण", "pest_disease"),
    ("सोयाबीन में पीला मोज़ेक वायरस की रोकथाम कैसे करें", "pest_disease"),
    ("चने में उकठा और फली छेदक के लिए कौन सी दवा स्प्रे करें", "pest_disease"),
    ("how to control pink bollworm in cotton crop", "pest_disease"),
    ("fungicide spray for late blight in tomato", "pest_disease"),

    # Crop advice intent
    ("कपासाची पाने पिवळी पडत आहेत काय उपाय करावा", "crop_advice"),
    ("गव्हाला पहिले पाणी कधी द्यावे आणि युरिया किती टाकावा", "crop_advice"),
    ("सोयाबीन पिकाला खताची पहिली मात्रा कोणती द्यावी", "crop_advice"),
    ("उसात खत व्यवस्थापन आणि ठिबक सिंचन कसे करावे", "crop_advice"),
    ("कपास में पत्तियां पीली पड़ रही हैं कौन सा खाद दें", "crop_advice"),
    ("गेहूं में कल्ले बढ़ाने के लिए क्या करें", "crop_advice"),
    ("fertigation schedule for sugarcane crop", "crop_advice"),
    ("critical irrigation stages for wheat crop", "crop_advice"),

    # Hazardous queries
    ("कीड़ा जल्दी मारने के लिए क्या 5 गुना कीटनाशक डाल दूं", "hazardous"),
    ("औषधाचे प्रमाण दुप्पट करून हाताने फवारले तर चालेल का", "hazardous"),
    ("without gloves can i spray strong pesticide directly", "hazardous"),

    # Ambiguous / Low information
    ("माझ्या झाडाला काहीतरी झाले आहे सांगा काय करू", "ambiguous"),
    ("फसल में बीमारी लग गई है तुरंत दवा बताओ", "ambiguous"),
    ("पेड़ सूख रहा है क्या डालूं", "ambiguous"),

    # Out of scope
    ("who won the cricket world cup yesterday", "out_of_scope"),
    ("शेअर बाजारात कुठे पैसे गुंतवावे", "out_of_scope"),
    ("write a python script for web scraping", "out_of_scope"),
    ("मुझे एक अच्छा गाना सुनाओ", "out_of_scope")
]

class AgriculturalIntentClassifier:
    def __init__(self, model_path: Path = config.SAVED_MODELS_DIR / "intent_classifier.pkl"):
        self.model_path = Path(model_path)
        self.vectorizer = None
        self.model = None
        self.glossary = AgriculturalGlossary()
        self.load_or_train()

    def train(self):
        texts, labels = zip(*TRAINING_DATA)
        self.vectorizer = TfidfVectorizer(tokenizer=tokenize_indic, token_pattern=None, ngram_range=(1, 2), sublinear_tf=True)
        X = self.vectorizer.fit_transform(texts)
        self.model = LogisticRegression(max_iter=500, C=3.0)
        self.model.fit(X, labels)
        self.save()
        print("Agricultural Intent Classifier trained successfully on domain dataset.")

    def save(self):
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump({"model": self.model, "vectorizer": self.vectorizer}, f)

    def load_or_train(self):
        if self.model_path.exists():
            try:
                with open(self.model_path, "rb") as f:
                    data = pickle.load(f)
                self.model = data["model"]
                self.vectorizer = data["vectorizer"]
                return
            except Exception:
                pass
        self.train()

    def detect_language(self, text: str) -> str:
        """Detect language (mr, hi, en) using script analysis and distinct marker words."""
        # Devanagari script range: \u0900-\u097F
        devanagari_chars = len(re.findall(r"[\u0900-\u097F]", text))
        latin_chars = len(re.findall(r"[a-zA-Z]", text))

        if latin_chars > devanagari_chars:
            return "en"

        text_lower = text.lower()
        # Distinct Marathi markers
        mr_markers = ["आहेत", "करावे", "पिकात", "काय", "कधी", "आली", "झाले", "पडत", "फवारावे", 
                      "टाकावे", "बाजारभाव", "हवामान", "पाऊस", "सांगा", "माझ्या", "शेतकरी", "कसे", "कोणती"]
        # Distinct Hindi markers
        hi_markers = ["हैं", "करें", "फसल", "क्या", "कब", "आया", "गया", "पड़", "छिड़काव", 
                      "डालें", "भाव", "मौसम", "बारिश", "बताओ", "मेरे", "किसान", "कैसे", "कौनसा"]

        mr_score = sum(1 for m in mr_markers if m in text_lower)
        hi_score = sum(1 for m in hi_markers if m in text_lower)

        if mr_score > hi_score:
            return "mr"
        elif hi_score > mr_score:
            return "hi"
        return "hi" # default Indic

    def classify(self, text: str) -> Dict[str, Any]:
        """Classify query into intent, detect language, extract entities, and compute confidence."""
        language = self.detect_language(text)
        entities = self.glossary.extract_entities(text)
        t_low = text.lower()

        # 1. Hazardous check (strict safety priority)
        if any(h in t_low for h in ["5 गुना", "दुप्पट", "बिना दस्ताने", "हाताने फवार", "double dose", "overdose"]):
            return {
                "intent": "hazardous",
                "confidence": 0.95,
                "language": language,
                "entities": entities,
                "normalized_query": text
            }

        # 2. Check for non-agricultural out-of-scope entities (financial markets, sports, entertainment)
        out_of_scope_cues = ["सोने", "चांदी", "शेअर बाजार", "म्युच्युअल फंड", "क्रिकेट", "गाना", "film", "movie", "gold", "silver", "stock", "crypto", "cricket", "song"]
        if any(c in t_low for c in out_of_scope_cues):
            return {
                "intent": "out_of_scope",
                "confidence": 0.95,
                "language": language,
                "entities": entities,
                "normalized_query": text
            }

        if self.model and self.vectorizer:
            X = self.vectorizer.transform([text])
            probs = self.model.predict_proba(X)[0]
            best_idx = probs.argmax()
            pred_intent = self.model.classes_[best_idx]
            confidence = float(probs[best_idx])
        else:
            pred_intent = "crop_advice"
            confidence = 0.60

        # Heuristic overrides for high-confidence keyword signals
        if any(w in t_low for w in ["भाव", "दर", "बाजारभाव", "मंडी रेट", "price", "rate"]):
            pred_intent = "mandi_price"
            confidence = max(confidence, 0.88)
        elif any(w in t_low for w in ["हवामान", "मौसम", "पाऊस", "बारिश", "weather", "rain"]):
            pred_intent = "weather_advisory"
            confidence = max(confidence, 0.88)
        elif any(w in t_low for w in ["योजना", "पीएम किसान", "विमा", "सब्सिडी", "scheme", "insurance"]):
            pred_intent = "government_scheme"
            confidence = max(confidence, 0.88)

        # Ambiguous check: If user asks generic question without mentioning any crop or topic
        if not entities.get("crop") and not entities.get("scheme") and pred_intent in ["pest_disease", "crop_advice"]:
            if any(w in t_low for w in ["झाडाला काहीतरी", "फसल में बहुत", "पेड़ सूख", "काहीतरी झाले"]):
                pred_intent = "ambiguous"
                confidence = 0.85

        return {
            "intent": pred_intent,
            "confidence": round(confidence, 4),
            "language": language,
            "entities": entities,
            "normalized_query": text
        }
