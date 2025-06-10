import os
import sqlite3
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, afx
from moviepy.audio.AudioClip import concatenate_audioclips
import textwrap
import json
import logging
import time
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure that required directories exist
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")
    else:
        logging.info(f"Directory already exists: {directory}")

# Improved: Connect to SQLite database with error handling
def connect_to_db(db_name="questions.db"):
    try:
        conn = sqlite3.connect(db_name)
        logging.info(f"Successfully connected to database: {db_name}")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection failed: {e}")
        raise

# Improved: Fetch questions with error handling
def fetch_questions(conn, subject, topics):
    cursor = conn.cursor()
    try:
        query = '''
            SELECT question_text, question_options, correct_answer, topic
            FROM question_bank
            WHERE subject = ? AND topic IN ({})
            ORDER BY subject, topic, question_id
            LIMIT 15
        '''.format(','.join(['?'] * len(topics)))
        cursor.execute(query, (subject, *topics))
        questions = cursor.fetchall()
        logging.info(f"Fetched {len(questions)} questions for subject {subject}.")
        return questions
    except sqlite3.Error as e:
        logging.error(f"Error fetching questions from database: {e}")
        raise

# Modularized: Ensure directories exist
def ensure_directories(config):
    ensure_directory_exists(config['working_slide_path'])
    ensure_directory_exists(os.path.dirname(config["output_video"]))

# Improved: Caching image and font loading
def load_resources(config):
    """Load the background image and fonts once and return them."""
    try:
        background_image = Image.open(config["background_image"])
        logging.info(f"Loaded background image: {config['background_image']}")
    except IOError as e:
        logging.error(f"Error loading background image: {e}")
        raise

    try:
        font_question = ImageFont.truetype(config["font_path_question"], config["font_settings"]['font_size_question'])
        font_options = ImageFont.truetype(config["font_path_options"], config["font_settings"]['font_size_options'])
        font_answer = ImageFont.truetype(config["font_path_answer"], config["font_settings"]['font_size_answer'])
        logging.info("Fonts loaded successfully")
    except IOError:
        logging.warning("Font file not found, using default font.")
        font_question = ImageFont.load_default()
        font_options = ImageFont.load_default()
        font_answer = ImageFont.load_default()

    return background_image, font_question, font_options, font_answer

# Modularized: Create and save the slides for questions and answers
def generate_slides(questions, config, background_image, font_question, font_options, font_answer):
    slides = []
    durations = []

    # Add start slide
    slides.append(create_slide_for_start_or_end(config["start_slide"], config))
    durations.append(config["slide_durations"]["start_slide"])

    # Create question and answer slides
    for idx, (question_text, question_options, correct_answer, topic) in enumerate(questions):
        logging.info(f"Processing question {idx + 1}/{len(questions)} for topic {topic}")

        # Format question text and options for the question slide
        options_list = question_options.replace('|', '\n').splitlines()
        formatted_options = "\n".join([f"{option.strip()}" for i, option in enumerate(options_list)])
        question_content = f"Q - {idx + 1}: {question_text}"
        options_content = f"{formatted_options}"

        # Create question slide
        question_slide = create_slide(question_content, options_content, background_image,
                                      font_question, font_options,
                                      f"{config['working_slide_path']}/slide_{idx + 1}", config, "question")

        # Create answer slide (only the answer, in a different font)
        answer_slide = create_slide(correct_answer, "", background_image,
                                    font_answer, font_answer,
                                    f"{config['working_slide_path']}/slide_{idx + 1}", config, "answer")

        # Add the slides to the list
        slides.extend([question_slide, answer_slide])
        durations.extend([config["slide_durations"]["question_slide"], config["slide_durations"]["answer_slide"]])

    # Add end slide
    slides.append(create_slide_for_start_or_end(config["end_slide"], config))
    durations.append(config["slide_durations"]["end_slide"])

    return slides, durations

# Function to create start or end slide in wide aspect ratio
def create_slide_for_start_or_end(image_path, config):
    img = Image.open(image_path)

    # Apply wide aspect ratio if specified in config
    if "wide_aspect_ratio" in config:
        img = img.resize((config["wide_aspect_ratio"]["width"], config["wide_aspect_ratio"]["height"]))  # Resize to wide aspect ratio
    else:
        logging.warning("Wide aspect ratio not found in config. Using original image dimensions.")

    output_filename = f"{image_path}_wide.png"
    img.save(output_filename)
    logging.info(f"Created start/end slide: {output_filename}")
    return output_filename

# Modularized: Create a video from slides
def create_video(subject, topics, config):
    # Ensure required directories exist
    ensure_directories(config)

    # Connect to DB and fetch questions
    conn = connect_to_db()
    questions = fetch_questions(conn, subject, topics)

    # Load resources (background image and fonts)
    background_image, font_question, font_options, font_answer = load_resources(config)

    # Generate slides for questions and answers
    slides, durations = generate_slides(questions, config, background_image, font_question, font_options, font_answer)

    # Create the video
    create_video_from_slides(slides, config["output_video"], durations, config.get("background_music"))

# Improved: Word wrapping function for better text formatting
def wrap_text(text, font, max_width, config):
    """Wrap text based on max width and return wrapped text"""
    wrap_width = config.get("text_wrap_width", 50)  # Default to 50 if not found in config
    wrapped_lines = []
    for line in text.split('\n'):
        wrapped_lines.extend(textwrap.wrap(line, width=wrap_width))  # Use the value from config
    return wrapped_lines

def create_slide(question_text, options_text, background_image, font_question, font_options, output_path, config, slide_type="question"):
    img = background_image.copy()

    # Resize image to wide aspect ratio
    if "wide_aspect_ratio" in config:
        img = img.resize((config["wide_aspect_ratio"]["width"], config["wide_aspect_ratio"]["height"]))  # Resize to wide aspect ratio
    else:
        logging.warning("Wide aspect ratio not found in config. Using original image dimensions.")

    draw = ImageDraw.Draw(img)

    # Position for question text
    x_question, y_question = 75, 100
    max_width_question = img.width - 100  # Leave padding for the text

    # Wrap and draw the question text
    wrapped_question = wrap_text(question_text, font_question, max_width_question, config)  # Pass config
    for line in wrapped_question:
        draw.text((x_question, y_question), line, font=font_question, fill=tuple(config['font_settings']['font_color_question']))
        line_height = font_question.getbbox(line)[3] - font_question.getbbox(line)[1]
        y_question += line_height + 20

    # Position for options text
    x_options, y_options = 75, y_question + 120  # Start below the question text
    max_width_options = img.width - 100  # Leave padding for the text

    # Wrap and draw the options text
    wrapped_options = wrap_text(options_text, font_options, max_width_options, config)  # Pass config
    for line in wrapped_options:
        draw.text((x_options, y_options), line, font=font_options, fill=tuple(config['font_settings']['font_color_options']))
        line_height = font_options.getbbox(line)[3] - font_options.getbbox(line)[1]
        y_options += line_height + 15

    # Save the slide as an image
    output_filename = f"{output_path}_{slide_type}.png"
    img.save(output_filename)
    logging.info(f"Created {slide_type} slide: {output_filename}")

    return output_filename

def create_video_from_slides(slides, output_video, durations, background_music=None, music_volume=0.2):
    logging.info("Starting video creation...")
    clips = []

    for slide, duration in zip(slides, durations):
        clip = ImageClip(slide).set_duration(duration)
        clips.append(clip)

    # Concatenate all slides to form the video
    video = concatenate_videoclips(clips, method="compose")

    # Total video duration
    video_duration = sum(durations)

    # Add background music in sequence if provided
    if background_music:
        if isinstance(background_music, list):
            # Concatenate music tracks to match the video duration
            music_clips = []
            total_music_duration = 0
            for music_file in background_music:
                music = AudioFileClip(music_file)
                music_clips.append(music)
                total_music_duration += music.duration

            # Concatenate all music clips together
            full_music = concatenate_audioclips(music_clips)

            # If the total music duration is less than the video duration, loop the music
            if total_music_duration < video_duration:
                full_music = afx.audio_loop(full_music, duration=video_duration)
            else:
                full_music = full_music.subclip(0, video_duration)
        else:
            # If background_music is a single file
            full_music = AudioFileClip(background_music)
            if full_music.duration < video_duration:
                full_music = afx.audio_loop(full_music, duration=video_duration)
            else:
                full_music = full_music.subclip(0, video_duration)

        # Apply a 3-second fade-out effect towards the end of the music
        full_music = full_music.audio_fadeout(3)

        # Adjust the volume of the music
        full_music = full_music.volumex(music_volume)
        video = video.set_audio(full_music)

    # Save the video
    video.write_videofile(output_video, fps=24)

    logging.info(f"Video saved as: {output_video}")


# Main function to read config and generate the MP4
def generate_video(config_file):
    start_time = time.time()
    logging.info("Starting video generation...")

    with open(config_file, 'r') as f:
        config = json.load(f)

    subject = config["subject"]
    topics = config["topics"]

    create_video(subject, topics, config)

    end_time = time.time()
    total_time = end_time - start_time
    logging.info(f"Total time taken: {total_time:.2f} seconds")

if __name__ == "__main__":
    generate_video("config/03_config_video_generation.json")
