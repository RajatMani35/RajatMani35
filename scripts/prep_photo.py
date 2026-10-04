from PIL import Image, ImageEnhance
from rembg import remove
import cv2
import numpy as np
import sys


def prep_photo(input_path, output_path):
    # Load image
    image = Image.open(input_path).convert("RGBA")

    # Remove background
    print("Removing background...")
    image_no_bg = remove(image)

    # White background
    white_bg = Image.new("RGBA", image_no_bg.size, (255, 255, 255, 255))
    white_bg.alpha_composite(image_no_bg)

    # Convert to RGB
    rgb = white_bg.convert("RGB")

    # Convert to OpenCV
    img = np.array(rgb)

    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Improve local contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # Slight contrast enhancement
    enhanced = Image.fromarray(enhanced)

    enhanced = ImageEnhance.Contrast(enhanced).enhance(1.4)

    # Save
    enhanced.save(output_path)

    print(f"Saved: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("python scripts/prep_photo.py source-photo.jpg source-prepped.png")
        sys.exit(1)

    prep_photo(sys.argv[1], sys.argv[2])