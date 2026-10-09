
from pathlib import Path
from html import escape

from PIL import Image, ImageOps, ImageEnhance


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_FILE = Path("rajat-ascii.svg")

# Prefer the processed image, then fall back to original.
POSSIBLE_INPUTS = [
    Path("source-prepped.png"),
    Path("source-photo.png"),
    Path("source-photo.jpg"),
    Path("source-photo.jpeg"),
]

# Higher values create denser, more detailed ASCII art.
COLS = 110
ROWS = 75

# Character dimensions in SVG pixels.
CHAR_WIDTH = 8
CHAR_HEIGHT = 11
FONT_SIZE = 10

# White text on a black background.
BACKGROUND = "#000000"
TEXT_COLOR = "#ffffff"
CURSOR_COLOR = "#ffffff"

# From sparse characters to dense characters.
# Dark parts of the source image become denser white text.
RAMP = "  .,:-~=+*#%@"

# Image processing.
CONTRAST = 1.5
SHARPNESS = 1.2

# Animation timing.
ROW_DELAY = 0.035
ROW_DURATION = 0.35


# ============================================================
# FIND INPUT IMAGE
# ============================================================

def find_input_image():
    for path in POSSIBLE_INPUTS:
        if path.exists():
            print(f"Using image: {path}")
            return path

    raise FileNotFoundError(
        "Could not find source-prepped.png or source-photo.png. "
        "Place your image in the project root."
    )


# ============================================================
# CROP IMAGE TO A CENTERED PORTRAIT
# ============================================================

def center_crop(image, target_ratio):
    width, height = image.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        image = image.crop(
            (left, 0, left + new_width, height)
        )
    elif current_ratio < target_ratio:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        image = image.crop(
            (0, top, width, top + new_height)
        )

    return image


# ============================================================
# CONVERT IMAGE TO ASCII
# ============================================================

def image_to_ascii(image_path):
    image = Image.open(image_path).convert("RGB")

    # Match the output's approximate character aspect ratio.
    target_ratio = (
        COLS * CHAR_WIDTH
        / (ROWS * CHAR_HEIGHT)
    )

    image = center_crop(image, target_ratio)

    # Convert to grayscale and improve contrast.
    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image)

    image = ImageEnhance.Contrast(image).enhance(CONTRAST)
    image = ImageEnhance.Sharpness(image).enhance(SHARPNESS)

    # Resize to a dense character grid.
    image = image.resize(
        (COLS, ROWS),
        Image.Resampling.LANCZOS
    )

    pixels = list(image.getdata())
    lines = []

    for row in range(ROWS):
        line = []

        for col in range(COLS):
            brightness = pixels[row * COLS + col]

            # Dark source pixels get dense characters.
            index = round(
                (255 - brightness)
                / 255
                * (len(RAMP) - 1)
            )

            line.append(RAMP[index])

        lines.append("".join(line))

    return lines


# ============================================================
# CREATE ANIMATED SVG
# ============================================================

def create_svg(lines):
    width = COLS * CHAR_WIDTH + 40
    height = ROWS * CHAR_HEIGHT + 40

    svg = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
        ),
        f'<rect width="100%" height="100%" fill="{BACKGROUND}"/>',
    ]

    # Render each line separately for a typing/reveal effect.
    for row, line in enumerate(lines):
        x = 20
        y = 20 + (row + 1) * CHAR_HEIGHT

        delay = row * ROW_DELAY

        svg.append(
            f'<text x="{x}" y="{y}" '
            f'fill="{TEXT_COLOR}" '
            f'font-family="monospace" '
            f'font-size="{FONT_SIZE}" '
            f'letter-spacing="0" '
            f'xml:space="preserve" opacity="0">'
            f'{escape(line)}'
            f'<animate attributeName="opacity" '
            f'from="0" to="1" '
            f'begin="{delay:.3f}s" '
            f'dur="{ROW_DURATION}s" '
            f'fill="freeze"/>'
            f'</text>'
        )

    # Blinking cursor at the bottom.
    cursor_x = 20
    cursor_y = 20 + (ROWS + 1) * CHAR_HEIGHT

    svg.append(
        f'<rect x="{cursor_x}" y="{cursor_y}" '
        f'width="8" height="{CHAR_HEIGHT}" '
        f'fill="{CURSOR_COLOR}">'
        '<animate attributeName="opacity" '
        'values="1;0;1" dur="1s" '
        'repeatCount="indefinite"/>'
        '</rect>'
    )

    svg.append("</svg>")

    return "\n".join(svg)


# ============================================================
# MAIN
# ============================================================

def main():
    image_path = find_input_image()

    print("Converting image to dense ASCII...")
    lines = image_to_ascii(image_path)

    print("Creating animated SVG...")
    svg = create_svg(lines)

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("ASCII portrait generated successfully!")
    print(f"Input:  {image_path}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Grid:   {COLS} columns x {ROWS} rows")
    print("Style:  white text on black background")


if __name__ == "__main__":
    main()
