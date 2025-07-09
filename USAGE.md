# driaClaude Usage Guide

## Quick Start

1. **Build the container:**
   ```bash
   docker compose build
   ```

2. **Start the container:**
   ```bash
   docker compose up -d
   ```

3. **Access the web interface:**
   Open http://localhost:4144 in your browser

## Web Interface Features

### Text-to-Speech Generation

1. Navigate to the home page
2. Enter your text in the input field
3. Use dialogue tags:
   - `[S1]` for speaker 1
   - `[S2]` for speaker 2
   - Add non-verbal sounds: `(laughs)`, `(sighs)`, `(coughs)`

4. Adjust generation parameters:
   - **Temperature**: Controls randomness (0.1-2.0)
   - **Guidance Scale**: Controls adherence to prompt (1.0-10.0)
   - **Top P**: Nucleus sampling parameter (0.1-1.0)
   - **Top K**: Top-k sampling parameter (1-100)
   - **Seed**: Optional for reproducible results

5. Click "Generate Speech" to create audio
6. Download or play the generated audio

### Voice Cloning

1. Go to the "Voices" page
2. Upload an audio sample (5-10 seconds)
3. Provide an accurate transcript with speaker tags
4. Name your voice
5. Click "Clone Voice"
6. Use the cloned voice in TTS generation

### API Usage

#### Generate Speech
```bash
curl -X POST http://localhost:4144/api/v1/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "[S1] Hello world! [S2] Hi there!",
    "temperature": 1.8,
    "guidance_scale": 3.0
  }'
```

#### Clone Voice
```bash
curl -X POST http://localhost:4144/api/v1/voices/clone \
  -F "name=John Doe" \
  -F "transcript=[S1] This is a sample of my voice" \
  -F "audio_file=@sample.mp3"
```

#### List Voices
```bash
curl http://localhost:4144/api/v1/voices/list
```

## Environment Variables

- `PORT`: Web server port (default: 4144)
- `API_KEY`: API authentication key
- `ENABLE_AUTH`: Enable/disable authentication
- `MAX_AUDIO_LENGTH`: Maximum audio length in seconds
- `MODEL_NAME`: Hugging Face model to use
- `TEMPERATURE`: Default temperature value
- `GUIDANCE_SCALE`: Default guidance scale

## Tips

1. **Better Results:**
   - Keep input text moderate length (5-20 seconds of speech)
   - Use speaker tags consistently
   - Provide clear transcripts for voice cloning

2. **Performance:**
   - First generation may be slow (model download)
   - CPU generation is slower than GPU
   - Consider using lower precision for faster generation

3. **Voice Cloning:**
   - Use high-quality audio samples
   - Ensure accurate transcripts
   - 5-10 second samples work best

## Troubleshooting

### Container won't start
- Check Docker logs: `docker compose logs`
- Ensure port 4144 is not in use
- Verify Docker has enough memory allocated

### Slow generation
- CPU inference is naturally slower than GPU
- First run downloads the model (~5GB)
- Consider reducing max_new_tokens for faster results

### Voice cloning fails
- Check audio format (MP3, WAV, FLAC, OGG supported)
- Ensure audio is 5-10 seconds long
- Verify transcript accuracy

### API authentication issues
- Set `ENABLE_AUTH=false` for development
- Use correct API key in Authorization header
- Check CORS settings if calling from browser