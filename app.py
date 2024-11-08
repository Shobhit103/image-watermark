from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images', 'watermarks')

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files or 'watermark_text' not in request.form:
        return "No image or watermark text provided", 400
    
    image_file = request.files['image']
    watermark_text = request.form['watermark_text']
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
    image_file.save(image_path)
    
    # Apply watermark
    watermarked_image_path = apply_watermark(image_path, watermark_text)
    
    return redirect(url_for('download_image', filename=os.path.basename(watermarked_image_path)))

def apply_watermark(image_path, watermark_text):
    # Open the image
    image = Image.open(image_path)
    drawable = ImageDraw.Draw(image)
    
    # Font size and position
    font = ImageFont.load_default()
    width, height = image.size
    textwidth, textheight = drawable.textsize(watermark_text, font=font)
    x = width - textwidth - 10
    y = height - textheight - 10
    
    # Apply watermark
    drawable.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
    
    # Save the watermarked image
    watermarked_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'watermarked_' + os.path.basename(image_path))
    image.save(watermarked_image_path)
    return watermarked_image_path

@app.route('/download/<filename>')
def download_image(filename):
    # Download the watermarked image to the default Downloads folder
    downloads_folder = os.path.expanduser("~/Downloads")
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    destination_path = os.path.join(downloads_folder, filename)
    os.rename(original_path, destination_path)
    return send_from_directory(downloads_folder, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)