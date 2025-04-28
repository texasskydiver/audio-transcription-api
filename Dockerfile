FROM python:3.10-slim

# Install FFmpeg and other dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Make start.sh executable
RUN chmod +x start.sh

# Expose port (Railway uses $PORT)
EXPOSE 8000

# Start the app using the entrypoint script (shell form for env var expansion)
CMD ./start.sh 