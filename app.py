import os
import tempfile
import uuid
import shutil
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from generate_certificates import generate_and_zip_certificates

app = Flask(__name__)
# Max upload size (e.g., 50MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if 'csvFile' not in request.files or 'templateImage' not in request.files or 'fontFile' not in request.files:
        return jsonify({'error': 'Missing required files'}), 400

    csv_file = request.files['csvFile']
    template_image = request.files['templateImage']
    font_file = request.files['fontFile']
    text_y_str = request.form.get('textY', '500')

    if not all([csv_file.filename, template_image.filename, font_file.filename]):
        return jsonify({'error': 'One or more files were not selected'}), 400

    try:
        text_y = int(text_y_str)
    except ValueError:
        return jsonify({'error': 'Vertical position (Y-axis) must be an integer'}), 400

    # Create a temporary directory for processing
    job_id = str(uuid.uuid4())
    temp_dir = os.path.join(tempfile.gettempdir(), f"cert_gen_{job_id}")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Save uploaded files
        csv_path = os.path.join(temp_dir, secure_filename(csv_file.filename))
        template_path = os.path.join(temp_dir, secure_filename(template_image.filename))
        font_path = os.path.join(temp_dir, secure_filename(font_file.filename))
        
        csv_file.save(csv_path)
        template_image.save(template_path)
        font_file.save(font_path)

        output_dir = os.path.join(temp_dir, "output")
        zip_path = os.path.join(temp_dir, "certificates.zip")

        # Call generation script
        success, message = generate_and_zip_certificates(
            csv_path, template_path, font_path, output_dir, zip_path, text_y
        )

        if not success:
            return jsonify({'error': message}), 500

        # Return the zip file to the client
        return send_file(zip_path, as_attachment=True, download_name='certificates.zip')

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    # Note: temp_dir cleanup in a production app would happen in a background task or finally block, 
    # but send_file needs the file to exist after the return. We'll leave it in tempdir for now.

if __name__ == '__main__':
    app.run(debug=True, port=5000)
