import face_recognition
import os
import shutil
from concurrent.futures import ProcessPoolExecutor

# Paths
source_dir = "C:\\_PhotosNVideos4BkUp\\JoannaArangetramPhotos\\27-04-2024_Arangetram"  # Replace with your photo directory
destination_dir = "C:\\_PhotosNVideos4BkUp\\JoannaArangetramPhotos\\SelectedByCode"  # Replace with your output directory
reference_image_path = "C:\\_PhotosNVideos4BkUp\\JoannaArangetramPhotos\\JoannaFace-01.jpg"  # Replace with your reference image

# Load and encode the reference image
reference_image = face_recognition.load_image_file(reference_image_path)
reference_encoding = face_recognition.face_encodings(reference_image)[0]

# Ensure the destination directory exists
os.makedirs(destination_dir, exist_ok=True)

def process_image(file_path):
    """
    Processes a single image to check if it contains the reference face.
    """
    try:
        # Load the image
        image = face_recognition.load_image_file(file_path)

        # Find face encodings in the image
        encodings = face_recognition.face_encodings(image)

        # Compare each encoding to the reference encoding
        for encoding in encodings:
            if face_recognition.compare_faces([reference_encoding], encoding, tolerance=0.6)[0]:
                # Copy the image if a match is found
                shutil.copy(file_path, os.path.join(destination_dir, os.path.basename(file_path)))
                print(f"Copied: {os.path.basename(file_path)}")
                break
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Main function to process images in parallel
def main():
    # List all image files in the source directory
    image_files = [
        os.path.join(source_dir, filename)
        for filename in os.listdir(source_dir)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]

    print(f"Found {len(image_files)} images to process.")

    # Use a process pool for parallel processing
    with ProcessPoolExecutor(max_workers=4) as executor:
        executor.map(process_image, image_files)

    print("Processing completed!")

if __name__ == "__main__":
    main()
