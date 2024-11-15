# Generating .mp4 Video from .mp3 and .srt

## 4. Rendering Text on Image:
Load an image, overlay the subtitle text onto it, and save the result.
The text is split into lines that fit within the image's width.

## 5. Generating Image Clips for Each Subtitle:
For each subtitle in the .srt file, create an image clip with the text overlayed.
The duration of each clip corresponds to the subtitle timing.

## 6. Concatenating Image Clips and Adding Audio:
Concatenate all image clips in the order of subtitles.
Add the .mp3 audio as the background track.

## 7. Exporting the Final Video:
Save the resulting video as an .mp4 file, ensuring the video length matches the audio duration.