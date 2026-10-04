from PIL import Image, ImageOps, ImageEnhance
import html
import sys


# ============================================================
# SETTINGS
# ============================================================

# Bright -> sparse
# Dark -> dense
RAMP = " .:-=+*#%@"

# ASCII resolution
COLS = 65
ROWS = 55

# Character dimensions
CHAR_WIDTH = 10
CHAR_HEIGHT = 14

# Animation
ROW_DELAY = 0.065
ROW_DURATION = 0.55

# Colors
BACKGROUND = "#ffffff"
TEXT_COLOR = "#222222"
CURSOR_COLOR = "#222222"


# ============================================================
# IMAGE -> ASCII
# ============================================================

def image_to_ascii(image_path):

    image = Image.open(image_path).convert("L")

    print(f"Original image: {image.width} x {image.height}")

    width, height = image.size

    # --------------------------------------------------------
    # CROP
    # --------------------------------------------------------

    left = int(width * 0.28)
    right = int(width * 0.72)

    top = int(height * 0.01)
    bottom = int(height * 0.99)

    image = image.crop(
        (left, top, right, bottom)
    )

    print(
        f"Cropped image: {image.width} x {image.height}"
    )

    # --------------------------------------------------------
    # Improve contrast
    # --------------------------------------------------------

    image = ImageOps.autocontrast(
        image,
        cutoff=1
    )

    image = ImageEnhance.Contrast(
        image
    ).enhance(1.25)

    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    image = image.resize(
        (COLS, ROWS),
        Image.Resampling.LANCZOS
    )

    pixels = image.load()

    lines = []

    # --------------------------------------------------------
    # Convert brightness -> ASCII
    # --------------------------------------------------------

    for y in range(ROWS):

        line = ""

        for x in range(COLS):

            brightness = pixels[x, y]

            index = int(
                (255 - brightness)
                / 255
                * (len(RAMP) - 1)
            )

            index = max(
                0,
                min(index, len(RAMP) - 1)
            )

            line += RAMP[index]

        lines.append(line)

    return lines


# ============================================================
# ASCII -> ANIMATED SVG
# ============================================================

def make_svg(lines, output_path):

    width = COLS * CHAR_WIDTH
    height = ROWS * CHAR_HEIGHT

    svg = []

    # --------------------------------------------------------
    # SVG HEADER
    # --------------------------------------------------------

    svg.append(
        f'''<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}"
    xml:space="preserve">

    <rect
        width="100%"
        height="100%"
        fill="{BACKGROUND}"
    />

    <style>

        .ascii {{
            font-family: "Courier New", monospace;
            font-size: {CHAR_HEIGHT}px;
            fill: {TEXT_COLOR};
            font-weight: 400;
        }}

        .cursor {{
            fill: {CURSOR_COLOR};
        }}

    </style>
'''
    )

    # --------------------------------------------------------
    # CREATE EACH ROW
    # --------------------------------------------------------

    for row, line in enumerate(lines):

        y = (row + 1) * CHAR_HEIGHT

        clip_id = f"clip-row-{row}"

        delay = row * ROW_DELAY

        # ----------------------------------------------------
        # CLIP PATH
        # ----------------------------------------------------

        svg.append(
            f'''
    <clipPath id="{clip_id}">

        <rect
            x="0"
            y="{row * CHAR_HEIGHT}"
            width="0"
            height="{CHAR_HEIGHT}">

            <animate
                attributeName="width"
                from="0"
                to="{width}"
                begin="{delay:.2f}s"
                dur="{ROW_DURATION}s"
                fill="freeze"
            />

        </rect>

    </clipPath>
'''
        )

        escaped_line = html.escape(line)

        # ----------------------------------------------------
        # ASCII ROW
        # ----------------------------------------------------

        svg.append(
            f'''
    <text
        x="0"
        y="{y}"
        class="ascii"
        clip-path="url(#{clip_id})"
        xml:space="preserve">{escaped_line}</text>
'''
        )

        # ----------------------------------------------------
        # CURSOR
        # ----------------------------------------------------

        svg.append(
            f'''
    <rect
        class="cursor"
        x="0"
        y="{row * CHAR_HEIGHT}"
        width="4"
        height="{CHAR_HEIGHT - 1}"
        opacity="0">

        <animate
            attributeName="x"
            from="0"
            to="{width}"
            begin="{delay:.2f}s"
            dur="{ROW_DURATION}s"
            fill="freeze"
        />

        <animate
            attributeName="opacity"
            values="0;1;1;0"
            keyTimes="0;0.05;0.9;1"
            begin="{delay:.2f}s"
            dur="{ROW_DURATION}s"
            fill="freeze"
        />

    </rect>
'''
        )

    svg.append("</svg>")

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(svg)
        )

    print()
    print("======================================")
    print(" Animated ASCII SVG created!")
    print("======================================")
    print(f"Output : {output_path}")
    print(f"Size   : {width} x {height}")
    print()


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) != 3:

        print()
        print("Usage:")
        print()
        print(
            "python3 scripts/make_ascii_svg.py "
            "source-photo.png rajat-ascii.svg"
        )
        print()

        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    print()
    print("======================================")
    print(" RajatMani35 ASCII Portrait")
    print("======================================")
    print()

    lines = image_to_ascii(
        input_path
    )

    print("Generating animated SVG...")

    make_svg(
        lines,
        output_path
    )


if __name__ == "__main__":
    main()