import json
import math
import os
import win32com.client
from mutagen.mp3 import MP3
from mutagen.wave import WAVE  # For WAV file duration


def calculate_advance_time(audio_duration, additional_time=5):
    return math.ceil(audio_duration + additional_time)


def add_audio_to_slide(slide, audio_file):
    if os.path.exists(audio_file):
        audio_shape = slide.Shapes.AddMediaObject2(audio_file, LinkToFile=False, SaveWithDocument=True)
        audio_shape.AnimationSettings.PlaySettings.PlayOnEntry = True
        audio_shape.AnimationSettings.PlaySettings.HideWhileNotPlaying = True
        audio_shape.AnimationSettings.AdvanceMode = 1
        print(f"Added audio file {audio_file} to slide {slide.SlideIndex}")
    else:
        print(f"Audio file {audio_file} not found for slide {slide.SlideIndex}")


def configure_slide_transition(slide, audio_duration, additional_time=5):
    advance_time = calculate_advance_time(audio_duration, additional_time)
    slide.SlideShowTransition.AdvanceOnTime = True
    slide.SlideShowTransition.AdvanceTime = advance_time
    print(f"Slide {slide.SlideIndex} configured to transition after {advance_time} seconds")


def get_audio_duration(audio_file, audio_format):
    """Get duration of audio file based on format"""
    try:
        if audio_format == "mp3":
            return math.ceil(MP3(audio_file).info.length)
        elif audio_format == "wav":
            return math.ceil(WAVE(audio_file).info.length)
        else:
            raise ValueError(f"Unsupported audio format: {audio_format}")
    except Exception as e:
        print(f"Error getting duration for {audio_file}: {e}")
        return 5  # Default duration if there's an error


def create_presentation_with_transitions(input_pptx_path, output_pptx_path, audio_files_path, audio_format):
    input_pptx_path = os.path.abspath(input_pptx_path)
    output_pptx_path = os.path.abspath(output_pptx_path)
    audio_files_path = os.path.abspath(audio_files_path)

    if not os.path.exists(input_pptx_path):
        raise FileNotFoundError(f"The file {input_pptx_path} does not exist.")

    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    powerpoint.Visible = 1

    try:
        presentation = powerpoint.Presentations.Open(input_pptx_path)
        print(f"Opened presentation: {input_pptx_path}")

        for slide in presentation.Slides:
            slide_index = slide.SlideIndex
            audio_file = os.path.join(audio_files_path, f"slide_{slide_index}_narration.{audio_format}")

            if os.path.exists(audio_file):
                audio_duration = get_audio_duration(audio_file, audio_format)
                add_audio_to_slide(slide, audio_file)
                configure_slide_transition(slide, audio_duration)
            else:
                print(f"Audio file not found: {audio_file}")
                configure_slide_transition(slide, 5)  # Default transition time

        presentation.SaveAs(output_pptx_path)
        print(f"Presentation saved to: {output_pptx_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        presentation.Close()
        powerpoint.Quit()
        print("PowerPoint application closed.")


if __name__ == "__main__":
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    audio_format = config.get("audio_format", "mp3").lower()  # Default to mp3 if not specified

    # Select the appropriate audio directory based on format
    if audio_format == "wav":
        audio_files_path = config.get("slide_wav_narration_dir")
    else:
        audio_files_path = config.get("slide_mp3_narration_dir")

    create_presentation_with_transitions(
        config.get("pptx_input_path"),
        config.get("pptx_output_path"),
        audio_files_path,
        audio_format
    )