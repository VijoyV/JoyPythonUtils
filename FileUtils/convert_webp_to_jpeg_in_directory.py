import os
from PIL import Image

def convert_webp_to_jpeg_in_directory(directory_path):
    """
    Convert all .webp files in a directory to .jpeg format with the same name,
    dimensions, and quality.

    :param directory_path: Path to the directory containing .webp files.
    """
    try:
        # Ensure the directory exists
        if not os.path.isdir(directory_path):
            print(f"Error: Directory '{directory_path}' does not exist.")
            return

        # Iterate through all files in the directory
        for file_name in os.listdir(directory_path):
            # Check for .webp files
            if file_name.lower().endswith(".webp"):
                webp_file_path = os.path.join(directory_path, file_name)
                jpeg_file_path = os.path.join(
                    directory_path, os.path.splitext(file_name)[0] + ".jpeg"
                )

                try:
                    # Open the .webp image
                    with Image.open(webp_file_path) as img:
                        # Convert and save as .jpeg
                        img = img.convert("RGB")  # Ensure no alpha channel
                        img.save(jpeg_file_path, "JPEG", quality=95)  # Set quality to 95
                    print(f"Converted: {webp_file_path} -> {jpeg_file_path}")
                except Exception as e:
                    print(f"Error converting {webp_file_path}: {e}")

        print("Conversion completed.")

    except Exception as e:
        print(f"Error: {e}")

# Example usage
directory = "C:\\Users\\vijoy\\Downloads"  # Replace with the path to your directory
convert_webp_to_jpeg_in_directory(directory)
