"""
ElevenLabs Voice Client for TeachBack AI
Generates voice responses for AI student personalities
"""

import os
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from typing import Optional

# Initialize ElevenLabs client
def get_elevenlabs_client():
    """Get initialized ElevenLabs client"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
    return ElevenLabs(api_key=api_key)


# Voice IDs for different AI student personalities
# These are pre-made voices from ElevenLabs library
VOICE_PERSONALITIES = {
    "🤔 Socratic Student": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam - thoughtful, patient male voice
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.5,
        "description": "Thoughtful and patient teacher voice"
    },
    "😈 Contrarian Student": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella - confident, challenging female voice
        "stability": 0.6,
        "similarity_boost": 0.8,
        "style": 0.7,
        "description": "Confident and challenging voice"
    },
    "👶 Five-Year-Old Student": {
        "voice_id": "ThT5KcBeYPX3keUQqHPh",  # Dorothy - young, curious female voice
        "stability": 0.4,
        "similarity_boost": 0.7,
        "style": 0.4,
        "description": "Young, curious child voice"
    },
    "😰 Anxious Student": {
        "voice_id": "pqHfZKP75CvOlQylNhV4",  # Bill - nervous, worried male voice
        "stability": 0.3,
        "similarity_boost": 0.6,
        "style": 0.3,
        "description": "Nervous and worried voice"
    }
}


def generate_voice_response(
    text: str,
    mode: str,
    output_path: Optional[str] = None
) -> Optional[bytes]:
    """
    Generate voice audio for AI student response

    Args:
        text: The text to convert to speech
        mode: AI student personality mode
        output_path: Optional path to save audio file

    Returns:
        Audio bytes if successful, None if error
    """
    try:
        client = get_elevenlabs_client()

        # Get voice settings for this personality
        personality = VOICE_PERSONALITIES.get(mode)
        if not personality:
            print(f"Warning: No voice mapping for mode '{mode}', using default")
            personality = VOICE_PERSONALITIES["🤔 Socratic Student"]

        # Generate speech with ElevenLabs
        response = client.text_to_speech.convert(
            voice_id=personality["voice_id"],
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_turbo_v2_5",  # Fast, high-quality model
            voice_settings=VoiceSettings(
                stability=personality["stability"],
                similarity_boost=personality["similarity_boost"],
                style=personality.get("style", 0.5),
                use_speaker_boost=True
            )
        )

        # Collect audio bytes
        audio_bytes = b""
        for chunk in response:
            if chunk:
                audio_bytes += chunk

        # Optionally save to file
        if output_path:
            with open(output_path, "wb") as f:
                f.write(audio_bytes)

        return audio_bytes

    except Exception as e:
        print(f"Error generating voice: {e}")
        return None


def text_to_speech_file(
    text: str,
    mode: str,
    output_filename: str = "response.mp3"
) -> Optional[str]:
    """
    Generate voice audio and save to file

    Args:
        text: The text to convert to speech
        mode: AI student personality mode
        output_filename: Name of output file

    Returns:
        Path to audio file if successful, None if error
    """
    import tempfile
    import os

    # Create temp file path
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, output_filename)

    # Generate audio
    audio_bytes = generate_voice_response(text, mode, output_path)

    if audio_bytes:
        return output_path
    else:
        return None
