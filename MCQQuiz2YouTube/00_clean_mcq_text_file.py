import re

def clean_quiz_file(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        cleaned_lines = []
        question_pattern = re.compile(r'^\d+\.\s*')  # Pattern to match any existing number and period at the start

        for line in lines:
            # Remove leading spaces and asterisks
            cleaned_line = line.strip().replace("**", "")

            # Renumber the question, stripping any existing numbering
            if "Question:" in cleaned_line:
                cleaned_line = question_pattern.sub("", cleaned_line)  # Remove existing numbering
                # cleaned_line = f"{cleaned_line.replace('Question:', 'Question: ')}"
            # Remove leading '- ' if it exists
            elif cleaned_line.startswith('- '):
                cleaned_line = cleaned_line.replace('- ', '')

            # Ensure "Options:" and "Answer:" are formatted correctly
            if cleaned_line.startswith("Options:"):
                cleaned_line = "Options:"
            elif cleaned_line.startswith("Answer:"):
                cleaned_line = cleaned_line.replace("Answer:", "Answer: ")

            cleaned_lines.append(cleaned_line)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(cleaned_lines))

        print(f"Cleaned file saved as {output_file}")

    except UnicodeDecodeError as e:
        print(f"Error decoding file: {e}")

# Replace 'your_input_file.txt' with the actual file name you want to process
input_file = './input/MCQ_Input.txt'
output_file = './input/Judges_Chapter_07_MCQ.txt'
clean_quiz_file(input_file, output_file)