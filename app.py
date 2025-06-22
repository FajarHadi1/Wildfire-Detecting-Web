from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

app = Flask(__name__)
app.secret_key = 'secret'  # dibutuhkan untuk session

# Load model
model = load_model('model/wildfire_classification_model.h5')

# Ukuran input sesuai dengan model kamu
IMG_SIZE = (128, 128)

def prepare_image(image_path):
    img = Image.open(image_path).convert('RGB')
    img = img.resize(IMG_SIZE)
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files.get('image')
    if not file:
        return "No image uploaded", 400

    # Ensure the uploads folder exists
    upload_folder = os.path.join('static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, file.filename)
    file.save(filepath)

    image_array = prepare_image(filepath)
    prediction = model.predict(image_array)[0][0]

    label = "wildfire" if prediction >= 0.5 else "no wildfire"
    confidence = float(prediction) if label == "wildfire" else 1.0 - float(prediction)

    session['label'] = label
    session['confidence'] = round(confidence * 100, 2)
    session['image_path'] = filepath  # full path
    session['image_filename'] = file.filename  # just the filename

    return redirect(url_for('result'))

@app.route('/result')
def result():
    label = session.get('label', None)
    confidence = session.get('confidence', None)
    image_path = session.get('image_path', 'static/forest.jpg')  # default image

    filename = os.path.basename(image_path)

    # Set fallback values
    if label is None or confidence is None:
        label = 'awaiting'
        confidence = 50.0

    return render_template('result.html',
                           label=label,
                           confidence=confidence,
                           image_filename=filename)


if __name__ == '__main__':
    app.run(debug=True)
