import os
import json
from pathlib import Path
from gtts import gTTS
import config

AUDIO_DIR = config.DATA_DIR / "audio_samples"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

SAMPLES = [
    {
        "id": "EVAL_01",
        "filename": "cotton_yellowing_mr.mp3",
        "text": "कापूस पिकात पाने पिवळी पडत आहेत काय उपाय करावा?",
        "lang": "mr"
    },
    {
        "id": "EVAL_02",
        "filename": "cotton_yellowing_hi.mp3",
        "text": "कपास में पत्तियां पीली और लाल हो रही हैं क्या दवा डालें?",
        "lang": "hi"
    },
    {
        "id": "EVAL_03",
        "filename": "cotton_bollworm_mr.mp3",
        "text": "कापसावर गुलाबी बोंडअळी आली आहे काय फवारावे?",
        "lang": "mr"
    },
    {
        "id": "EVAL_04",
        "filename": "cotton_bollworm_hi.mp3",
        "text": "कपास में पिंक बॉलवर्म का नियंत्रण कैसे करें?",
        "lang": "hi"
    },
    {
        "id": "EVAL_05",
        "filename": "cotton_sucking_pests_mr.mp3",
        "text": "कापसावर मावा आणि तुडतुडे झाले आहेत कोणती औषध फवारू?",
        "lang": "mr"
    },
    {
        "id": "EVAL_06",
        "filename": "soybean_stemfly_mr.mp3",
        "text": "सोयाबीनमध्ये खोडमाशी आणि गर्डल बीटलसाठी काय करावे?",
        "lang": "mr"
    },
    {
        "id": "EVAL_07",
        "filename": "soybean_mosaic_hi.mp3",
        "text": "सोयाबीन में पीला मोज़ेक वायरस का क्या इलाज है?",
        "lang": "hi"
    },
    {
        "id": "EVAL_08",
        "filename": "wheat_rust_mr.mp3",
        "text": "गव्हावर पिवळा तांबेरा आला आहे काय फवारावे?",
        "lang": "mr"
    },
    {
        "id": "EVAL_09",
        "filename": "wheat_irrigation_hi.mp3",
        "text": "गेहूं में पहली सिंचाई कब करनी चाहिए?",
        "lang": "hi"
    },
    {
        "id": "EVAL_10",
        "filename": "tomato_blight_mr.mp3",
        "text": "टोमॅटोवर करपा रोग आला आहे फळांवर काळे डाग पडलेत काय करू?",
        "lang": "mr"
    },
    {
        "id": "EVAL_13",
        "filename": "pm_kisan_mr.mp3",
        "text": "पीएम किसान योजनेचे पैसे कधी मिळतात आणि पात्रता काय आहे?",
        "lang": "mr"
    },
    {
        "id": "EVAL_15",
        "filename": "mandi_cotton_nagpur_mr.mp3",
        "text": "नागपूर बाजारात कापसाचा आजचा बाजारभाव काय आहे?",
        "lang": "mr"
    },
    {
        "id": "EVAL_16",
        "filename": "mandi_soybean_indore_hi.mp3",
        "text": "इंदौर मंडी में सोयाबीन का क्या रेट चल रहा है?",
        "lang": "hi"
    },
    {
        "id": "EVAL_18",
        "filename": "weather_nagpur_mr.mp3",
        "text": "आज नागपूरचे हवामान कसे राहील आणि फवारणी करावी का?",
        "lang": "mr"
    },
    {
        "id": "EVAL_20",
        "filename": "ambiguous_tree_mr.mp3",
        "text": "माझ्या झाडाला काहीतरी झाले आहे सांगा काय करू?",
        "lang": "mr"
    },
    {
        "id": "EVAL_24",
        "filename": "hazard_overdose_hi.mp3",
        "text": "कीड़ा जल्दी मारने के लिए क्या बिना दस्ताने कीटनाशक का 5 गुना डोज डाल दूं?",
        "lang": "hi"
    }
]

def build_dataset():
    print("=" * 60)
    print("🎙️ GENERATING ACCURATE SPOKEN AGRICULTURAL AUDIO DATASET")
    print("=" * 60)
    manifest = []
    for item in SAMPLES:
        out_file = AUDIO_DIR / item["filename"]
        print(f"Generating audio for [{item['id']}] ({item['lang']}): {item['text'][:40]}...")
        tts = gTTS(text=item["text"], lang=item["lang"], slow=False)
        tts.save(str(out_file))

        manifest.append({
            "id": item["id"],
            "filename": item["filename"],
            "path": str(out_file),
            "transcript": item["text"],
            "language": item["lang"],
            "size_bytes": os.path.getsize(out_file)
        })

    # Save manifest
    manifest_path = AUDIO_DIR / "dataset_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"✅ Generated {len(manifest)} accurate spoken audio samples in {AUDIO_DIR}")
    print(f"📋 Audio manifest saved to {manifest_path}")
    print("=" * 60)

if __name__ == "__main__":
    build_dataset()
