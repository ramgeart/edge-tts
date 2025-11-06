"""OpenAI-compatible API server for edge-tts."""

import io
from typing import AsyncGenerator, Dict, Optional, Union

try:
    from fastapi import FastAPI, HTTPException, Response
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field
except ImportError as e:
    raise ImportError(
        "FastAPI dependencies are required for the API server. "
        "Install them with: pip install edge-tts[server]"
    ) from e

from .communicate import Communicate


# OpenAI voice to edge-tts voice mapping
VOICE_MAPPING = {
    "alloy": "en-US-AndrewNeural",
    "ash": "en-US-AshleyNeural",
    "ballad": "en-US-BrianNeural",
    "coral": "en-US-CoraNeural",
    "echo": "en-US-EricNeural",
    "fable": "en-US-GuyNeural",
    "onyx": "en-US-RogerNeural",
    "nova": "en-US-EmmaNeural",
    "sage": "en-US-SaraNeural",
    "shimmer": "en-US-JennyNeural",
    "verse": "en-US-AriaNeural",
}

# Model names (for compatibility, all use the same engine)
SUPPORTED_MODELS = ["tts-1", "tts-1-hd", "gpt-4o-mini-tts"]

# Supported response formats
# Note: Only mp3 is currently supported natively. Other formats require ffmpeg conversion.
SUPPORTED_FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]
NATIVE_FORMATS = ["mp3"]  # Formats supported without conversion


class SpeechRequest(BaseModel):
    """Request model for speech generation."""

    input: str = Field(
        ..., max_length=4096, description="The text to generate audio for"
    )
    model: str = Field(..., description="One of the available TTS models")
    voice: str = Field(..., description="The voice to use when generating the audio")
    instructions: Optional[str] = Field(
        None, description="Additional instructions for the voice"
    )
    response_format: str = Field("mp3", description="The format to return audio in")
    speed: float = Field(
        1.0, ge=0.25, le=4.0, description="The speed of the generated audio"
    )
    stream_format: Optional[str] = Field(
        "audio", description="The format to stream the audio in"
    )


app = FastAPI(
    title="Edge TTS OpenAI-compatible API",
    description="OpenAI-compatible text-to-speech API using Microsoft Edge TTS",
    version="1.0.0"
)


def speed_to_rate(speed: float) -> str:
    """
    Convert OpenAI speed parameter to edge-tts rate parameter.

    Args:
        speed: Speed value from 0.25 to 4.0, where 1.0 is normal speed

    Returns:
        Rate string in edge-tts format (e.g., "+50%", "-25%")
    """
    # Convert speed to percentage change
    # speed 1.0 = +0%, speed 2.0 = +100%, speed 0.5 = -50%
    percentage = int((speed - 1.0) * 100)
    return f"{percentage:+d}%"


def get_content_type(response_format: str) -> str:
    """Get MIME content type for the response format."""
    format_to_mime = {
        "mp3": "audio/mpeg",
        "opus": "audio/opus",
        "aac": "audio/aac",
        "flac": "audio/flac",
        "wav": "audio/wav",
        "pcm": "audio/pcm",
    }
    return format_to_mime.get(response_format, "audio/mpeg")


async def generate_speech(
    text: str,
    voice: str,
    rate: str = "+0%",
) -> bytes:
    """
    Generate speech audio from text.

    Args:
        text: The text to convert to speech
        voice: The edge-tts voice name
        rate: The speech rate

    Returns:
        Audio data as bytes
    """
    communicate = Communicate(text, voice, rate=rate)
    audio_data = io.BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.write(chunk["data"])

    return audio_data.getvalue()


async def generate_speech_stream(
    text: str,
    voice: str,
    rate: str = "+0%",
) -> AsyncGenerator[bytes, None]:
    """
    Generate speech audio from text as a stream.

    Args:
        text: The text to convert to speech
        voice: The edge-tts voice name
        rate: The speech rate

    Yields:
        Audio data chunks
    """
    communicate = Communicate(text, voice, rate=rate)

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]


@app.post("/v1/audio/speech", response_model=None)
async def create_speech(request: SpeechRequest) -> Union[StreamingResponse, Response]:
    """
    Generate audio from the input text.

    This endpoint is compatible with OpenAI's text-to-speech API.
    """
    # Validate model parameter
    if request.model not in SUPPORTED_MODELS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid model '{request.model}'. "
                f"Supported models: {SUPPORTED_MODELS}"
            )
        )

    # Validate voice parameter
    if request.voice not in VOICE_MAPPING:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid voice '{request.voice}'. "
                f"Supported voices: {list(VOICE_MAPPING.keys())}"
            )
        )

    # Validate format parameter
    if request.response_format not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid format '{request.response_format}'. "
                f"Supported formats: {SUPPORTED_FORMATS}"
            )
        )

    # Check if format is natively supported (currently only mp3)
    if request.response_format not in NATIVE_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Format '{request.response_format}' requires audio conversion. "
                f"Only {NATIVE_FORMATS} formats are currently supported."
            )
        )

    # Map OpenAI voice to edge-tts voice
    edge_voice = VOICE_MAPPING[request.voice]

    # Convert speed to rate
    rate = speed_to_rate(request.speed)

    # Get content type
    content_type = get_content_type(request.response_format)

    # Check if streaming is requested
    if request.stream_format == "audio":
        # Stream the audio
        return StreamingResponse(
            generate_speech_stream(request.input, edge_voice, rate),
            media_type=content_type
        )

    # Generate complete audio
    audio_data = await generate_speech(request.input, edge_voice, rate)
    return Response(content=audio_data, media_type=content_type)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


def main() -> None:
    """Run the API server."""
    import uvicorn  # pylint: disable=import-outside-toplevel
    uvicorn.run(app, host="0.0.0.0", port=5050)


if __name__ == "__main__":
    main()
