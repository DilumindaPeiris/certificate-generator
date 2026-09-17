import csv
import os
import re
import zipfile
from PIL import Image, ImageDraw, ImageFont


def _sanitize_filename_component(value):
    safe_value = value.strip()
    safe_value = re.sub(r"[\\/:*?\"<>|]+", " ", safe_value)
    safe_value = safe_value.replace("\n", " ").replace("\r", " ")
    safe_value = re.sub(r"\s+", " ", safe_value).strip()
    safe_value = re.sub(r"[^A-Za-z0-9_. -]", "_", safe_value)
    safe_value = re.sub(r"\s+", "_", safe_value.strip())
    safe_value = safe_value.strip("._")
    return safe_value or "certificate"


def generate_and_zip_certificates(csv_path, template_path, font_path, output_dir, zip_path, text_y=500):
    """
    Generates customized certificates from a CSV file and packages them into a ZIP archive.
    Returns a tuple (success: bool, message: str).
    """
    os.makedirs(output_dir, exist_ok=True)

    try:
        base_image = Image.open(template_path)
    except FileNotFoundError:
        return False, f"Template image not found at {template_path}"

    try:
        font = ImageFont.truetype(font_path, size=60)
    except IOError:
        return False, f"Font file not found at {font_path}"

    generated_files = []

    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Ignore header

            for row in reader:
                if not row:
                    continue

                name = row[0].strip()
                if not name:
                    continue

                certificate = base_image.copy()
                draw = ImageDraw.Draw(certificate)

                text_width = draw.textlength(name, font=font)
                image_width = certificate.width
                text_x = (image_width - text_width) / 2

                draw.text((text_x, text_y), name, fill=(0, 0, 0), font=font)

                safe_name = _sanitize_filename_component(name)
                output_filename = f"{safe_name}_certificate.pdf"
                output_path = os.path.join(output_dir, output_filename)

                if certificate.mode != 'RGB':
                    certificate = certificate.convert('RGB')

                certificate.save(output_path, "PDF", resolution=300.0)
                generated_files.append(output_path)

    except FileNotFoundError:
        return False, f"CSV file not found at {csv_path}"
    except Exception as e:
        return False, f"Error processing CSV: {str(e)}"

    if not generated_files:
        return False, "No valid names found in the CSV file."

    # Create the zip file
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in generated_files:
                # Add file to zip with just its base name (no directory structure inside zip)
                zipf.write(file_path, os.path.basename(file_path))
        return True, "Success"
    except Exception as e:
        return False, f"Error creating ZIP file: {str(e)}"

if __name__ == "__main__":
    # Test block
    print("This script is now intended to be used programmatically by the Flask app.")
