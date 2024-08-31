import win32com.client
import os



def calculate_advance_time(text_length):
    """
    Calculate the slide advance time based on the length of the text.
    The time ranges from 3 to 25 seconds.
    """
    # Assuming a linear relationship between text length and advance time
    min_time = 5  # Minimum time in seconds
    max_time = 30  # Maximum time in seconds
    max_text_length = 400  # Assume max text length is 300 characters (for example)

    # Calculate advance time proportionally to text length
    advance_time = min_time + (max_time - min_time) * min(text_length / max_text_length, 1.0)

    print(f"text_length = {text_length}, advance_time = {advance_time}")
    return advance_time


def create_presentation_with_transitions(input_pptx_path, output_pptx_path):
    """
    Creates a new PowerPoint presentation with specified transitions and animations.

    Args:
        input_pptx_path (str): Path to the input PowerPoint presentation.
        output_pptx_path (str): Path to save the modified presentation.
        transition_effect (str, optional): The desired transition effect (e.g., "Push"). Defaults to "Push".
    """

    # Resolve absolute paths
    input_pptx_path = os.path.abspath(input_pptx_path)
    output_pptx_path = os.path.abspath(output_pptx_path)

    # Print the file paths for debugging
    print(f"Opening presentation at: {input_pptx_path}")
    print(f"Saving modified presentation to: {output_pptx_path}")

    # Check if the input file exists
    if not os.path.exists(input_pptx_path):
        raise FileNotFoundError(f"The file {input_pptx_path} does not exist.")

    # Open PowerPoint
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    # Do not change the visibility, let it be visible
    powerpoint.WindowState = 2  # Minimize the window (2 corresponds to ppWindowMinimized)

    try:
        # Attempt to open the presentation
        presentation = powerpoint.Presentations.Open(input_pptx_path)
        print("Presentation opened successfully.")

        # Iterate through the slides and apply transitions/animations
        for slide in presentation.Slides:
            # Get the length of the text in the second shape (assuming it's the question text)
            shapes = slide.Shapes
            if shapes.Count > 0:
                text_length = len(shapes(3).TextFrame.TextRange.Text) + len(shapes(4).TextFrame.TextRange.Text)
                advance_time = calculate_advance_time(text_length)
            else:
                advance_time = 5  # Default to 5 seconds if no text is found

            # Set slide transition timing
            slide.SlideShowTransition.AdvanceOnTime = True
            slide.SlideShowTransition.AdvanceTime = advance_time  # Set based on text length

            # Set the transition effect using the translated value
            # slide.SlideShowTransition.EntryEffect = transition_effect_value

            # Add animation to the third text box
            if shapes.Count >= 5:
                # Add fade animation to the fourth shape
                shape4 = shapes(5)
                effect = slide.TimeLine.MainSequence.AddEffect(
                    shape4, 13, 0, 2)  # 13 is msoAnimEffectFade, 2 is msoAnimTriggerAfterPrevious
                effect.Timing.Duration = 2  # 2 second duration
                effect.Timing.TriggerDelayTime = advance_time * 0.60  # 60% of advance time

        # Save and close the presentation as a new file
        presentation.SaveAs(output_pptx_path)
        print(f"Presentation saved to: {output_pptx_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the presentation and quit PowerPoint
        presentation.Close()
        powerpoint.Quit()
        print("PowerPoint application closed.")


if __name__ == "__main__":
    input_pptx_path = './output/Judges_Chapter_03_MCQ_V1.pptx'
    output_pptx_path = './output/Judges_Chapter_03_MCQ_V2.pptx'
    create_presentation_with_transitions(input_pptx_path, output_pptx_path)
