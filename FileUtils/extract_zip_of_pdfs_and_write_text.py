import os
import zipfile
from PyPDF2 import PdfReader

def extract_zip(zip_file_path, extract_to):
    """Extracts all contents of a ZIP file."""
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return [os.path.join(extract_to, file) for file in os.listdir(extract_to) if file.endswith('.pdf')]

def extract_pdf_text(pdf_file_path):
    """Extracts text from a PDF file."""
    reader = PdfReader(pdf_file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def save_text_to_file(text, output_file_path):
    """Saves extracted text to a text file."""
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(text)

def process_zip_to_text(zip_file_path, output_folder):
    """Processes a ZIP file containing PDFs and extracts text to individual TXT files."""
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Step 1: Extract ZIP contents
    pdf_files = extract_zip(zip_file_path, output_folder)
    print(f"Extracted PDF files: {pdf_files}")

    # Step 2: Extract text from each PDF and save as TXT
    for pdf_file in pdf_files:
        text = extract_pdf_text(pdf_file)
        output_file = os.path.splitext(os.path.basename(pdf_file))[0] + '.txt'
        output_file_path = os.path.join(output_folder, output_file)
        save_text_to_file(text, output_file_path)
        print(f"Extracted text saved to: {output_file_path}")

# Example usage
if __name__ == "__main__":
    zip_file_path = "C:\\WorkArea\\Joanna_Class_XII_Catechism\\Class-XII-SundayCatechism12ChaptersAsPDF.zip"  # Replace with the path to your ZIP file
    output_folder = "C:\\WorkArea\\Joanna_Class_XII_Catechism\\extracted_files"  # Replace with your desired output folder
    process_zip_to_text(zip_file_path, output_folder)

