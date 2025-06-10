import os
import io
import PyPDF2
import fitz  # PyMuPDF
from PIL import Image


def compress_jpg(input_path, output_path, quality=75):
    """
    Compresses a JPG file to reduce its size.

    :param input_path: Path to the input JPG file.
    :param output_path: Path to save the compressed JPG file.
    :param quality: Quality of the output image (1-100).
    """
    try:
        with Image.open(input_path) as img:
            img = img.convert("RGB")  # Ensure compatibility
            img.save(output_path, "JPEG", quality=quality)
        print(f"Compressed JPG saved at {output_path}")
    except Exception as e:
        print(f"Error compressing JPG: {e}")

def compress_pdf(input_path, output_path):
    """
    Compresses a PDF file by reducing image quality and content duplication.

    :param input_path: Path to the input PDF file.
    :param output_path: Path to save the compressed PDF file.
    """
    try:
        doc = fitz.open(input_path)
        new_doc = fitz.open()  # Create a new PDF

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img = img.convert("RGB")
            img = img.resize((int(pix.width * 0.5), int(pix.height * 0.5)), Image.Resampling.LANCZOS)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=50)
            img_byte_arr = img_byte_arr.getvalue()

            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(new_page.rect, stream=img_byte_arr)

        new_doc.save(output_path, garbage=4, deflate=True)
        print(f"Compressed PDF saved at {output_path}")
    except Exception as e:
        print(f"Error compressing PDF: {e}")

def compress_files_in_directory(input_dir, output_dir, jpg_quality=75):
    """
    Compresses all JPG and PDF files in a directory.

    :param input_dir: Directory containing files to compress.
    :param output_dir: Directory to save compressed files.
    :param jpg_quality: Quality of the compressed JPG files (1-100).
    """
    os.makedirs(output_dir, exist_ok=True)
    for file_name in os.listdir(input_dir):
        input_path = os.path.join(input_dir, file_name)
        output_path = os.path.join(output_dir, file_name)

        if file_name.lower().endswith(".jpg") or file_name.lower().endswith(".jpeg"):
            print(f"Compressing JPG: {file_name}")
            compress_jpg(input_path, output_path, quality=jpg_quality)
        elif file_name.lower().endswith(".pdf"):
            print(f"Compressing PDF: {file_name}")
            compress_pdf(input_path, output_path)
        else:
            print(f"Skipping unsupported file: {file_name}")


# Example Usage
if __name__ == "__main__":
    # input_directory = "input_files"  # Replace with your input directory
    # output_directory = "compressed_files"  # Replace with your output directory

    input_file = "C:\\Users\\vijoy\\OneDrive\\Documents\\4_Joanna\\Photos-N-Signatures\\Vijoy-Signature.jpg"  # Replace with your input directory
    output_file = "C:\\Users\\vijoy\\OneDrive\\Documents\\4_Joanna\\Photos-N-Signatures\\Vijoy-Signature_20kb.jpg"  # Replace with your output directory
    # input_file = "./Joanna_Aadhaar.pdf"  # Replace with your input directory
    # output_file = "./Joanna_Aadhaar_200KB.pdf"  # Replace with your output directory
    # compress_pdf(input_file, output_file)
    jpg_quality = 70  # Adjust JPG quality as needed (default is 75)

    # compress_files_in_directory(input_directory, output_directory, jpg_quality)
    compress_jpg(input_file, output_file, jpg_quality)
