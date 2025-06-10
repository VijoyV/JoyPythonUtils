import win32com.client
import os
import json
import math
import logging

# Optional import for .mp3 support
try:
    from mutagen.mp3 import MP3
except ImportError:
    MP3 = None

import wave

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_audio_duration(audio_file, ext):
    """Returns duration of audio file based on extension."""
    if ext == '.mp3':
        if MP3 is None:
            raise ImportError("mutagen.mp3 is required to read MP3 durations.")
        audio = MP3(audio_file)
        return audio.info.length
    elif ext == '.wav':
        with wave.open(audio_file, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    else:
        raise ValueError(f"Unsupported audio format: {ext}")

def calculate_advance_time(audio_duration, additional_time=5):
    """Calculates total slide advance time."""
    advance_time = math.ceil(audio_duration + additional_time)
    logging.info(f"Audio duration = {audio_duration:.2f}s, Advance time set to {advance_time}s")
    return advance_time

def apply_transition_and_animation(slide, audio_duration, additional_time=5):
    """Applies slide transition after audio ends."""
    advance_time = calculate_advance_time(audio_duration, additional_time)
    slide.SlideShowTransition.AdvanceOnTime = True
    slide.SlideShowTransition.AdvanceTime = advance_time

def add_audio_to_slide(slide, audio_file):
    """Embeds audio file in slide and sets playback behavior."""
    audio_shape = slide.Shapes.AddMediaObject2(audio_file, LinkToFile=False, SaveWithDocument=True)
    audio_shape.AnimationSettings.PlaySettings.PlayOnEntry = True
    audio_shape.AnimationSettings.PlaySettings.HideWhileNotPlaying = True
    audio_shape.AnimationSettings.AdvanceMode = 1  # msoAnimTriggerWithPrevious
    logging.info(f"✅ Added audio to slide {slide.SlideIndex}")

def create_presentation_with_transitions(input_pptx_path, output_pptx_path, audio_files_path, audio_ext):
    """Processes the PowerPoint file to embed audio and set transitions."""
    input_pptx_path = os.path.abspath(input_pptx_path)
    output_pptx_path = os.path.abspath(output_pptx_path)
    audio_files_path = os.path.abspath(audio_files_path)

    if not os.path.exists(input_pptx_path):
        raise FileNotFoundError(f"The file {input_pptx_path} does not exist.")

    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    powerpoint.Visible = True
    powerpoint.WindowState = 2  # Minimize

    try:
        presentation = powerpoint.Presentations.Open(input_pptx_path)

        for slide in presentation.Slides:
            slide_index = slide.SlideIndex
            audio_file = os.path.join(audio_files_path, f"slide_{slide_index}_narration{audio_ext}")

            try:
                if os.path.exists(audio_file):
                    duration = get_audio_duration(audio_file, audio_ext)
                    add_audio_to_slide(slide, audio_file)
                    apply_transition_and_animation(slide, duration)
                else:
                    logging.warning(f"⚠️ Audio file not found for slide {slide_index}, using default delay.")
                    apply_transition_and_animation(slide, 0)
            except Exception as e:
                logging.error(f"❌ Error processing slide {slide_index}: {e}")
                apply_transition_and_animation(slide, 0)

        presentation.SaveAs(output_pptx_path)
        logging.info(f"🎉 Presentation saved to: {output_pptx_path}")
    except Exception as e:
        logging.error(f"❌ An error occurred: {e}")
    finally:
        try:
            presentation.Close()
        except:
            pass
        powerpoint.Quit()
        logging.info("✅ PowerPoint application closed.")

if __name__ == "__main__":
    try:
        with open('02_config.json', 'r') as config_file:
            config = json.load(config_file)

        input_pptx_path = config.get('pptx_input_path_v1')
        output_pptx_path = config.get('pptx_output_path_v2')
        audio_files_path = config.get('audio_files_path')
        audio_ext = config.get('audio_file_extension', '.wav').lower()

        if audio_ext not in ['.mp3', '.wav']:
            raise ValueError("Only '.mp3' and '.wav' are supported.")

        create_presentation_with_transitions(input_pptx_path, output_pptx_path, audio_files_path, audio_ext)

    except Exception as e:
        logging.critical(f"💥 Fatal error: {e}")
