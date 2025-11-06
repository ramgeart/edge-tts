#!/usr/bin/env python3

"""Example script demonstrating OpenAI-compatible API usage with edge-tts."""

import asyncio
import aiohttp


async def test_api():
    """Test the edge-tts API server."""

    # API endpoint
    url = "http://localhost:5050/v1/audio/speech"

    # Request payload (OpenAI-compatible format)
    payload = {
        "model": "tts-1",
        "voice": "alloy",
        "input": "Today is a wonderful day to build something people love!",
        "response_format": "mp3",
        "speed": 1.0
    }

    print(f"Sending request to {url}")
    print(f"Payload: {payload}")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                # Save the audio file
                audio_data = await response.read()
                output_file = "speech.mp3"
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                print(f"✓ Audio saved to {output_file} ({len(audio_data)} bytes)")
            else:
                error = await response.text()
                print(f"✗ Error: {response.status}")
                print(f"  {error}")


if __name__ == "__main__":
    asyncio.run(test_api())
