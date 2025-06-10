from pydub import AudioSegment
from pydub.playback import play


def concatenate_audios_with_fade(audio_files, fade_duration=2000):
    # Initialize an empty AudioSegment
    final_audio = AudioSegment.empty()

    for i, file in enumerate(audio_files):
        # Load the audio file
        audio = AudioSegment.from_file(file)

        # Apply fade-in and fade-out, except for the first and last files
        if i > 0:
            audio = audio.fade_in(fade_duration)
        if i < len(audio_files) - 1:
            audio = audio.fade_out(fade_duration)

        # Concatenate the audio
        final_audio += audio

    return final_audio


# List of MP3 files to concatenate
audio_files = ["./BG-Music/Amazement - Freedom Trail Studio.mp3",
               "./BG-Music/Everything Where it Needs to Be - Nat Keefe & Hot Buttered Rum.mp3",
               "./BG-Music/Slow Times Over Here - Midnight North.mp3",
               "./BG-Music/Sunshine on Sand - Unicorn Heads.mp3"]  # Replace with your file paths

# Generate the final concatenated audio
final_audio = concatenate_audios_with_fade(audio_files)

# Export the final audio to a file
final_audio.export("Combined BG Music.mp3", format="mp3")

print("Audio concatenated successfully and saved as 'Combined BG Music.mp3'!")