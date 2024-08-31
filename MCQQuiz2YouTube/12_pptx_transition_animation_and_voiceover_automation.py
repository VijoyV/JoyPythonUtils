import win32com.client
import os
import json
from mutagen.mp3 import MP3  # Make sure to install this package


def calculate_advance_time(slide_index, audio_duration=None, additional_time=3, animation_duration=2,
                           post_animation_delay=2):
    if audio_duration is None:
        audio_duration = 0
    # Total advance time includes audio duration, animation duration, and post-animation delay
    advance_time = audio_duration + animation_duration + post_animation_delay + additional_time
    print(f"Slide {slide_index}: audio_duration = {audio_duration}, advance_time = {advance_time}")
    return advance_time


def apply_transition_and_animation(slide, advance_time, animation_duration=2):
    slide.SlideShowTransition.AdvanceOnTime = True
    slide.SlideShowTransition.AdvanceTime = advance_time

    if slide.Shapes.Count >= 5:
        shape = slide.Shapes(5)
        effect = slide.TimeLine.MainSequence.AddEffect(
            shape, 13, 0, 1)  # 13 is msoAnimEffectFade, 1 is msoAnimTriggerWithPrevious
        effect.Timing.Duration = animation_duration
        print(f"Slide {slide.SlideIndex}: Added shape animation")


def add_audio_to_slide(slide, audio_file):
    if os.path.exists(audio_file):
        audio_shape = slide.Shapes.AddMediaObject2(audio_file, LinkToFile=False, SaveWithDocument=True)
        audio_shape.AnimationSettings.PlaySettings.PlayOnEntry = True
        audio_shape.AnimationSettings.PlaySettings.HideWhileNotPlaying = True
        audio_shape.AnimationSettings.AdvanceMode = 1  # 1 is msoAnimTriggerWithPrevious
        print(f"Added audio file {audio_file} to slide {slide.SlideIndex}")
    else:
        print(f"Audio file {audio_file} not found for slide {slide.SlideIndex}")


def create_presentation_with_transitions(input_pptx_path, output_pptx_path, audio_files_path):
    input_pptx_path = os.path.abspath(input_pptx_path)
    output_pptx_path = os.path.abspath(output_pptx_path)
    audio_files_path = os.path.abspath(audio_files_path)

    print(f"Opening presentation at: {input_pptx_path}")
    print(f"Saving modified presentation to: {output_pptx_path}")

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
                audio_duration = MP3(audio_file).info.length
                advance_time = calculate_advance_time(slide_index, audio_duration)
            else:
                advance_time = calculate_advance_time(slide_index)  # Use default time of 3 seconds

            # First add the audio so it plays as soon as the slide appears
            add_audio_to_slide(slide, audio_file)

            # Then apply the transition and animation with adjusted timing
            apply_transition_and_animation(slide, advance_time)

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
