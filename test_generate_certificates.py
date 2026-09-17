import os
import shutil
import tempfile
import unittest
from PIL import Image

from generate_certificates import generate_and_zip_certificates


class GenerateCertificatesTests(unittest.TestCase):
    def _find_font_path(self):
        candidates = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        self.fail("No suitable font file found for testing")

    def test_generates_certificate_with_sanitized_filename(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, "names.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
                csv_file.write("Name\nAlice / Bob\n")

            template_path = os.path.join(tmp_dir, "template.png")
            Image.new("RGB", (1200, 800), "white").save(template_path)

            font_path = os.path.join(tmp_dir, "font.ttf")
            shutil.copyfile(self._find_font_path(), font_path)

            output_dir = os.path.join(tmp_dir, "output")
            zip_path = os.path.join(tmp_dir, "certificates.zip")

            success, message = generate_and_zip_certificates(
                csv_path, template_path, font_path, output_dir, zip_path, 500
            )

            self.assertTrue(success, message)
            self.assertTrue(os.path.exists(zip_path))
            files = sorted(os.listdir(output_dir))
            self.assertEqual(len(files), 1)
            self.assertIn("Alice_Bob_certificate.pdf", files[0])


if __name__ == "__main__":
    unittest.main()
