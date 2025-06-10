import requests
import os
from azure_config_loader import load_config

def get_tts_headers(config):
    """Generate headers for Azure TTS API."""
    return {
        "Ocp-Apim-Subscription-Key": config["azure"]["speech_key"],
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
        "User-Agent": "PythonTTSClient"
    }

def synthesize_text(text, voice_name, rate, output_path, tts_url, headers):
    """Convert text to speech using Azure TTS and save as WAV file."""
    ssml = (
        f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-IN">'
        f'<voice name="{voice_name}">' 
        f'<prosody rate="{rate}">{text}</prosody>'
        f'</voice></speak>'
    )

    response = requests.post(tts_url, headers=headers, data=ssml.encode("utf-8"))

    if response.status_code == 200:
        with open(output_path, "wb") as audio_file:
            audio_file.write(response.content)
        print(f"Audio saved: {output_path}")
    else:
        print(f"Error synthesizing audio. Status code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    config = load_config()

    # Load Azure configuration
    speech_key = config["azure"]["speech_key"]
    service_region = config["azure"]["service_region"]
    tts_url = config["azure"].get("tts_endpoint", "").rstrip("/") + "/cognitiveservices/v1"
    voice_selection = config["azure"]["voice"].lower()
    speech_rate = config["azure"]["rate"]
    slides_for_tts = set(config.get("slides_for_tts", []))  # Get slides to process

    # Select voice
    voice_name = "en-IN-NeerjaNeural" if voice_selection == "female" else "en-IN-PrabhatNeural"

    # Set up headers
    headers = get_tts_headers(config)

    # Process slides
    output_dir = config["output"]["audio_directory"]
    os.makedirs(output_dir, exist_ok=True)

    for slide_num in slides_for_tts:
        slide_text = f"Extracted text from slide {slide_num}."  # Placeholder for actual text extraction
        output_path = os.path.join(output_dir, f"slide_{slide_num}.wav")
        synthesize_text(slide_text, voice_name, speech_rate, output_path, tts_url, headers)
