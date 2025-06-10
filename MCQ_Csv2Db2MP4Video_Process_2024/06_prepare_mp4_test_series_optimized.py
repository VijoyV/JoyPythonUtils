import json
import logging
import os
import random
import sqlite3
import textwrap
import time
import csv
from multiprocessing import Pool, cpu_count
from datetime import datetime
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from moviepy.audio.fx.volumex import volumex
from moviepy.editor import ImageSequenceClip, AudioFileClip, afx

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Word wrapping function
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


# Fetch all questions for the given topics from the database
def fetch_all_questions(conn, subject, topics, used_question_ids):
    cursor = conn.cursor()
    all_questions = []
    for topic_info in topics:
        topic_name = topic_info['topic_name']
        try:
            if used_question_ids:
                # When there are used_question_ids, include them in the query
                query = '''
                    SELECT question_id, question_text, question_options, correct_answer, topic
                    FROM question_bank
                    WHERE subject = ? AND topic = ? AND question_id NOT IN ({})

                '''.format(','.join('?' * len(used_question_ids)))
                params = (subject, topic_name) + tuple(used_question_ids)
            else:
                # When no used_question_ids, omit the NOT IN clause
                query = '''
                    SELECT question_id, question_text, question_options, correct_answer, topic
                    FROM question_bank
                    WHERE subject = ? AND topic = ?

                '''
                params = (subject, topic_name)

            cursor.execute(query, params)
            topic_questions = cursor.fetchall()
            all_questions.extend(topic_questions)
            logging.info(f"Fetched {len(topic_questions)} questions for topic {topic_name}.")
        except sqlite3.Error as e:
            logging.error(f"Error fetching questions for topic {topic_name}: {e}")
            raise
    return all_questions


# Filter out lengthy questions and options
def filter_out_lengthy_questions(questions, question_word_limit=50, option_word_limit=50, combined_word_limit=80):
    filtered_questions = []

    for question in questions:
        question_text = question[1]  # Assuming question[1] is the question_text
        options_text = question[2]  # Assuming question[2] is the question_options

        # Word count for the question
        question_word_count = len(question_text.split())

        # Word count for the options (split by the pipe '|' delimiter if multiple options are present)
        options_word_count = sum(len(opt.split()) for opt in options_text.split('|'))

        # Combined word count
        combined_word_count = question_word_count + options_word_count

        # Apply the filtering conditions
        if (question_word_count <= question_word_limit and
                options_word_count <= option_word_limit and
                combined_word_count <= combined_word_limit):
            filtered_questions.append(question)
        else:
            logging.info(f"Filtered out question ID {question[0]} due to word limits. "
                         f"Question words: {question_word_count}, Options words: {options_word_count}, "
                         f"Combined words: {combined_word_count}")

    return filtered_questions


# Fetch and filter questions from the database
def fetch_and_filter_questions(conn, subject, topics, used_question_ids):
    all_questions = fetch_all_questions(conn, subject, topics, used_question_ids)

    # Apply the filter to remove lengthy questions or options
    filtered_questions = filter_out_lengthy_questions(all_questions)

    logging.info(
        f"Filtered {len(all_questions) - len(filtered_questions)} out of {len(all_questions)} questions based on word limits.")

    return filtered_questions


# Filter and select questions for the test
def select_random_questions(filtered_questions, topics):
    selected_questions = []
    for topic_info in topics:
        topic_name = topic_info['topic_name']
        num_questions_per_topic = topic_info['num_questions_per_topic']
        topic_questions = [q for q in filtered_questions if q[4] == topic_name]
        if len(topic_questions) < num_questions_per_topic:
            logging.warning(f"Not enough questions for topic {topic_name}. Selecting all available.")
            selected_questions.extend(topic_questions)
        else:
            random_selection = random.sample(topic_questions, num_questions_per_topic)
            selected_questions.extend(random_selection)
        logging.info(f"Randomly selected {len(random_selection)} questions for topic {topic_name}.")
    return selected_questions


# Insert selected questions into test_series.db and also log question_no and answer
def log_selected_questions(test_name, selected_questions, db_name="test_series.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Ensure the test_questions table is created with correct schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_questions (
            test_name TEXT,
            topic_name TEXT,
            question_id TEXT,  -- Use TEXT type for UUID
            question_no INTEGER,
            answer TEXT,
            date_created TEXT
        )
    ''')

    date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for question_no, question in enumerate(selected_questions, start=1):
        cursor.execute('''
            INSERT INTO test_questions (test_name, topic_name, question_id, question_no, answer, date_created)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (test_name, question[4], question[0], question_no, question[3], date_created))

    conn.commit()
    conn.close()


# Fetch previously used question IDs from test_series.db with table existence and empty table handling
def fetch_used_question_ids(db_name="test_series.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        # Check if the table exists and fetch the question IDs
        cursor.execute('''
            SELECT question_id 
            FROM test_questions
        ''')
        used_question_ids = [row[0] for row in cursor.fetchall()]

        if not used_question_ids:
            logging.info("No used question IDs found in test_questions table.")
            used_question_ids = []

    except sqlite3.OperationalError as e:
        # Handle case where the table does not exist
        logging.warning(f"Table 'test_questions' does not exist: {e}. Proceeding with an empty list.")
        used_question_ids = []

    conn.close()
    return used_question_ids


# Parallel image resizing function
def resize_image(slide, target_size):
    img = Image.open(slide)
    original_size = img.size
    if original_size != target_size:
        img_resized = img.resize(target_size)
        img_resized = img_resized.convert("RGB")  # Convert to RGB to remove alpha
        resized_slide_path = slide.replace(".png", "_resized.png")
        img_resized.save(resized_slide_path, format="PNG")
        return resized_slide_path
    return slide  # Return original slide if no resizing needed


# Optimize resizing using multiprocessing
def resize_images_to_same_size(slides, target_size):
    logging.info(f"Resizing {len(slides)} slides using {cpu_count()} CPUs")
    with Pool(cpu_count()) as pool:
        resized_slides = pool.starmap(resize_image, [(slide, target_size) for slide in slides])
    return resized_slides


# Create question slide with proper size from config
def create_question_slide(question_content, options_content, background_image, font_question, font_options, output_path,
                          config):
    # Resize the background image to the wide aspect ratio
    img = background_image.copy()
    img = img.resize((config["wide_aspect_ratio"]["width"], config["wide_aspect_ratio"]["height"]))
    draw = ImageDraw.Draw(img)

    # Position for question text
    x_question, y_question = 120, 80
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


# Generate slides for the test ensuring all use the wide aspect ratio
def generate_slides(questions, config):
    slides = []
    durations = []
    pool = Pool(cpu_count())  # Use multiple processors

    # Load fonts from config
    font_question = ImageFont.truetype(config["font_path_question"], config["font_settings"]["font_size_question"])
    font_options = ImageFont.truetype(config["font_path_options"], config["font_settings"]["font_size_options"])

    # 1. Add the start slide
    start_slide_image = config["start_slide"]
    start_slide_output = f"{config['working_slide_path']}/start_slide.png"
    start_img = Image.open(start_slide_image).resize(
        (config["wide_aspect_ratio"]["width"], config["wide_aspect_ratio"]["height"]))
    start_img.save(start_slide_output)
    slides.append(start_slide_output)
    durations.append(config["slide_durations"]["start_slide"])

    # 2. Create question slides
    for idx, (question_id, question_text, question_options, _, topic) in enumerate(questions):
        background_image = Image.open(config["background_image"])
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

        logging.info(f"Slide for question {idx + 1} created")
        durations.append(config["slide_durations"]["question_slide"])

    pool.close()
    pool.join()

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


# Create video from slides and add continuous audio, ensuring all slides are resized correctly
def create_video_from_slides(slides, output_video, durations, audio_file, config):
    logging.info("Starting video creation...")

    # Ensure all images have the same size based on the wide aspect ratio
    target_size = (config["wide_aspect_ratio"]["width"], config["wide_aspect_ratio"]["height"])
    resized_slides = resize_images_to_same_size(slides, target_size)

    # Durations are in seconds (no conversion needed)
    image_clip = ImageSequenceClip(resized_slides, durations=durations)

    # Calculate the total duration of the video
    total_duration = sum(durations)

    # Load the audio file
    audio = AudioFileClip(audio_file)

    # Adjust volume (reduce to 510% of the original volume)
    audio = volumex(audio, 0.1)  # Control volume directly with volumex

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

    # Write the video file with optimized encoding
    video.write_videofile(
        output_video,
        fps=12,  # Low FPS is fine for static slides
        codec='libx264',
        preset='veryfast',  # A slight trade-off between speed and quality
        bitrate="5000k",  # Adjust this based on desired output quality
        audio_codec='aac'  # Efficient audio compression
    )


# Generate CSV for the selected questions (question_id, question_no, answer)
def generate_csv_report(test_name, db_name="test_series.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Check if the test_questions table exists before proceeding
    cursor.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='test_questions'
    ''')
    table_exists = cursor.fetchone()

    if table_exists:
        cursor.execute('''
            SELECT question_id, question_no, answer
            FROM test_questions
            WHERE test_name = ?
        ''', (test_name,))
        rows = cursor.fetchall()

        csv_file = f"{test_name}_question_report.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow(['question_id', 'question_no', 'answer'])
            writer.writerows(rows)

        logging.info(f"CSV report generated: {csv_file}")
    else:
        logging.warning("The 'test_questions' table does not exist, skipping CSV generation.")

    conn.close()


# Main function to read config and generate the MP4
def generate_video(config_file):
    start_time = time.time()
    logging.info("Starting video generation...")

    with open(config_file, 'r') as f:
        config = json.load(f)

    subject = config["subject"]
    topics = config["topics"]
    test_name = config["test_name"]
    audio_file = config["background_audio"]

    ensure_directory_exists(config['working_slide_path'])

    # Fetch previously used questions to avoid duplicates
    used_question_ids = fetch_used_question_ids()

    # Connect to questions.db and fetch and filter questions
    conn = connect_to_db()
    filtered_questions = fetch_and_filter_questions(conn, subject, topics, used_question_ids)

    # Select random questions as per config
    selected_questions = select_random_questions(filtered_questions, topics)

    # Log selected questions into test_series.db
    log_selected_questions(test_name, selected_questions)

    # Generate slides for selected questions
    slides, durations = generate_slides(selected_questions, config)

    # Create the video with continuous audio
    create_video_from_slides(slides, config["output_video"], durations, audio_file, config)

    # Generate CSV report for the selected questions
    generate_csv_report(test_name)

    end_time = time.time()
    total_time = end_time - start_time
    logging.info(f"Total time taken: {total_time:.2f} seconds")


if __name__ == "__main__":
    generate_video("config/06_config_4_test_series_generation.json")
