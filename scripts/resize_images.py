
from pathlib import Path
from PIL import Image, ImageOps
import tempfile
import os

IMAGE_DIR = Path("images")
MAX_WIDTH = 1000
JPEG_QUALITY = 85

EXTENSIONS = {".jpg", ".jpeg"}


def process_image(path):
    try:
        with Image.open(path) as original:
            # Correct orientation using EXIF metadata
            img = ImageOps.exif_transpose(original)

            original_size = img.size

            # Resize only if wider than 1000px
            if img.width > MAX_WIDTH:
                new_height = round(img.height * MAX_WIDTH / img.width)
                img = img.resize(
                    (MAX_WIDTH, new_height),
                    Image.Resampling.LANCZOS
                )

            # Convert to RGB for JPEG output
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Retain embedded colour profile where available
            save_options = {
                "format": "JPEG",
                "quality": JPEG_QUALITY,
                "optimize": True,
                "progressive": True
            }

            icc_profile = original.info.get("icc_profile")
            if icc_profile:
                save_options["icc_profile"] = icc_profile

            # Write to temporary file before replacing original
            with tempfile.NamedTemporaryFile(
                suffix=".jpg",
                dir=path.parent,
                delete=False
            ) as temp:
                temp_path = Path(temp.name)

            try:
                img.save(temp_path, **save_options)
                os.replace(temp_path, path)
            finally:
                if temp_path.exists():
                    temp_path.unlink()

            print(
                f"Processed: {path} "
                f"{original_size} -> {img.size}"
            )

    except Exception as error:
        print(f"ERROR processing {path}: {error}")
        raise


def main():
    if not IMAGE_DIR.exists():
        raise FileNotFoundError("images/ directory not found")

    images = [
        p for p in IMAGE_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSIONS
    ]

    print(f"Found {len(images)} JPEG images.")

    for image in images:
        process_image(image)

    print("Image processing complete.")


if __name__ == "__main__":
    main()
