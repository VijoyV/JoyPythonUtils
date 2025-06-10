import win32com.client
import os
import json
from mutagen.mp3 import MP3
import math

# Simplified calculation of advance time based on audio duration
def calculate_advance_time(audio_duration, additional_time=5):
    advance_time = math.ceil(audio_duration + additional_time)
    print(f"Audio duration = {audio_duration}, advance_time = {advance_time}")
    return advance_time

# Apply slide transition and optional Shape-5 animation (if present)
def apply_transition_and_animation(slide, audio_duration, additional_time=5, animation_duration=3):
    # Ensure the slide transition occurs after the full audio duration
    advance_time = calculate_advance_time(audio_duration, additional_time)
    slide.SlideShowTransition.AdvanceOnTime = True
    slide.SlideShowTransition.AdvanceTime = advance_time

    # Apply animation to Shape-5 if it exists, but ensure the slide transition is still based on audio
    if slide.Shapes.Count >= 5:
        shape = slide.Shapes(5)
        effect = slide.TimeLine.MainSequence.AddEffect(
            shape, 13, 0, 2)  # 13 is msoAnimEffectFade, 2 is msoAnimTriggerAfterPrevious
        effect.Timing.Duration = animation_duration
        effect.Timing.TriggerDelayTime = audio_duration  # Start animation after audio finishes
        print(f"Slide {slide.SlideIndex}: Shape-5 animation added. Total transition time: {advance_time}")

# Add audio to the slide
def add_audio_to_slide(slide, audio_file):
    if os.path.exists(audio_file):
        audio_shape = slide.Shapes.AddMediaObject2(audio_file, LinkToFile=False, SaveWithDocument=True)
        audio_shape.AnimationSettings.PlaySettings.PlayOnEntry = True
        audio_shape.AnimationSettings.PlaySettings.HideWhileNotPlaying = True
        audio_shape.AnimationSettings.AdvanceMode = 1  # 1 is msoAnimTriggerWithPrevious
        print(f"Added audio file {audio_file} to slide {slide.SlideIndex}")
    else:
        print(f"Audio file {audio_file} not found for slide {slide.SlideIndex}")

# Process the presentation and ensure all slides have proper transitions
def create_presentation_with_transitions(input_pptx_path, output_pptx_path, audio_files_path):
    input_pptx_path = os.path.abspath(input_pptx_path)
    output_pptx_path = os.path.abspath(output_pptx_path)
    audio_files_path = os.path.abspath(audio_files_path)

    print(f"Opening presentation at: {input_pptx_path}")
    print(f"Will save modified presentation to: {output_pptx_path}")

    if not os.path.exists(input_pptx_path):
        raise FileNotFoundError(f"The file {input_pptx_path} does not exist.")

    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    powerpoint.WindowState = 2  # Minimize the window

    try:
        presentation = powerpoint.Presentations.Open(input_pptx_path)
        print("Presentation opened successfully.")

        for slide in presentation.Slides:
            slide_index = slide.SlideIndex
            audio_file = os.path.join(audio_files_path, f"slide_{slide_index}_narration.mp3")

            if os.path.exists(audio_file):
                audio_duration = math.ceil(MP3(audio_file).info.length)
                add_audio_to_slide(slide, audio_file)
                apply_transition_and_animation(slide, audio_duration)
            else:
                # Even if no audio file, give a default advance time of 5 seconds
                apply_transition_and_animation(slide, 0)  # No audio, use default transition time

        # Save the modified presentation
        presentation.SaveAs(output_pptx_path)
        print(f"Presentation saved to: {output_pptx_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        presentation.Close()
        powerpoint.Quit()
        print("PowerPoint application closed.")

if __name__ == "__main__":
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    input_pptx_path = config.get('ppt_output_path_v1')
    output_pptx_path = config.get('ppt_output_path_v2')
    audio_files_path = config.get('slide_mp3_narration_dir')

    create_presentation_with_transitions(input_pptx_path, output_pptx_path, audio_files_path)
