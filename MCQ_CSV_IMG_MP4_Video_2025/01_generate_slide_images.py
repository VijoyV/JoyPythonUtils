# 01_generate_slide_images.py

import os
import json
import csv
from PIL import Image, ImageDraw, ImageFont

# === Load config ===
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

CSV_PATH = config["csv_file"]
BG_IMAGE = config["background_image"]
FONT_PATH = config["font_path"]
WIDTH = config["image_width"]
HEIGHT = config["image_height"]
OUTPUT_DIR = config["output_dir"]

QUESTION_BOX = config["question"]["box"]
QUESTION_FONT_SIZE = config["question"]["font_size"]
QUESTION_BG = config["question"]["background_color"]
QUESTION_COLOR = config["question"]["text_color"]

CHOICE_BOX = config["choices"]["box"]
CHOICE_FONT_SIZE = config["choices"]["font_size"]
CHOICE_BG = config["choices"]["background_color"]
CHOICE_COLOR = config["choices"]["text_color"]
CHOICE_SPACING = CHOICE_BOX["spacing"]
CHOICE_LABEL_BG = config["choices"].get("label_background_color", "#220033")

ANSWER_BOX = config["answer"]["box"]
ANSWER_FONT_SIZE = config["answer"]["font_size"]
ANSWER_BG = config["answer"]["background_color"]
ANSWER_COLOR = config["answer"]["text_color"]

os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)

# === Helper: Draw wrapped text inside a box ===
def draw_text_box(draw, text, font, box, fill_bg, fill_fg, padding=10, line_spacing=1.0):
    x, y, w, h = box["x"], box["y"], box["w"], box["h"]
    draw.rectangle([x, y, x + w, y + h], fill=fill_bg)

    # Word-wrap logic
    lines = []
    words = text.split()
    line = ""

    for word in words:
        test_line = f"{line} {word}".strip()
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0]
        if line_width + 2 * padding <= w:
            line = test_line
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    # Line height and vertical spacing
    line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1]
    line_gap = int(line_height * line_spacing)
    total_height = len(lines) * line_gap
    start_y = y + (h - total_height) // 2

    for i, line in enumerate(lines):
        draw.text((x + padding, start_y + i * line_gap), line, font=font, fill=fill_fg)

# === Helper: Draw a choice label and its text ===
def draw_choice_with_label_box(draw, label, text, font, base_x, base_y, box_w, box_h, label_bg, text_bg, text_fg, spacing=10):
    label_box_width = 80
    label_box = [base_x, base_y, base_x + label_box_width, base_y + box_h]
    draw.rectangle(label_box, fill=label_bg)

    bbox = font.getbbox(label)
    label_w = bbox[2] - bbox[0]
    label_h = bbox[3] - bbox[1]
    label_x = base_x + (label_box_width - label_w) // 2
    label_y = base_y + (box_h - label_h) // 2
    draw.text((label_x, label_y), label, font=font, fill=text_fg)

    # Text box
    text_box = {
        "x": base_x + label_box_width + spacing,
        "y": base_y,
        "w": box_w - label_box_width - spacing,
        "h": box_h
    }
    draw_text_box(draw, text, font, text_box, fill_bg=text_bg, fill_fg=text_fg)

# === Main Function ===
def generate_images():
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter='|')

        for idx, row in enumerate(reader, 1):
            # Base image
            base = Image.open(BG_IMAGE).convert("RGB").resize((WIDTH, HEIGHT))
            draw = ImageDraw.Draw(base)

            # Fonts
            font_q = ImageFont.truetype(FONT_PATH, QUESTION_FONT_SIZE)
            font_c = ImageFont.truetype(FONT_PATH, CHOICE_FONT_SIZE)
            font_a = ImageFont.truetype(FONT_PATH, ANSWER_FONT_SIZE)

            # Question
            draw_text_box(draw, row["Question"], font_q, QUESTION_BOX, QUESTION_BG, QUESTION_COLOR, line_spacing=1.5)

            # Choices
            y = CHOICE_BOX["y_start"]
            for opt in ["A", "B", "C", "D"]:
                label = f"Option {opt}"
                if label in row:
                    option_text = row[label].split('.', 1)[-1].strip()  # Strip "A.", "B." etc.
                    draw_choice_with_label_box(
                        draw,
                        f"[{opt}]",
                        option_text,
                        font_c,
                        CHOICE_BOX["x"],
                        y,
                        CHOICE_BOX["w"],
                        CHOICE_BOX["h"],
                        label_bg=CHOICE_LABEL_BG,
                        text_bg=CHOICE_BG,
                        text_fg=CHOICE_COLOR
                    )
                y += CHOICE_BOX["h"] + CHOICE_SPACING

            # Save question image
            q_path = os.path.join(OUTPUT_DIR, "images", f"slide_{idx:03d}_q.png")
            base.save(q_path)

            # Answer image
            base_a = base.copy()
            draw_a = ImageDraw.Draw(base_a)
            draw_text_box(draw_a, f"Answer: {row['Answer']}", font_a, ANSWER_BOX, ANSWER_BG, ANSWER_COLOR)
            a_path = os.path.join(OUTPUT_DIR, "images", f"slide_{idx:03d}_a.png")
            base_a.save(a_path)

            print(f"🖼️ Saved slide_{idx:03d}_q.png and slide_{idx:03d}_a.png")

if __name__ == "__main__":
    generate_images()
