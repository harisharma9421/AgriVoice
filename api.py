import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
from src.pipeline import AgriVoiceAssistantPipeline
from src.evaluation.benchmark import AgriculturalBenchmarkRunner

app = FastAPI(
    title="Agri Voice Assistant API",
    description="Voice-first multilingual assistant API for Indian agriculture",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = AgriVoiceAssistantPipeline()

class TextQueryRequest(BaseModel):
    query: str
    language: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def root():
    """Serves the interactive voice assistant landing page UI."""
    template_path = config.BASE_DIR / "templates" / "index.html"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h2>Agri Voice Assistant is Running.</h2><p><a href='/docs'>View Swagger API Docs</a></p>")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Agri Voice Assistant",
        "supported_languages": list(config.SUPPORTED_LANGUAGES.keys()),
        "kisan_helpline": config.KISAN_CALL_CENTRE
    }

@app.post("/api/chat")
def process_chat(req: TextQueryRequest):
    """Process farmer text query with grounded retrieval, safety checks, and TTS."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    res = pipeline.process_text(req.query.strip(), forced_language=req.language)
    return res

@app.post("/api/voice")
async def process_voice(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    """Process incoming voice note (e.g. WhatsApp audio OGG/WAV/MP3)."""
    temp_path = config.TEMP_AUDIO_DIR / f"upload_{audio_file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        result = pipeline.process_voice(str(temp_path), forced_language=language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/{filename}")
def get_audio_file(filename: str):
    """Stream synthesized spoken audio response to client."""
    file_path = config.TEMP_AUDIO_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(file_path, media_type="audio/mpeg" if filename.endswith(".mp3") else "audio/wav")

@app.get("/api/mandi")
def get_mandi_prices(
    commodity: str = Query(..., description="Crop or commodity name (e.g., cotton, soybean, wheat)"),
    market: Optional[str] = Query(None, description="Mandi/APMC market name"),
    lang: str = Query("mr", description="Response language ('mr', 'hi', 'en')")
):
    """Retrieve live or cached mandi prices with 'data as of' timestamp."""
    return pipeline.mandi_tool.get_prices(commodity_query=commodity, market_query=market, lang=lang)

@app.get("/api/weather")
def get_weather_advisory(
    district: Optional[str] = Query("nagpur", description="District name"),
    lang: str = Query("mr", description="Response language ('mr', 'hi', 'en')")
):
    """Retrieve district agromet weather advisory."""
    return pipeline.weather_tool.get_advisory(location_query=district, lang=lang)

@app.get("/api/benchmark")
def get_benchmark_report():
    """Retrieve latest quantitative evaluation benchmark report."""
    report_path = config.BASE_DIR / "benchmark_report.json"
    if report_path.exists():
        import json
        with open(report_path, "r", encoding="utf-8") as f:
            return json.load(f)
    runner = AgriculturalBenchmarkRunner()
    return runner.run_benchmark()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
