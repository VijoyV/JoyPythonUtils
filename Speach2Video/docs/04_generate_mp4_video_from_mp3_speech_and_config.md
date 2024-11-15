# Steps:
1. Render Text on Image: For each slide, the specified text is rendered on the image using word wrapping.
2. Generate Image Clips: An image clip is created for each slide, and its duration is set according to the provided from_time and to_time.
3. Concatenate Clips: All image clips are concatenated, and the .mp3 audio is added to the video.
4. Export Video: The final video is saved as an .mp4 file with the synchronized images, audio, and engraved text.
5. This code will allow you to generate a video using multiple slides, overlay text on each slide, and set the duration for each slide, all according to the specifications in the config.json file.

# Key Elements in config.json:
- input_mp3: Path to the input MP3 file containing the audio.
- output_mp4: Path to the output MP4 file that will be generated.
- video_dimensions: Dimensions for the video (e.g., [720, 1280] for a vertical video).
- font_path (optional): Path to the font used for rendering the text. If not provided, the default font is used.
- slides: List of slides, each containing:
- image: Path to the image for the slide.
- from_time and to_time: Start and end times for the slide in the video (formatted as mm:ss).
- text: The text to be engraved on the image. The text will automatically wrap based on the image size.

# Sample Malayalam Text
സ്വർഗ്ഗസ്ഥനായ ഞങ്ങളുടെ പിതാവേ, 
അങ്ങയുടെ നാമം പൂജിതമാകണമേ, 
അങ്ങയുടെ രാജ്യം വരേണമേ,
അങ്ങയുടെ തിരുമനസ്സ്, സ്വർഗ്ഗത്തിലെപ്പോലെ ഭൂമിയിലുമാകണമേ. 

അന്നന്ന് വേണ്ട ആഹാരം ഞങ്ങൾക്ക് തരേണമേ.
ഞങ്ങളോട് തെറ്റ് ചെയ്യുന്നവരോട് ഞങ്ങൾ ക്ഷമിക്കുന്നതുപോലെ,
ഞങ്ങളുടെ തെറ്റുകൾ ഞങ്ങളോടും ക്ഷമിക്കേണമേ.
 
ഞങ്ങളെ പ്രലോഭനത്തിൽ ഉൾപ്പെടുത്തരുതേ
തിന്മയിൽ നിന്നും ഞങ്ങളെ രക്ഷിക്കണെമെ, ആമേൻ!

