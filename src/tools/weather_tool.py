from typing import Dict, Any, Optional

class WeatherAdvisoryTool:
    def __init__(self):
        # District level agromet advisory database based on IMD Agromet bulletins
        self.weather_data = {
            "nagpur": {
                "district": "Nagpur (Vidarbha)",
                "temp_c": 28,
                "condition": "Partly Cloudy",
                "humidity": "58%",
                "rain_prob": "10%",
                "wind_kmh": 12,
                "advisory_mr": "पुढील 3 दिवस हवामान कोरडे राहण्याचा अंदाज आहे. कीटकनाशक फवारणीसाठी सकाळची वेळ अनुकूल आहे.",
                "advisory_hi": "अगले 3 दिनों में मौसम साफ व शुष्क रहने का अनुमान है। कीटनाशक छिड़काव सुबह के समय किया जा सकता है।",
                "advisory_en": "Dry weather likely for next 3 days. Morning hours are favorable for pesticide and nutrient spraying."
            },
            "pune": {
                "district": "Pune (Western Maharashtra)",
                "temp_c": 26,
                "condition": "Clear Sky",
                "humidity": "52%",
                "rain_prob": "5%",
                "wind_kmh": 10,
                "advisory_mr": "हवामान स्वच्छ राहील. पिकांना हलके पाणी देण्यास व आंतरमशागतीस पोषक वातावरण आहे.",
                "advisory_hi": "मौसम साफ रहेगा। फसलों में हल्की सिंचाई व निराई-गुड़ाई के लिए अनुकूल मौसम है।",
                "advisory_en": "Clear weather conditions. Suitable for light irrigation and intercultural operations."
            },
            "nashik": {
                "district": "Nashik (North Maharashtra)",
                "temp_c": 24,
                "condition": "Morning Fog & Dew",
                "humidity": "72%",
                "rain_prob": "15%",
                "wind_kmh": 8,
                "advisory_mr": "सकाळी धुके व दव पडत असल्याने टोमॅटो व कांदा पिकात करपा रोगाचा धोका वाढू शकतो. प्रतिबंधात्मक बुरशीनाशक फवारावे.",
                "advisory_hi": "सुबह कोहरा व ओस के कारण टमाटर और प्याज में झुलसा/करपा का प्रकोप बढ़ सकता है। सावधानीपूर्वक फफूंदनाशक का छिड़काव करें।",
                "advisory_en": "High morning dew and fog may trigger fungal blight in tomato and onion. Apply preventive fungicide."
            },
            "indore": {
                "district": "Indore (Malwa)",
                "temp_c": 27,
                "condition": "Sunny",
                "humidity": "45%",
                "rain_prob": "0%",
                "wind_kmh": 14,
                "advisory_mr": "ऊन स्वच्छ पडेल, गहू पेरणी व पहिल्या पाण्याकरिता (CRI) योग्य वेळ आहे.",
                "advisory_hi": "धूप खिली रहेगी, गेहूं की बुवाई और पहली सिंचाई (CRI) के लिए अनुकूल समय है।",
                "advisory_en": "Sunny conditions, ideal for rabi wheat sowing and crown root initiation irrigation."
            }
        }

    def get_advisory(self, location_query: Optional[str] = None, lang: str = "mr") -> Dict[str, Any]:
        as_of_date = "24 Nov 2026"
        key = "nagpur" # default central hub
        if location_query:
            loc = location_query.lower()
            for k in self.weather_data.keys():
                if k in loc:
                    key = k
                    break

        item = self.weather_data[key]
        adv = item.get(f"advisory_{lang}", item["advisory_en"])

        if lang == "mr":
            formatted = (
                f"दिनांक {as_of_date} चे {item['district']} हवामान: तापमान {item['temp_c']}°C, "
                f"पावसाची शक्यता {item['rain_prob']} आणि आर्द्रता {item['humidity']}. "
                f"कृषी सल्ला: {adv} (स्रोत: IMD ॲग्रोमेट)."
            )
        elif lang == "hi":
            formatted = (
                f"दिनांक {as_of_date} को {item['district']} का मौसम: तापमान {item['temp_c']}°C, "
                f"बारिश की संभावना {item['rain_prob']} और नमी {item['humidity']}। "
                f"कृषि सलाह: {adv} (स्रोत: IMD एग्रोमेट)।"
            )
        else:
            formatted = (
                f"Weather as of {as_of_date} for {item['district']}: Temp {item['temp_c']}°C, "
                f"Rain probability {item['rain_prob']}, Humidity {item['humidity']}. "
                f"Agromet Advisory: {adv} (Source: IMD Agromet)."
            )

        return {
            "success": True,
            "district": item["district"],
            "temp_c": item["temp_c"],
            "rain_prob": item["rain_prob"],
            "humidity": item["humidity"],
            "wind_kmh": item["wind_kmh"],
            "as_of_date": as_of_date,
            "source": "IMD Agromet Advisory Service",
            "formatted_response": formatted
        }
