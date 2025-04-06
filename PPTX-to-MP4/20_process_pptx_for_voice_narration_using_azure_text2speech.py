import os
from config_loader import load_config
from pptx_processor import extract_and_save_text_from_pptx, read_text_from_files
from azure_tts import synthesize_text, get_tts_headers

# --- Load Configuration ---
config = load_config("config-azure.json")

pptx_filename = config["pptx"]["input_file"]
output_text_dir = config["output"]["text_directory"]
output_audio_dir = config["output"]["audio_directory"]
voice_selection = config["azure"]["voice"].lower()
speech_rate = config["azure"]["rate"]
tts_url = config["azure"]["tts_endpoint"].rstrip("/") + "/cognitiveservices/v1"

# Select voice for Indian English accent
voice_name = "en-IN-NeerjaNeural" if voice_selection == "female" else "en-IN-PrabhatNeural"

# Ensure output directories exist
os.makedirs(output_text_dir, exist_ok=True)
os.makedirs(output_audio_dir, exist_ok=True)

# --- Extract and Save Text to .txt Files ---
extract_and_save_text_from_pptx(pptx_filename, output_text_dir)

# --- Read Text from Stored Files ---
slide_texts = read_text_from_files(output_text_dir)

# --- Get API headers ---
headers = get_tts_headers(config)

# --- Generate Audio for Each Slide ---
for idx, text in enumerate(slide_texts, start=1):
    if not text.strip():
        print(f"Slide {idx} is empty; skipping audio generation.")
        continue

    audio_filename = os.path.join(output_audio_dir, f"slide_{idx}.wav")
    print(f"Generating audio for slide {idx}...")
    synthesize_text(text, voice_name, speech_rate, audio_filename, tts_url, headers)

print("Audio generation complete!")
