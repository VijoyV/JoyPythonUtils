import re


def split_text_by_heading(text, output_dir, base_name):
    # Use a regular expression to split text based on exactly two hashes (##)
    chunks = re.split(r'\n(?=## [^#])', text)

    # The first chunk before the first `##` will be skipped if it's empty
    if not chunks[0].strip().startswith("##"):
        chunks = chunks[1:]

    for chunk in chunks:
        # Extract the heading and remove it from the content
        heading_match = re.match(r'## (.+)', chunk)
        if heading_match:
            heading = heading_match.group(1).strip()
            content = chunk[len(heading_match.group(0)):].strip()  # Remove the heading line from the content

            # Create a safe filename from the heading
            filename = f"{output_dir}\\{base_name}_{heading.replace(' ', '_').replace('/', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Created file: {filename}")


def process_md_file(input_md_file, output_dir, base_name):
    with open(input_md_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # Split the text by Heading Level 2 (##) and save to files
    split_text_by_heading(text, output_dir, base_name)


if __name__ == "__main__":
    input_md_file = "C:\\LogosQuiz_Preparation\\LogosQuiz-Judges.md"
    output_dir = "C:\\LogosQuiz_Preparation\\Split_Files"
    base_name = "Judges"

    process_md_file(input_md_file, output_dir, base_name)
