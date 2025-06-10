import json
import sqlite3
import uuid
import os


# Function to read config.json
def read_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)


# Function to create or connect to the SQLite database
def connect_to_db(db_name="questions.db"):
    conn = sqlite3.connect(db_name)
    return conn


# Function to create the question_bank table if it doesn't exist
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_bank (
            question_id TEXT PRIMARY KEY,
            question_text TEXT,
            question_options TEXT,
            correct_answer TEXT,
            subject TEXT,
            topic TEXT,
            text_language TEXT,
            created_by TEXT,
            created_updated_on TEXT
        )
    ''')
    conn.commit()


# Function to process file content line by line and extract question, options, and answer
def extract_qa(file_content):
    questions = []
    question_text = ""
    options = []
    answer = ""
    inside_question = False

    for line in file_content:
        line = line.strip()

        # Detect Question Line
        if line.startswith("Question:"):
            if inside_question and question_text and options and answer:
                # Append the previous question before starting a new one
                questions.append((question_text, " | ".join(options), answer))
            # Start a new question
            question_text = line[len("Question:"):].strip()
            options = []
            answer = ""
            inside_question = True

        # Detect Options Line
        elif line.startswith("Options:"):
            continue  # Skip the "Options:" header line

        elif line.startswith("A)") or line.startswith("B)") or line.startswith("C)") or line.startswith("D)"):
            options.append(line.strip())

        # Detect Answer Line
        elif line.startswith("Answer:"):
            answer = line[len("Answer:"):].strip()

    # Append the last question after file ends
    if inside_question and question_text and options and answer:
        questions.append((question_text, " | ".join(options), answer))

    return questions


# Function to insert questions into the database
def insert_into_db(conn, questions, config):
    cursor = conn.cursor()

    for question, options, answer in questions:
        question_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO question_bank (
                question_id, question_text, question_options, correct_answer, 
                subject, topic, text_language, created_by, created_updated_on
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            question_id, question, options, answer,
            config['subject'], config['topic'], config['text_language'],
            config['created_by'], config['created_updated_on']
        ))

    conn.commit()


# Main function to process the files
def process_files(config):
    conn = connect_to_db()
    create_table(conn)

    for file_info in config['files']:
        file_path = file_info['file_path']
        subject = file_info['subject']
        topic = file_info['topic']

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    file_content = f.readlines()
                    questions = extract_qa(file_content)
                    # Insert questions with specific subject and topic from the file
                    insert_into_db(conn, questions, {
                        'subject': subject,
                        'topic': topic,
                        'text_language': config['text_language'],
                        'created_by': config['created_by'],
                        'created_updated_on': config['created_updated_on']
                    })
                print(f"questions from chapter {file_path} = {len(questions)}")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
        else:
            print(f"File {file_path} does not exist.")

    conn.close()


# Entry point
if __name__ == "__main__":
    config = read_config("config/01_config_4_db_load.json")
    process_files(config)
    print("Questions inserted successfully.")
