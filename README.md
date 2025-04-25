# Audio Transcription API

This API provides endpoints for transcribing base64 encoded audio files using OpenAI's Whisper model.

## Project Structure

```
audio-transcription-api/
├── main.py              # Main FastAPI application
├── .env                 # Environment variables configuration
├── requirements.txt     # Python dependencies
├── ffmpeg/             # Auto-downloaded FFmpeg files
│   └── bin/            # FFmpeg binaries
└── .gitignore          # Git ignore file
```

## Critical Files

- `main.py`: The core application file containing the FastAPI server and transcription logic
- `.env`: Configuration file for API settings (create this from the template below)
- `requirements.txt`: Lists all Python package dependencies
- `ffmpeg/`: Directory automatically created to store FFmpeg binaries (created on first run)

## Environment Variables

Create a `.env` file in the root directory with the following settings:

```env
# API Configuration
API_KEY=your-secret-api-key-change-this
PORT=8000
HOST=0.0.0.0

# Security
ALLOWED_ORIGINS=*  # Use comma-separated values for multiple origins
```

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create the `.env` file as shown above

3. Run the server:
```bash
uvicorn main:app --reload
```

The API will automatically:
- Download and set up FFmpeg on first run
- Load the Whisper model in the background
- Start listening for requests

## API Endpoints

### GET /
- Health check endpoint
- Requires API key
- Returns current API status

### POST /transcribe/
- Main transcription endpoint
- Requires API key
- Accepts base64 encoded audio data
- Returns transcribed text

## API Authentication

All endpoints require an API key passed in the `X-API-Key` header:

```python
headers = {
    "X-API-Key": "your-secret-api-key-change-this",
    "Content-Type": "application/json"
}
```

## Example Usage

```python
import requests
import base64

# Read audio file and encode to base64
with open("audio.wav", "rb") as audio_file:
    audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')

# API endpoint
url = "http://your-server:8000/transcribe/"

# Headers with API key
headers = {
    "X-API-Key": "your-secret-api-key-change-this",
    "Content-Type": "application/json"
}

# Make request
response = requests.post(
    url,
    json={"audio_base64": audio_base64},
    headers=headers
)

# Print result
print(response.json())
```

## Supported Audio Formats

The API supports various audio formats including:
- WAV (PCM)
- WAV (µ-law)
- Other formats supported by soundfile library

## Security Notes

1. Change the default API key in `.env`
2. In production:
   - Use HTTPS
   - Set specific ALLOWED_ORIGINS
   - Use a strong API key
   - Consider adding rate limiting

## Troubleshooting

1. If FFmpeg fails to download automatically:
   - Download FFmpeg manually from https://github.com/BtbN/FFmpeg-Builds/releases
   - Extract to `ffmpeg/` directory in project root
   - Ensure `ffmpeg.exe` is in `ffmpeg/bin/`

2. If the model is slow to load:
   - The first request may take longer as the model loads
   - Check the API status at `/` endpoint
   - Monitor server logs for progress 