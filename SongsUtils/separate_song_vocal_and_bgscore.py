"""

    This is experimental code. Require powerful machine with GPU
    uses its own venv: spleeter-env

    21-NOV-2024]

"""

import os
import gc
from spleeter.separator import Separator
import tensorflow as tf

# Suppress GPU-related warnings (use CPU only)
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings

def separate_audio(input_file, output_dir):
    """
    Separates vocals and accompaniment from an audio file.

    Args:
        input_file (str): Path to the input MP3 file.
        output_dir (str): Path to save the separated tracks.
    """
    os.makedirs(output_dir, exist_ok=True)
    try:
        print("Initializing Spleeter...")
        separator = Separator('spleeter:2stems')  # Use '4stems' for finer separation

        print(f"Processing file: {input_file}")
        separator.separate_to_file(input_file, output_dir)

        print(f"Separation completed. Files saved to: {output_dir}")
    except Exception as e:
        print(f"Error during separation: {e}")
    finally:
        gc.collect()  # Ensure resources are cleaned up

if __name__ == "__main__":
    input_file = "./songs/ETHRAYUM_DHAYAYULLA_MATHAVE.MP3"
    output_dir = "output"
    separate_audio(input_file, output_dir)
