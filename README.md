# driaClaude

A CPU-based Docker container with WebGUI for TTS (Text-to-Speech) based on the dia model, featuring voice cloning, granular control, and API integration.

## Features

- 🎙️ **Text-to-Speech Generation** - High-quality speech synthesis with dialogue support
- 🎭 **Voice Cloning** - Clone and save voices from audio samples
- 🎛️ **Granular Control** - Fine-tune voice parameters (temperature, guidance scale, etc.)
- 🌐 **Web Interface** - User-friendly GUI accessible on port 4144
- 📥 **Download Support** - Download generated audio files
- 🔌 **REST API** - Integrate with other applications
- 🐳 **Docker Ready** - Easy deployment with docker-compose
- 💻 **CPU Optimized** - Runs without GPU requirements

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/jyoung2000/driaClaude.git
cd driaClaude
```

2. Build and run the container:
```bash
docker compose build
docker compose up -d
```

3. Access the web interface at: http://localhost:4144

### Configuration

Environment variables can be set in `.env` file or docker-compose.yml:

- `PORT` - Web server port (default: 4144)
- `API_KEY` - API authentication key
- `ENABLE_AUTH` - Enable/disable authentication (default: false)
- `MAX_AUDIO_LENGTH` - Maximum audio length in seconds (default: 300)

### API Documentation

When the container is running, access the interactive API documentation at:
- Swagger UI: http://localhost:4144/docs
- ReDoc: http://localhost:4144/redoc

## Usage

### Web Interface

1. **Text-to-Speech**: Enter text with dialogue tags [S1] and [S2]
2. **Voice Selection**: Choose from available voices or use default
3. **Parameters**: Adjust voice generation parameters
4. **Generate**: Click to create audio
5. **Download**: Save generated audio files

### Voice Cloning

1. Upload an audio sample (5-10 seconds)
2. Provide transcript of the audio
3. Name your voice
4. Use the cloned voice in future generations

### API Example

```python
import requests

# Generate speech
response = requests.post(
    "http://localhost:4144/api/v1/generate",
    json={
        "text": "[S1] Hello! [S2] Hi there! How are you?",
        "voice_id": "default",
        "temperature": 1.8
    }
)

# Download audio
audio_url = response.json()["audio_url"]
```

## Development

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

### Project Structure

```
driaClaude/
├── app/
│   ├── api/          # REST API endpoints
│   ├── models/       # TTS engine and models
│   ├── web/          # Web interface routes
│   └── config.py     # Configuration settings
├── static/           # Frontend assets
├── docker-compose.yml
├── Dockerfile
└── main.py          # Application entry point
```

## License

This project is based on the dia model by Nari Labs and is licensed under Apache License 2.0.

## Acknowledgments

- [Nari Labs](https://github.com/nari-labs/dia) for the original dia TTS model
- Hugging Face for Transformers support