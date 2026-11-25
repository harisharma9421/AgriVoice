import json
from pathlib import Path
from typing import Dict, Any, Optional
import config

class MandiPriceTool:
    def __init__(self, cache_file: Path = config.DATA_DIR / "mandi_cache.json"):
        self.cache_file = Path(cache_file)
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if self.cache_file.exists():
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"as_of_date": "24 Nov 2026", "commodities": {}}

    def normalize_commodity(self, query: str) -> Optional[str]:
        q = query.lower()
        mapping = {
            "cotton": ["कापूस", "कापसा", "कापस", "कपास", "कपासी", "रुई", "cotton"],
            "soybean": ["सोयाबीन", "सोयाबिन", "सोया", "soybean", "soya"],
            "wheat": ["गहू", "गव्हा", "गव्हाचे", "गेहूं", "गेहु", "wheat"],
            "tomato": ["टोमॅटो", "टोमॅटोचे", "टमाटर", "tomato"],
            "gram": ["हरभरा", "हरभऱ्या", "हरभऱ्याचे", "चना", "चने", "gram", "chana"],
            "onion": ["कांदा", "कांद्या", "कांद्य", "कांद्याचे", "प्याज", "onion"]
        }
        for commodity, aliases in mapping.items():
            for alias in aliases:
                if alias in q:
                    return commodity
        return None

    def get_prices(self, commodity_query: str, market_query: Optional[str] = None, lang: str = "mr") -> Dict[str, Any]:
        commodity = self.normalize_commodity(commodity_query)
        as_of_date = self.data.get("as_of_date", "24 Nov 2026")

        if not commodity or commodity not in self.data.get("commodities", {}):
            return {
                "success": False,
                "as_of_date": as_of_date,
                "message": f"कोणत्या पिकाचा/शेतमालाचा बाजारभाव हवा आहे ते कृपया स्पष्ट सांगा (उदा. कापूस, सोयाबीन, गहू, कांदा)."
            }

        comm_data = self.data["commodities"][commodity]
        mandis = comm_data["mandis"]

        # Market mapping for Marathi, Hindi, and English
        market_aliases = {
            "nagpur": "nagpur", "नागपूर": "nagpur", "नागपुर": "nagpur",
            "akola": "akola", "अकोला": "akola",
            "rajkot": "rajkot", "राजकोट": "rajkot",
            "indore": "indore", "इंदूर": "indore", "इंदौर": "indore",
            "lasalgaon": "lasalgaon", "लासलगाव": "lasalgaon", "लासलगांव": "lasalgaon",
            "pune": "pune", "पुणे": "pune",
            "nashik": "nashik", "नाशिक": "nashik", "नासिक": "nashik",
            "karnal": "karnal", "कर्नाल": "karnal"
        }

        matched_mandi = None
        if market_query:
            m_q = market_query.lower()
            detected_mkt_key = None
            for alias, norm_key in market_aliases.items():
                if alias in m_q:
                    detected_mkt_key = norm_key
                    break

            if detected_mkt_key:
                for m in mandis:
                    if detected_mkt_key in m["market"].lower():
                        matched_mandi = m
                        break

        if not matched_mandi:
            matched_mandi = mandis[0]  # default to primary regional benchmark mandi

        # Format spoken and text messages based on language
        comm_name = comm_data.get(f"name_{lang}", comm_data["name_en"])
        market_name = matched_mandi["market"]
        modal = matched_mandi["modal_price"]
        min_p = matched_mandi["min_price"]
        max_p = matched_mandi["max_price"]

        if lang == "mr":
            formatted_text = (
                f"दिनांक {as_of_date} नुसार {market_name} बाजार समितीत {comm_name}चा सरासरी दर "
                f"₹{modal} प्रति क्विंटल आहे (किमान ₹{min_p}, कमाल ₹{max_p}). स्रोत: Agmarknet/e-NAM."
            )
        elif lang == "hi":
            formatted_text = (
                f"दिनांक {as_of_date} के अनुसार {market_name} मंडी में {comm_name} का औसत भाव "
                f"₹{modal} प्रति क्विंटल है (न्यूनतम ₹{min_p}, अधिकतम ₹{max_p})। स्रोत: Agmarknet/e-NAM।"
            )
        else:
            formatted_text = (
                f"As of {as_of_date}, the modal price for {comm_name} in {market_name} is "
                f"Rs {modal} per quintal (Range: Rs {min_p} - Rs {max_p}). Source: Agmarknet/e-NAM."
            )

        return {
            "success": True,
            "commodity": commodity,
            "market": market_name,
            "modal_price": modal,
            "min_price": min_p,
            "max_price": max_p,
            "unit": comm_data.get("unit", "Rs / Quintal"),
            "arrivals_tonnes": matched_mandi.get("arrivals_tonnes", 0),
            "as_of_date": as_of_date,
            "source": "Agmarknet / e-NAM Live Portal",
            "formatted_response": formatted_text
        }
