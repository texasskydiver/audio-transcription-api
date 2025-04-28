from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import base64
import tempfile
import os
import whisper
import numpy as np
import soundfile as sf
import io
import traceback
from typing import Optional
import urllib.request
import zipfile
import shutil
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security configuration
API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY") or "your-secret-api-key-change-this"  # Default key if not in env
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": API_KEY_NAME},
        )
    return api_key

app = FastAPI(
    title="Audio Transcription API",
    description="API for transcribing base64 encoded WAV files using Whisper",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware with more restrictive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),  # Configure via env var or allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to hold the model
model: Optional[whisper.Whisper] = None
model_loading = False

class AudioData(BaseModel):
    audio_base64: str

@app.on_event("startup")
async def load_model():
    global model, model_loading
    model_loading = True
    print("Loading Whisper model in background...")
    model = whisper.load_model("base")
    model_loading = False
    print("Whisper model loaded successfully")

def validate_and_convert_wav(audio_bytes):
    try:
        with io.BytesIO(audio_bytes) as wav_io:
            try:
                # Read audio data with soundfile (supports more formats including MULAW)
                data, samplerate = sf.read(wav_io)
                print(f"Audio file validated: {samplerate}Hz, shape: {data.shape}")
                
                # Create a temporary file with the converted audio (PCM format)
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                    # Write as 16-bit PCM WAV
                    sf.write(temp_audio.name, data, samplerate, subtype='PCM_16')
                    return temp_audio.name
                    
            except Exception as e:
                raise ValueError(f"Invalid audio format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Invalid audio format: {str(e)}\n{traceback.format_exc()}")

@app.post("/transcribe/", response_model=dict, dependencies=[Depends(verify_api_key)])
async def transcribe_audio(audio_data: AudioData):
    global model, model_loading
    
    # Check if model is ready
    if model is None:
        if model_loading:
            raise HTTPException(
                status_code=503,
                detail="Model is still loading. Please try again in a few moments."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Model failed to load. Please contact the administrator."
            )

    temp_audio_path = None
    try:
        # Log the length of received base64 string
        base64_string = audio_data.audio_base64.strip()
        print(f"Received base64 string length: {len(base64_string)}")
        
        # Add padding if needed
        padding = len(base64_string) % 4
        if padding:
            base64_string += '=' * (4 - padding)
            print(f"Added {4 - padding} padding characters")

        # Decode base64 string
        try:
            audio_bytes = base64.b64decode(base64_string)
            print(f"Successfully decoded base64 to {len(audio_bytes)} bytes")
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid base64 encoding: {str(e)}\nFirst 50 chars of input: {base64_string[:50]}..."
            )
        
        # Validate and convert WAV format
        try:
            temp_audio_path = validate_and_convert_wav(audio_bytes)
            print("Audio format validation and conversion successful")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        try:
            # Use the pre-loaded model
            print("Starting transcription...")
            result = model.transcribe(temp_audio_path)
            print("Transcription completed successfully")
            
            return {
                "status": "success",
                "text": result["text"]
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Transcription error: {str(e)}\n{traceback.format_exc()}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid audio data: {str(e)}\n{traceback.format_exc()}"
        )
    finally:
        # Clean up temporary file
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.unlink(temp_audio_path)
            except:
                pass

@app.get("/", dependencies=[Depends(verify_api_key)])
async def root():
    global model_loading, model
    status = "loading" if model_loading else "ready" if model else "failed"
    return {
        "message": "Audio Transcription API is running. Use POST /transcribe/ to transcribe audio.",
        "model_status": status
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port) 