import os
import sqlite3
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, concatenate_videoclips
import textwrap
import json
import logging
import time
import random


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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


# Step 1: Fetch all questions from the DB
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


# Step 2: Filter questions based on question_text and question_options length
def filter_questions(questions):
    filtered_questions = []

    for question in questions:
        question_id, question_text, question_options, correct_answer, topic = question

        # Check if question text and answer lengths meet the criteria
        if len(question_text.split()) <= 30 and len(' '.join(question_options.split('|')).split()) <= 24:
            filtered_questions.append(question)
        else:
            logging.info(f"Filtered out question {question_id} for exceeding length criteria.")

    logging.info(f"Filtered {len(filtered_questions)} questions that met the length criteria.")
    return filtered_questions


# Step 3: Randomly select questions for each topic
def select_random_questions(filtered_questions, topics):
    selected_questions = []

    for topic_info in topics:
        topic_name = topic_info['topic_name']
        num_questions_per_topic = topic_info['num_questions_per_topic']

        # Filter questions by topic
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


# Step 4: Remove duplicates based on question_id
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
    return unique_questions


# Fetch, filter, select, and remove duplicates
def fetch_and_select_questions(conn, subject, topics):
    # Step 1: Extract all questions from the DB
    all_questions = fetch_all_questions(conn, subject, topics)

    # Step 2: Filter questions based on the length criteria
    filtered_questions = filter_questions(all_questions)

    # Step 3: Randomly select questions for each topic
    selected_questions = select_random_questions(filtered_questions, topics)

    # Step 4: Remove duplicates based on question_id
    unique_questions = remove_duplicates(selected_questions)

    return unique_questions


# Ensure directories exist
def ensure_directories(config):
    ensure_directory_exists(config['working_slide_path'])
    ensure_directory_exists(os.path.dirname(config["output_video"]))


# Caching image and font loading
def load_resources(config):
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


# Word wrapping function for better text formatting
def wrap_text(text, font, max_width, config):
    wrap_width = config.get("text_wrap_width", 50)
    wrapped_lines = []
    for line in text.split('\n'):
        wrapped_lines.extend(textwrap.wrap(line, width=wrap_width))
    return wrapped_lines

# Create individual slide (either question or answer)
def create_slide(question_content, options_content, background_image, font_question, font_options, output_path, config, slide_type="question"):
    img = background_image.copy()

    # Resize image to wide aspect ratio
    if "wide_aspect_ratio" in config:
        img = img.resize((config["wide_aspect_ratio"]["width"], config["wide_aspect_ratio"]["height"]))
    else:
        logging.warning("Wide aspect ratio not found in config. Using original image dimensions.")

    draw = ImageDraw.Draw(img)

    # Position for question text
    x_question, y_question = 75, 100
    max_width_question = img.width - 100

    # Wrap and draw the question text
    wrapped_question = wrap_text(question_content, font_question, max_width_question, config)
    for line in wrapped_question:
        draw.text((x_question, y_question), line, font=font_question, fill=tuple(config['font_settings']['font_color_question']))
        # Use getbbox to get the height of the line
        bbox = draw.textbbox((x_question, y_question), line, font=font_question)
        line_height = bbox[3] - bbox[1]  # The height is bottom minus top of the bounding box
        y_question += line_height + 20

    # If options are present, draw the options
    if options_content:
        x_options, y_options = 75, y_question + 120
        max_width_options = img.width - 100

        # Wrap and draw the options text
        wrapped_options = wrap_text(options_content, font_options, max_width_options, config)
        for line in wrapped_options:
            draw.text((x_options, y_options), line, font=font_options, fill=tuple(config['font_settings']['font_color_options']))
            bbox = draw.textbbox((x_options, y_options), line, font=font_options)
            line_height = bbox[3] - bbox[1]
            y_options += line_height + 15

    # Save the slide as an image
    output_filename = f"{output_path}_{slide_type}.png"
    img.save(output_filename)
    logging.info(f"Created {slide_type} slide: {output_filename}")

    return output_filename

# Create and save slides for questions and answers
def generate_slides(questions, config, background_image, font_question, font_options, font_answer):
    slides = []
    durations = []

    # Add start slide
    slides.append(create_slide_for_start_or_end(config["start_slide"], config))
    durations.append(config["slide_durations"]["start_slide"])

    # Create question and answer slides
    for idx, (question_id, question_text, question_options, correct_answer, topic) in enumerate(questions):
        logging.info(f"Processing question {idx + 1}/{len(questions)} for topic {topic}")

        # Format question text and options for the question slide
        options_list = question_options.replace('|', '\n').splitlines()
        formatted_options = "\n".join([f"{option.strip()}" for i, option in enumerate(options_list)])
        question_content = f"Q - {idx + 1}: {question_text}"
        options_content = f"{formatted_options}"

        # Create question slide
        question_slide = create_slide(
            question_content=question_content,
            options_content=options_content,
            background_image=background_image,
            font_question=font_question,
            font_options=font_options,
            output_path=f"{config['working_slide_path']}/slide_{idx + 1}_question",
            config=config,
            slide_type="question"
        )

        # Create answer slide (only the answer)
        answer_slide = create_slide(
            question_content=correct_answer,
            options_content="",
            background_image=background_image,
            font_question=font_answer,  # Using font_answer for the answer text
            font_options=font_answer,  # No options on this slide, but font_answer will be used
            output_path=f"{config['working_slide_path']}/slide_{idx + 1}_answer",
            config=config,
            slide_type="answer"
        )

        # Add the slides to the list
        slides.extend([question_slide, answer_slide])
        durations.extend([config["slide_durations"]["question_slide"], config["slide_durations"]["answer_slide"]])

    # Add end slide
    slides.append(create_slide_for_start_or_end(config["end_slide"], config))
    durations.append(config["slide_durations"]["end_slide"])

    return slides, durations


# Create start or end slide in wide aspect ratio
def create_slide_for_start_or_end(image_path, config):
    img = Image.open(image_path)

    # Apply wide aspect ratio if specified in config
    if "wide_aspect_ratio" in config:
        img = img.resize((config["wide_aspect_ratio"]["width"], config["wide_aspect_ratio"]["height"]))
    else:
        logging.warning("Wide aspect ratio not found in config. Using original image dimensions.")

    output_filename = f"{image_path}_wide.png"
    img.save(output_filename)
    logging.info(f"Created start/end slide: {output_filename}")
    return output_filename


# Create video from slides
def create_video_from_slides(slides, output_video, durations):
    logging.info("Starting video creation...")

    # Create all clips in one pass with reduced frame rate (e.g., 12 FPS for static slides)
    clips = [ImageClip(slide).set_duration(duration).set_fps(12) for slide, duration in zip(slides, durations)]

    # Concatenate all slides into a single video
    video = concatenate_videoclips(clips, method="compose")

    # Save the video with reduced FPS (12 or another value that works well with your slides)
    video.write_videofile(output_video, fps=12, codec='libx264', preset='fast')
    logging.info(f"Video saved as: {output_video}")


# Main function to read config and generate the MP4
def generate_video(config_file):
    start_time = time.time()
    logging.info("Starting video generation...")

    with open(config_file, 'r') as f:
        config = json.load(f)

    subject = config["subject"]
    topics = config["topics"]

    # Ensure required directories exist
    ensure_directories(config)

    # Connect to DB and fetch questions
    conn = connect_to_db()
    questions = fetch_and_select_questions(conn, subject, topics)

    # Load resources (background image and fonts)
    background_image, font_question, font_options, font_answer = load_resources(config)

    # Generate slides for questions and answers
    slides, durations = generate_slides(questions, config, background_image, font_question, font_options, font_answer)

    # Create the video
    create_video_from_slides(slides, config["output_video"], durations)

    end_time = time.time()
    total_time = end_time - start_time
    logging.info(f"Total time taken: {total_time:.2f} seconds")


if __name__ == "__main__":
    generate_video("config/04_config_video_generation.json")

"""
The provided Python code and config.json file outline a process for generating a video from a set of quiz questions, answers, and options drawn from a database. Below is an analysis of the key components and how the configuration file supports the process:

# Code Analysis:
## Logging and Setup:

Logging is configured for the entire process, which helps in tracking progress and errors.
Functions like ensure_directory_exists and connect_to_db are used to ensure necessary directories and database connections are set up properly.

## Question Handling:

The code fetches questions from a SQLite database (fetch_all_questions) based on the subject and topics defined in the configuration file.
It then filters out questions that are too long in terms of the number of words in both the question text and options (filter_questions).
The filtered questions are randomly sampled per topic (select_random_questions) and duplicates are removed (remove_duplicates).

## Slide Creation:

The create_slide function generates individual image slides for both questions and answers. It uses PIL to draw text on images, wrapping the text to fit within a specified width (wrap_text).
Background images and fonts are loaded via load_resources, with fallback to default fonts if any errors occur.
Slides for questions and answers are created separately, with question slides containing the question text and options, while answer slides contain only the correct answer.
Start and end slides are created by resizing provided images to the specified aspect ratio (create_slide_for_start_or_end).

## Video Creation:

Once the slides are created, create_video_from_slides generates a video from these slides using the moviepy library, setting a static FPS (12 frames per second) to optimize for slideshows.
The video is saved with a specified output file path, using libx264 codec and fast preset to speed up the encoding.

## Configuration File (config.json):

The subject and topics specify what questions should be fetched from the database. Each topic is associated with a specified number of questions (num_questions_per_topic).

### Design Settings:
background_image, start_slide, and end_slide define images used as the background or start/end slides.
The wide_aspect_ratio settings resize images to 1920x1080 (HD resolution).

### Font Settings:
Fonts for questions, options, and answers are defined with their paths, sizes, and colors (font_settings).
If the font files are missing, the code uses default fonts.

### Timing:
slide_durations defines how long each type of slide (start, question, answer, end) stays on screen.

### Text Wrapping:
text_wrap_width controls the number of characters per line, affecting how the text is wrapped on the slides.

### Output Settings:
output_video sets the name and location of the final MP4 file that will be generated.

## Strengths and Potential Optimizations:

### Modular Structure: 
The code is modular, with functions clearly responsible for distinct tasks, such as fetching questions, generating slides, and creating the video.

### Error Handling and Logging: 
The code handles database and file operations carefully, with extensive logging to track errors and process completion.

### Flexibility: 
By reading the configuration from a JSON file, the user can easily adjust topics, question counts, fonts, colors, and durations without altering the core code.

### Performance: 
While the code efficiently filters, selects, and processes questions, creating individual slides and videos can be time-consuming for large datasets (e.g., 200+ questions). The use of PIL for drawing and moviepy for video creation ensures quality, but performance could be improved by parallelizing certain operations or reducing image processing overhead.

## Suggestions for Further Optimization:

### Parallel Processing: 
If video generation takes too long, consider processing slides in parallel or using caching techniques for slides that do not change.

### Memory Efficiency: 
If handling large amounts of images, ensure that images are released from memory when no longer needed to avoid memory bloat.

### Pre-generated Templates: 
For static elements like background images or common fonts, you could pre-generate slide templates and avoid redundant operations during each question’s processing.

"""
