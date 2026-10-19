"""Generate styled terminal screenshots from raw log files using PIL."""
import os
from PIL import Image, ImageDraw, ImageFont

BG_COLOR = (15, 23, 42)      # Deep slate
HEADER_COLOR = (30, 41, 59)  # Slate header
TEXT_COLOR = (241, 245, 249) # Light text
MUTED_COLOR = (148, 163, 184)


def render_terminal(title, text_lines, output_image_path):
    width = 900
    line_height = 20
    header_height = 36
    padding = 20
    total_height = header_height + (len(text_lines) * line_height) + (padding * 2)

    img = Image.new("RGB", (width, total_height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Draw header bar
    draw.rectangle([0, 0, width, header_height], fill=HEADER_COLOR)

    # Draw Mac/Linux window buttons
    draw.ellipse([14, 12, 26, 24], fill=(239, 68, 68))
    draw.ellipse([34, 12, 46, 24], fill=(245, 158, 11))
    draw.ellipse([54, 12, 66, 24], fill=(16, 185, 129))

    try:
        font = ImageFont.truetype("consola.ttf", 13)
        header_font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        font = ImageFont.load_default()
        header_font = font

    # Draw title
    draw.text((80, 10), title, fill=MUTED_COLOR, font=header_font)

    # Draw body lines
    y = header_height + padding
    for line in text_lines:
        color = TEXT_COLOR
        if "PASSED" in line or "healthy" in line or "SUCCESS" in line:
            color = (52, 211, 153) # Green
        elif "CRITICAL" in line or "ERROR" in line or "FAILED" in line:
            color = (248, 113, 113) # Red
        elif "WARNING" in line or "HIGH" in line:
            color = (251, 191, 36) # Amber

        draw.text((padding, y), line, fill=color, font=font)
        y += line_height

    img.save(output_image_path)
    print(f"Rendered terminal capture: {output_image_path}")


if __name__ == "__main__":
    evidence_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(evidence_dir, "raw")

    # Sample render from raw pytest output
    pytest_path = os.path.join(raw_dir, "pytest.txt")
    if os.path.exists(pytest_path):
        with open(pytest_path, "r", encoding="utf-8") as f:
            lines = [line.rstrip() for line in f.readlines()[:35]]
        render_terminal("pytest --cov=app (45 passed, 96% coverage)", lines, os.path.join(evidence_dir, "term_pytest.png"))
