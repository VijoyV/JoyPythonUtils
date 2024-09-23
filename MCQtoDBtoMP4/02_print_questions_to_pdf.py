import sqlite3
import json
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


# Function to read the configuration from config.json
def read_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)


# Function to connect to the SQLite database
def connect_to_db(db_name="questions.db"):
    conn = sqlite3.connect(db_name)
    return conn


# Function to fetch questions from the database by subject and topic
def fetch_questions(conn, subject, topic):
    cursor = conn.cursor()
    query = '''
        SELECT question_text, question_options, correct_answer
        FROM question_bank
        WHERE subject = ? AND topic = ?
        ORDER BY subject, topic, question_id
    '''
    cursor.execute(query, (subject, topic))
    return cursor.fetchall()


# Function to create a PDF with questions and answers
def create_pdf(filename, subject, topics, config):
    # Load the page configuration
    font_name = config["page_config"]["font_name"]
    font_size = config["page_config"]["font_size"]
    lines_per_page = config["page_config"]["lines_per_page"]
    wrap_width = 76  # Approximate number of characters per line for wrapping

    conn = connect_to_db()

    # Initialize PDF canvas
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Set font for title and content
    c.setFont(font_name, font_size)

    # Margins and starting y-position
    margin_x = inch
    margin_y = inch
    text_width = width - 2 * margin_x  # Available width for text
    y_position = height - margin_y

    # Serial number for questions
    def reset_serial_number():
        return 1

    def add_page(topic):
        nonlocal y_position
        c.showPage()
        y_position = height - margin_y
        c.setFont(font_name, font_size)
        draw_footer(topic)

    def draw_footer(topic):
        # Add footer with topic name and page number
        footer_text = f"Topic: {topic}"
        page_number_text = f"Page {c.getPageNumber()}"
        c.setFont(font_name, font_size - 2)
        c.drawString(margin_x, margin_y - 10, footer_text)
        c.drawRightString(width - margin_x, margin_y - 10, page_number_text)

    def add_heading(subject, topic):
        nonlocal y_position
        if y_position - 2 * font_size < margin_y:
            add_page(topic)
        # Main heading for the subject
        c.setFont(font_name, font_size + 4)
        c.drawString(margin_x, y_position, subject)
        y_position -= font_size * 2
        # Subheading for the topic
        c.setFont(font_name, font_size + 2)
        c.drawString(margin_x, y_position, topic)
        y_position -= font_size * 2
        # Draw a horizontal line
        c.setLineWidth(1)
        c.line(margin_x, y_position, width - margin_x, y_position)
        y_position -= font_size * 1.5
        # Reset font back to normal for questions
        c.setFont(font_name, font_size)

    # Function to wrap and print text
    def draw_wrapped_text(text, wrap_width, bold=False):
        nonlocal y_position
        wrapped_lines = textwrap.wrap(text, width=wrap_width)
        if bold:
            c.setFont('Helvetica-Bold', font_size)  # Using built-in bold font
        else:
            c.setFont(font_name, font_size)
        for line in wrapped_lines:
            if y_position - font_size < margin_y:
                add_page(topic)
            c.drawString(margin_x, y_position, line)
            y_position -= font_size * 1.5

    # Function to add a question
    def add_question(serial_no, question, options):
        nonlocal y_position
        question_text = f"{serial_no:03}. {question}"

        # Wrap question text and make it bold
        draw_wrapped_text(question_text, wrap_width, bold=True)

        # Add 1 line space between the question and the options
        y_position -= font_size * 1.5

        # Handle options with wrapping (normal font)
        for option in options.split(" | "):
            draw_wrapped_text(option.strip(), wrap_width - 4)

        # Add an empty line after each question
        y_position -= font_size * 1.5

    # Main function to process each topic
    for topic in topics:
        questions = fetch_questions(conn, subject, topic)
        serial_number = reset_serial_number()
        answers = []

        # Add heading for subject and topic
        add_heading(subject, topic)

        # Write Questions
        for question_text, question_options, correct_answer in questions:
            # Check if the question and options will fit on the current page
            if y_position - (len(question_options.split(" | ")) + 4) * font_size < margin_y:
                add_page(topic)

            add_question(serial_number, question_text, question_options)
            # Store the answers for printing later
            answers.append((serial_number, correct_answer))
            serial_number += 1

        # Print answers after questions for each topic
        if y_position - (len(answers) + 2) * font_size < margin_y:
            add_page(topic)

        # Title for the answer section
        c.setFont(font_name, font_size + 2)
        c.drawString(margin_x, y_position, f"Answers for {topic}")
        y_position -= font_size * 2
        c.setFont(font_name, font_size)

        # Write Answers
        for serial_no, answer in answers:
            if y_position - font_size < margin_y:
                add_page(topic)
            c.drawString(margin_x, y_position, f"{serial_no:03}. {answer}")
            y_position -= font_size * 1.5

        # Add a page break between topics
        add_page(topic)

    # Save the PDF
    c.save()


# Main function to generate the PDF for multiple topics
def generate_pdf(config):
    filename = config["output_file"]
    subject = config["subject"]
    topics = config["topics"]
    create_pdf(filename, subject, topics, config)
    print(f"PDF generated: {filename}")


# Entry point
if __name__ == "__main__":
    config = read_config("config/02_config_4_print_pdf.json")
    generate_pdf(config)
