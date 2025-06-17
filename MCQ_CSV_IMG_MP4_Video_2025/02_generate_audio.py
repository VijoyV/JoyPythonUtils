# 02_generate_audio.py

import os
import json
from gtts import gTTS
from csv import DictReader
from pydub import AudioSegment

# === Load config ===
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

VOICE = config["voice"]
VOICE_LANG = VOICE.get("lang", "en")
VOICE_SLOW = VOICE.get("slow", False)
ANSWER_PREFIX = VOICE.get("answer_prefix", "The correct answer is")
SUFFIX_TEXT = VOICE.get("question_suffix", "Your time starts now.")

CSV_PATH = config["csv_file"]
AUDIO_OUT = os.path.join(config["output_dir"], "audio")
os.makedirs(AUDIO_OUT, exist_ok=True)

# === Constants ===
SILENCE_BEFORE_Q = 2400
SILENCE_AFTER_Q = 1200
SILENCE_BETWEEN_OPTIONS = 1200
SILENCE_BEFORE_A = 1000

def generate_gtts_wav(text: str, lang="en", slow=False) -> AudioSegment:
    tts = gTTS(text=text, lang=lang, slow=slow)
    tmp_mp3 = "temp.mp3"
    tts.save(tmp_mp3)
    sound = AudioSegment.from_mp3(tmp_mp3)
    os.remove(tmp_mp3)
    return sound.set_frame_rate(44100).set_channels(1)

def save_with_padding(audio: AudioSegment, filename: str, pre_ms: int = 0, post_ms: int = 0):
    padded = AudioSegment.silent(duration=pre_ms) + audio + AudioSegment.silent(duration=post_ms)
    padded.export(filename, format="wav")

def generate_slide_audio():
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = DictReader(f, delimiter='|')  # <-- Use '|' as delimiter

        for i, row in enumerate(reader, 1):
            base = os.path.join(AUDIO_OUT, f"slide_{i:03d}")
            print(f"🔊 Generating audio for slide {i:03d}...")

            # 1. Question narration
            q_text = row.get("Question", "").strip()
            if not q_text:
                print(f"⚠️ Skipping empty question at row {i}")
                continue
            q_audio = generate_gtts_wav(q_text, lang=VOICE_LANG, slow=VOICE_SLOW)

            # 2. Options
            option_labels = ["Option A", "Option B", "Option C", "Option D"]
            combined_options_audio = AudioSegment.silent(duration=0)
            for label in option_labels:
                opt_text = row.get(label, "").strip()
                if opt_text:
                    label_letter = label.split()[-1]  # Extract A/B/C/D
                    opt_audio = generate_gtts_wav(f"{label_letter}. {opt_text}", lang=VOICE_LANG, slow=VOICE_SLOW)
                    combined_options_audio += opt_audio + AudioSegment.silent(duration=SILENCE_BETWEEN_OPTIONS)

            # 3. Add suffix "Your time starts now."
            suffix_audio = generate_gtts_wav(SUFFIX_TEXT, lang=VOICE_LANG, slow=VOICE_SLOW)

            # Combine all
            full_q_audio = (
                q_audio +
                AudioSegment.silent(duration=SILENCE_BETWEEN_OPTIONS) +
                combined_options_audio +
                AudioSegment.silent(duration=800) +
                suffix_audio
            )
            save_with_padding(full_q_audio, f"{base}_q.wav", pre_ms=SILENCE_BEFORE_Q, post_ms=SILENCE_AFTER_Q)

            # 4. Answer narration
            ans_text = row.get("Answer", "").strip()
            if ans_text:
                prefix_audio = generate_gtts_wav(ANSWER_PREFIX, lang=VOICE_LANG, slow=VOICE_SLOW)
                answer_audio = generate_gtts_wav(ans_text, lang=VOICE_LANG, slow=VOICE_SLOW)
                final_answer = prefix_audio + AudioSegment.silent(duration=500) + answer_audio
                save_with_padding(final_answer, f"{base}_a.wav", pre_ms=SILENCE_BEFORE_A)

if __name__ == "__main__":
    generate_slide_audio()
