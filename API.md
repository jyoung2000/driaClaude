# driaClaude API Documentation

## Base URL
```
http://localhost:4144/api/v1
```

## Authentication

When `ENABLE_AUTH=true`, include the API key in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Text-to-Speech

#### Generate Speech
```http
POST /tts/generate
```

**Request Body:**
```json
{
  "text": "[S1] Hello! [S2] Hi there!",
  "voice_id": "optional_voice_id",
  "temperature": 1.8,
  "guidance_scale": 3.0,
  "top_p": 0.90,
  "top_k": 45,
  "seed": 12345
}
```

**Response:**
```json
{
  "success": true,
  "filename": "tts_20240101_120000_abc123.mp3",
  "audio_url": "/outputs/tts_20240101_120000_abc123.mp3",
  "metadata": {
    "text": "[S1] Hello! [S2] Hi there!",
    "voice_id": null,
    "parameters": {
      "temperature": 1.8,
      "guidance_scale": 3.0,
      "top_p": 0.9,
      "top_k": 45,
      "seed": 12345
    },
    "timestamp": "20240101_120000",
    "filename": "tts_20240101_120000_abc123.mp3"
  }
}
```

#### Batch Generate
```http
POST /tts/batch
```

**Request Body:**
```json
{
  "items": [
    {
      "text": "[S1] First text",
      "temperature": 1.8
    },
    {
      "text": "[S2] Second text",
      "voice_id": "voice_123"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "success": true,
      "filename": "tts_20240101_120000_abc123.mp3",
      "audio_url": "/outputs/tts_20240101_120000_abc123.mp3",
      "metadata": {...}
    }
  ],
  "failed": [],
  "total": 2
}
```

#### Download Audio
```http
GET /tts/download/{filename}
```

#### Delete Audio
```http
DELETE /tts/audio/{filename}
```

#### List Audio Files
```http
GET /tts/list?limit=50&offset=0
```

**Response:**
```json
{
  "files": [
    {
      "filename": "tts_20240101_120000_abc123.mp3",
      "size": 245760,
      "created_at": 1704110400,
      "url": "/outputs/tts_20240101_120000_abc123.mp3"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

### Voice Management

#### Clone Voice
```http
POST /voices/clone
```

**Request (multipart/form-data):**
- `name`: Voice name (required)
- `transcript`: Accurate transcript of audio (required)
- `description`: Voice description (optional)
- `audio_file`: Audio file (required, 5-10 seconds)

**Response:**
```json
{
  "success": true,
  "voice_id": "abc123def456",
  "message": "Voice 'John Doe' cloned successfully"
}
```

#### List Voices
```http
GET /voices/list
```

**Response:**
```json
{
  "voices": [
    {
      "id": "abc123def456",
      "name": "John Doe",
      "description": "Male voice, deep tone",
      "created_at": "2024-01-01T12:00:00",
      "duration": 7.5
    }
  ],
  "total": 5
}
```

#### Get Voice Details
```http
GET /voices/{voice_id}
```

#### Delete Voice
```http
DELETE /voices/{voice_id}
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

No built-in rate limiting, but recommended limits:
- TTS generation: 10 requests per minute
- Voice cloning: 5 requests per minute
- Batch generation: 1 request per minute

## WebSocket Support

Not currently implemented. All operations are synchronous HTTP requests.

## CORS

CORS is enabled for all origins by default. Restrict in production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```