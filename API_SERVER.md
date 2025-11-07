# Edge TTS OpenAI-Compatible API Server

This module provides an OpenAI-compatible REST API for the edge-tts service, allowing you to use Microsoft Edge's text-to-speech service through a familiar API interface.

## Installation

To use the API server, install edge-tts with the server dependencies:

```bash
pip install edge-tts[server]
```

## Starting the Server

Run the API server with:

```bash
edge-tts-api
```

By default, the server runs on `http://127.0.0.1:5050` (localhost only for security).

To expose the server to other machines on your network:

```bash
edge-tts-api --host 0.0.0.0
```

To use a different port:

```bash
edge-tts-api --port 8080
```

## API Endpoints

### POST /v1/audio/speech

Generate audio from text input. This endpoint is compatible with OpenAI's text-to-speech API.

**Request Body:**

```json
{
  "input": "Text to convert to speech",
  "model": "tts-1",
  "voice": "alloy",
  "response_format": "mp3",
  "speed": 1.0
}
```

**Parameters:**

- `input` (string, required): The text to generate audio for. Maximum length is 4096 characters.
- `model` (string, required): One of the available TTS models: `tts-1`, `tts-1-hd`, or `gpt-4o-mini-tts`.
- `voice` (string, required): The voice to use. Supported voices are:
  - `alloy`
  - `ash`
  - `ballad`
  - `coral`
  - `echo`
  - `fable`
  - `onyx`
  - `nova`
  - `sage`
  - `shimmer`
  - `verse`
- `response_format` (string, optional): The audio format. Currently only `mp3` is supported. Default: `mp3`
- `speed` (number, optional): The speed of the generated audio. Range: 0.25 to 4.0. Default: 1.0

**Response:**

Returns the audio file in the requested format with appropriate `Content-Type` header.

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

## Usage Examples

### Python with aiohttp

```python
import asyncio
import aiohttp

async def generate_speech():
    url = "http://localhost:5050/v1/audio/speech"
    payload = {
        "model": "tts-1",
        "voice": "alloy",
        "input": "Today is a wonderful day to build something people love!",
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            audio_data = await response.read()
            with open("speech.mp3", "wb") as f:
                f.write(audio_data)

asyncio.run(generate_speech())
```

### Python with requests

```python
import requests

url = "http://localhost:5050/v1/audio/speech"
payload = {
    "model": "tts-1",
    "voice": "alloy",
    "input": "Today is a wonderful day to build something people love!",
}

response = requests.post(url, json=payload)
with open("speech.mp3", "wb") as f:
    f.write(response.content)
```

### cURL

```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "voice": "alloy",
    "input": "Today is a wonderful day to build something people love!"
  }' \
  --output speech.mp3
```

### Node.js (OpenAI SDK Compatible)

```javascript
// Note: You can use the OpenAI SDK by changing the base URL
import OpenAI from "openai";
import fs from "fs";
import path from "path";

const openai = new OpenAI({
  apiKey: "dummy-key", // API key not required for edge-tts
  baseURL: "http://localhost:5050/v1",
});

const speechFile = path.resolve("./speech.mp3");

async function main() {
  const mp3 = await openai.audio.speech.create({
    model: "tts-1",
    voice: "alloy",
    input: "Today is a wonderful day to build something people love!",
  });
  
  const buffer = Buffer.from(await mp3.arrayBuffer());
  await fs.promises.writeFile(speechFile, buffer);
}

main();
```

## Voice Mapping

OpenAI voices are mapped to Microsoft Edge TTS voices as follows:

| OpenAI Voice | Edge TTS Voice |
|--------------|----------------|
| alloy        | en-US-AndrewNeural |
| ash          | en-US-AshleyNeural |
| ballad       | en-US-BrianNeural |
| coral        | en-US-CoraNeural |
| echo         | en-US-EricNeural |
| fable        | en-US-GuyNeural |
| onyx         | en-US-RogerNeural |
| nova         | en-US-EmmaNeural |
| sage         | en-US-SaraNeural |
| shimmer      | en-US-JennyNeural |
| verse        | en-US-AriaNeural |

## Limitations

- Currently only `mp3` format is supported. Other formats (opus, aac, flac, wav, pcm) are not supported.
- The `instructions` parameter from OpenAI's API is not supported (not available in Edge TTS).
- The `stream_format` parameter only supports `"audio"` (default). SSE streaming is not implemented.

## OpenAPI Documentation

Once the server is running, you can access the auto-generated API documentation at:

- Swagger UI: `http://localhost:5050/docs`
- ReDoc: `http://localhost:5050/redoc`
- OpenAPI JSON: `http://localhost:5050/openapi.json`
