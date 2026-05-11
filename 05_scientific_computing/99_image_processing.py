"""
Script: Basic Image Processing with PIL/Pillow
What it does: Loads, modifies, and saves images using Python.
Pillow is the most popular Python library for image manipulation.

Install: pip install pillow numpy
"""

try:
    from PIL import Image, ImageFilter, ImageDraw, ImageFont
    import numpy as np
    import os

    # --- Create a sample image from scratch ---
    print("=== Creating an Image ===")

    # Create a 300x300 RGB image with a gradient
    width, height = 300, 300
    img_array = np.zeros((height, width, 3), dtype=np.uint8)

    # Create a gradient: red increases left-to-right, blue top-to-bottom
    for y in range(height):
        for x in range(width):
            img_array[y, x] = [
                int(255 * x / width),   # R: increases left to right
                100,                     # G: constant green
                int(255 * y / height)   # B: increases top to bottom
            ]

    img = Image.fromarray(img_array)  # convert numpy array to PIL image
    img.save("gradient.png")
    print(f"Created: gradient.png ({width}x{height})")

    # --- Image properties ---
    print("\n=== Image Properties ===")
    print(f"Size:   {img.size}")         # (width, height)
    print(f"Mode:   {img.mode}")         # RGB, RGBA, L (grayscale), etc.
    print(f"Format: {img.format}")       # PNG, JPEG, etc. (None for new images)

    # --- Basic transformations ---
    print("\n=== Transformations ===")

    # Resize
    resized = img.resize((150, 150))    # make it smaller
    resized.save("gradient_small.png")
    print("Resized to 150x150: gradient_small.png")

    # Convert to grayscale
    gray = img.convert("L")             # "L" = luminance (grayscale)
    gray.save("gradient_gray.png")
    print("Grayscale: gradient_gray.png")

    # Rotate
    rotated = img.rotate(45, expand=True)  # rotate 45 degrees
    rotated.save("gradient_rotated.png")
    print("Rotated 45°: gradient_rotated.png")

    # Flip
    flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
    flipped.save("gradient_flipped.png")
    print("Flipped: gradient_flipped.png")

    # --- Apply filters ---
    print("\n=== Filters ===")
    blurred = img.filter(ImageFilter.BLUR)
    blurred.save("gradient_blurred.png")
    print("Blurred: gradient_blurred.png")

    sharpened = img.filter(ImageFilter.SHARPEN)
    sharpened.save("gradient_sharp.png")
    print("Sharpened: gradient_sharp.png")

    # --- Draw on an image ---
    print("\n=== Drawing on Image ===")
    canvas = Image.new("RGB", (300, 100), color=(255, 255, 255))  # white canvas
    draw = ImageDraw.Draw(canvas)

    draw.rectangle([10, 10, 100, 90], fill="blue", outline="black")   # rectangle
    draw.ellipse([120, 10, 220, 90], fill="red", outline="black")      # ellipse
    draw.line([240, 10, 290, 90], fill="green", width=3)               # line
    draw.text((10, 10), "Hello!", fill="white")                        # text

    canvas.save("drawing.png")
    print("Drawing: drawing.png")

    # Clean up
    for f in ["gradient.png", "gradient_small.png", "gradient_gray.png",
              "gradient_rotated.png", "gradient_flipped.png",
              "gradient_blurred.png", "gradient_sharp.png", "drawing.png"]:
        if os.path.exists(f):
            os.remove(f)
    print("\nAll files created and cleaned up!")

except ImportError:
    print("Install: pip install pillow numpy")
