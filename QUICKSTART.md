# Quick Start Guide - Edge TTS OpenAI API Server

## Installation

```bash
pip install edge-tts[server]
```

## Start the Server

```bash
edge-tts-api
```

The server will start on `http://127.0.0.1:5050` (localhost only)

To expose to other machines:
```bash
edge-tts-api --host 0.0.0.0
```

To use a different port:
```bash
edge-tts-api --port 8080
```

## Test with cURL

```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "voice": "alloy",
    "input": "Hello from edge-tts!"
  }' \
  --output speech.mp3
```

## Available Voices

- `alloy` - Andrew (en-US-AndrewNeural)
- `ash` - Ashley (en-US-AshleyNeural)
- `ballad` - Brian (en-US-BrianNeural)
- `coral` - Cora (en-US-CoraNeural)
- `echo` - Eric (en-US-EricNeural)
- `fable` - Guy (en-US-GuyNeural)
- `onyx` - Roger (en-US-RogerNeural)
- `nova` - Emma (en-US-EmmaNeural)
- `sage` - Sara (en-US-SaraNeural)
- `shimmer` - Jenny (en-US-JennyNeural)
- `verse` - Aria (en-US-AriaNeural)

## API Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| input | string | required | Text to convert (max 4096 chars) |
| model | string | required | Model: tts-1, tts-1-hd, or gpt-4o-mini-tts |
| voice | string | required | Voice name (see list above) |
| response_format | string | "mp3" | Audio format (only mp3 supported) |
| speed | float | 1.0 | Speed from 0.25 to 4.0 |
| stream_format | string | "audio" | Streaming format (only "audio" supported) |

## Health Check

```bash
curl http://localhost:5050/health
```

Response: `{"status": "healthy"}`

## Documentation

- Swagger UI: http://localhost:5050/docs
- ReDoc: http://localhost:5050/redoc
- Full Documentation: See API_SERVER.md

## OpenAI SDK Compatibility

Change the baseURL to use with OpenAI SDK:

```javascript
const openai = new OpenAI({
  apiKey: "dummy",
  baseURL: "http://localhost:5050/v1"
});
```

## Examples

See `examples/openai_compatible_api_example.py` for a complete Python example.
