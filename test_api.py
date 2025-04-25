import requests
import base64

# Your Railway deployment URL
API_URL = "https://your-railway-url.railway.app"  # Replace with your URL
API_KEY = "your-api-key"  # Replace with your API key

# Test the root endpoint
response = requests.get(
    f"{API_URL}/",
    headers={"X-API-Key": API_KEY}
)
print("Root endpoint response:", response.json())

# Test transcription with a small audio file
with open("audio.wav", "rb") as audio_file:  # Replace with your audio file
    audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')

response = requests.post(
    f"{API_URL}/transcribe/",
    json={"audio_base64": audio_base64},
    headers={
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
)
print("Transcription response:", response.json()) 