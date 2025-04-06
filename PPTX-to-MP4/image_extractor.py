import os
import time
import win32com.client  # Windows-only
from config_loader import load_config


def pptx_to_images(pptx_file, output_dir, image_format="png", width=1920, height=1080):
    """Extracts slides as images using PowerPoint COM automation (Windows only)."""
    print(f"Extracting slides from {pptx_file} to {output_dir}...")

    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    powerpoint.Visible = 1
    presentation = powerpoint.Presentations.Open(os.path.abspath(pptx_file), WithWindow=False)

    os.makedirs(output_dir, exist_ok=True)
    presentation.Export(os.path.abspath(output_dir), image_format, width, height)

    time.sleep(2)  # Ensure files are saved
    presentation.Close()
    powerpoint.Quit()
    print("Slide extraction complete.")


if __name__ == "__main__":
    config = load_config()
    pptx_to_images(config["pptx"]["input_file"], config["video"]["slides_dir"])
