import json
import logging
import os
import random
import sqlite3
import textwrap
import time
from multiprocessing import Pool, cpu_count

from PIL import Image, ImageDraw, ImageFont
from moviepy.audio.fx.volumex import volumex
from moviepy.editor import ImageSequenceClip, AudioFileClip, afx

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Word wrapping function for better text formatting
def wrap_text(text, font, max_width, config):
    wrap_width = config.get("text_wrap_width", 50)
    wrapped_lines = []
    for line in text.split('\n'):
        wrapped_lines.extend(textwrap.wrap(line, width=wrap_width))
    return wrapped_lines


# Ensure that required directories exist
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")
    else:
        logging.info(f"Directory already exists: {directory}")


# Connect to SQLite database with error handling
def connect_to_db(db_name="questions.db"):
    try:
        conn = sqlite3.connect(db_name)
        logging.info(f"Successfully connected to database: {db_name}")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection failed: {e}")
        raise


# Fetch all questions from the DB
def fetch_all_questions(conn, subject, topics):
    cursor = conn.cursor()
    all_questions = []
    for topic_info in topics:
        topic_name = topic_info['topic_name']
        try:
            query = '''
                SELECT question_id, question_text, question_options, correct_answer, topic
                FROM question_bank
                WHERE subject = ? AND topic = ?
                ORDER BY subject, topic, question_id
            '''
            cursor.execute(query, (subject, topic_name))
            topic_questions = cursor.fetchall()
            all_questions.extend(topic_questions)
            logging.info(f"Fetched {len(topic_questions)} questions for topic {topic_name}.")
        except sqlite3.Error as e:
            logging.error(f"Error fetching questions for topic {topic_name}: {e}")
            raise
    logging.info(f"Total questions fetched: {len(all_questions)}.")
    return all_questions


# Filter questions based on question_text and question_options length
def filter_questions(questions):
    filtered_questions = []
    for question in questions:
        question_id, question_text, question_options, correct_answer, topic = question
        question_words = len(question_text.split())
        options_words = len(' '.join(question_options.split('|')).split())
        total_words = question_words + options_words
        logging.info(f"Filter criteria: "
                     f"question_words = {question_words} [<= 45] "
                     f"options_words = {options_words} [<= 35] "
                     f"total_words = {total_words} [<=70] ")
        if question_words <= 45 and options_words <= 35 and total_words <= 70:
            filtered_questions.append(question)
            logging.info(f"Filtered IN question {question_id} for clearing length criteria")
        else:
            logging.info(f"Filtered OUT question {question_id} for exceeding length criteria.")
    logging.info(f"Filtered {len(filtered_questions)} questions that met the length criteria.")
    return filtered_questions


# Randomly select questions for each topic
def select_random_questions(filtered_questions, topics):
    selected_questions = []
    for topic_info in topics:
        topic_name = topic_info['topic_name']
        num_questions_per_topic = topic_info['num_questions_per_topic']
        topic_questions = [q for q in filtered_questions if q[4] == topic_name]
        if len(topic_questions) < num_questions_per_topic:
            logging.warning(
                f"Not enough questions for topic {topic_name}. Selecting all available {len(topic_questions)} questions.")
            selected_questions.extend(topic_questions)
        else:
            random_selection = random.sample(topic_questions, num_questions_per_topic)
            selected_questions.extend(random_selection)
        logging.info(f"Randomly selected {len(random_selection)} questions for topic {topic_name}.")
    return selected_questions


# Remove duplicates based on question_id and sort by question_id
def remove_duplicates(selected_questions):
    unique_questions = []
    seen_question_ids = set()
    for question in selected_questions:
        question_id = question[0]
        if question_id not in seen_question_ids:
            unique_questions.append(question)
            seen_question_ids.add(question_id)
        else:
            logging.info(f"Duplicate question found and skipped: {question_id}")

    logging.info(f"Total unique questions after removing duplicates: {len(unique_questions)}.")

    # Sort unique questions by topic (assumed to be at index 4) and then by question_id (index 0)
    sorted_unique_questions = sorted(unique_questions, key=lambda x: (x[4], x[0]))
    return sorted_unique_questions


# Fetch, filter, select, and remove duplicates
def fetch_and_select_questions(conn, subject, topics):
    all_questions = fetch_all_questions(conn, subject, topics)
    filtered_questions = filter_questions(all_questions)
    selected_questions = select_random_questions(filtered_questions, topics)
    unique_questions = remove_duplicates(selected_questions)
    return unique_questions


# Ensure directories exist
def ensure_directories(config):
    ensure_directory_exists(config['working_slide_path'])
    ensure_directory_exists(os.path.dirname(config["output_video"]))


# Load resources for each topic
def load_resources_for_topic(topic, config):
    try:
        background_image = Image.open(config["topic_background_images"][topic])
        logging.info(f"Loaded background image for topic: {topic}")
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


def create_question_slide(question_content, options_content, background_image, font_question, font_options, output_path,
                          config):
    img = background_image.copy()
    if "wide_aspect_ratio" in config:
        img = img.resize((config["wide_aspect_ratio"]["width"], config["wide_aspect_ratio"]["height"]))
    draw = ImageDraw.Draw(img)

    # Position for question text
    x_question, y_question = 120, 150
    wrapped_question = wrap_text(question_content, font_question, config.get("text_wrap_width", 50), config)
    for line in wrapped_question:
        draw.text((x_question, y_question), line, font=font_question,
                  fill=tuple(config['font_settings']['font_color_question']))
        y_question += 80

    # Options
    if options_content:
        x_options, y_options = 120, y_question + 120
        wrapped_options = wrap_text(options_content, font_options, config.get("text_wrap_width", 50), config)
        for line in wrapped_options:
            draw.text((x_options, y_options), line, font=font_options,
                      fill=tuple(config['font_settings']['font_color_options']))
            y_options += 90

    # Save slide
    output_filename = f"{output_path}_question.png"
    img.save(output_filename)
    return output_filename


def create_answer_slide(answer_content, background_image, font_answer, output_path, config):
    img = background_image.copy()
    if "wide_aspect_ratio" in config:
        img = img.resize((config["wide_aspect_ratio"]["width"], config["wide_aspect_ratio"]["height"]))
    draw = ImageDraw.Draw(img)

    # Position for answer text
    x_answer, y_answer = 120, 480
    wrapped_answer = wrap_text(answer_content, font_answer, config.get("text_wrap_width", 50), config)
    for line in wrapped_answer:
        draw.text((x_answer, y_answer), line, font=font_answer,
                  fill=tuple(config['font_settings']['font_color_answer']))
        y_answer += 80

    # Save slide
    output_filename = f"{output_path}_answer.png"
    img.save(output_filename)
    return output_filename


# Create and save slides for questions and answers
def generate_slides(questions, config, topic_backgrounds):
    slides = []
    durations = []
    pool = Pool(cpu_count())  # Use multiple processors

    # Load fonts from config
    font_question = ImageFont.truetype(config["font_path_question"], config["font_settings"]["font_size_question"])
    font_options = ImageFont.truetype(config["font_path_options"], config["font_settings"]["font_size_options"])
    font_answer = ImageFont.truetype(config["font_path_answer"], config["font_settings"]["font_size_answer"])

    # 1. Add the start slide
    start_slide_image = config["start_slide"]
    start_slide_output = f"{config['working_slide_path']}/start_slide.png"
    start_img = Image.open(start_slide_image).resize(
        (config["wide_aspect_ratio"]["width"], config["wide_aspect_ratio"]["height"]))
    start_img.save(start_slide_output)
    slides.append(start_slide_output)
    durations.append(config["slide_durations"]["start_slide"])

    logging.info("Start slide created")

    # 2. Create question and answer slides
    for idx, (question_id, question_text, question_options, correct_answer, topic) in enumerate(questions):
        background_image = topic_backgrounds[topic]
        question_content = f"Q - {idx + 1}: {question_text}"
        options_content = '\n'.join([opt.strip() for opt in question_options.replace('|', '\n').splitlines()])

        # Create question slide
        question_slide_output = f"{config['working_slide_path']}/slide_{idx + 1}_question.png"
        slides.append(
            pool.apply_async(create_question_slide, (
                question_content,
                options_content,
                background_image,
                font_question,
                font_options,
                question_slide_output,
                config
            )).get()
        )
        logging.info(f"Slide for question and options {idx + 1} created")

        # Create answer slide
        answer_slide_output = f"{config['working_slide_path']}/slide_{idx + 1}_answer.png"
        slides.append(
            pool.apply_async(create_answer_slide, (
                correct_answer,
                background_image,
                font_answer,
                answer_slide_output,
                config
            )).get()
        )

        logging.info(f"Slide for answer {idx + 1} created")

        durations.extend([config["slide_durations"]["question_slide"], config["slide_durations"]["answer_slide"]])

    pool.close()
    pool.join()

    logging.info(f"All question, options and answer slides created")

    # 3. Add the end slide
    end_slide_image = config["end_slide"]
    end_slide_output = f"{config['working_slide_path']}/end_slide.png"
    end_img = Image.open(end_slide_image).resize(
        (config["wide_aspect_ratio"]["width"], config["wide_aspect_ratio"]["height"]))
    end_img.save(end_slide_output)
    slides.append(end_slide_output)
    durations.append(config["slide_durations"]["end_slide"])

    logging.info("End slide created")

    return slides, durations


# Create video from slides and add continuous audio
def create_video_from_slides(slides, output_video, durations, audio_file, config):
    logging.info("Starting video creation...")

    # Durations are in seconds (no conversion needed)
    image_clip = ImageSequenceClip(slides, durations=durations)

    # Calculate the total duration of the video
    total_duration = sum(durations)

    # Load the audio file
    audio = AudioFileClip(audio_file)

    # Adjust volume (reduce to 50% of the original volume)
    audio = volumex(audio, 0.3)  # Control volume directly with volumex

    # If the audio is shorter than the video, loop the audio
    if audio.duration < total_duration:
        logging.info(f"Audio is shorter than the video. Looping audio to fit {total_duration} seconds.")
        audio = afx.audio_loop(audio, duration=total_duration)

    # If the audio is longer than the video, trim the audio
    elif audio.duration > total_duration:
        logging.info(f"Audio is longer than the video. Trimming audio to {total_duration} seconds.")
        audio = audio.subclip(0, total_duration)

    # Apply fade-in and fade-out to the audio
    faded_audio = audio.audio_fadein(2).audio_fadeout(2)

    # Set the audio to the video
    video = image_clip.set_audio(faded_audio)

    # Write the video file with faster encoding settings
    video.write_videofile(
        output_video,
        fps=12,  # Low FPS is fine for static slides
        codec='libx264',
        preset='ultrafast',  # Use ultrafast preset to speed up encoding
        audio_codec='aac'  # Use aac for better audio compression
    )


# Main function to read config and generate the MP4
def generate_video(config_file):
    start_time = time.time()
    logging.info("Starting video generation...")

    with open(config_file, 'r') as f:
        config = json.load(f)

    subject = config["subject"]
    topics = config["topics"]
    audio_file = config["background_audio"]

    ensure_directories(config)

    conn = connect_to_db()
    questions = fetch_and_select_questions(conn, subject, topics)

    # Load different background images for each topic
    topic_backgrounds = {topic_info["topic_name"]: load_resources_for_topic(topic_info["topic_name"], config)[0] for
                         topic_info in topics}

    slides, durations = generate_slides(questions, config, topic_backgrounds)

    # # Create the video with continuous audio
    create_video_from_slides(slides, config["output_video"], durations, audio_file, config)

    end_time = time.time()
    total_time = end_time - start_time
    logging.info(f"Total time taken: {total_time:.2f} seconds")


if __name__ == "__main__":
    generate_video("config/05_config_video_generation-sirach.json")
