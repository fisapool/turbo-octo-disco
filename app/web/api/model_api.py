from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from PIL import Image
import numpy as np
from ml.training.screenshot_classifier import classify_screenshot

model_api = Blueprint('model_api', __name__)

# Configuration
UPLOAD_FOLDER = 'data/unlabeled'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@model_api.route('/predict', methods=['POST'])
def predict():
    """Endpoint for model prediction with confidence"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            prediction, confidence = classify_screenshot(filepath, return_confidence=True)
            return jsonify({
                'prediction': prediction,
                'confidence': confidence,
                'filename': filename
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400

@model_api.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Endpoint for batch predictions"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
        
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected'}), 400
        
    valid_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            valid_files.append(filepath)
            
    if not valid_files:
        return jsonify({'error': 'No valid files'}), 400
        
    try:
        results = classify_batch(valid_files)
        return jsonify({
            'predictions': [{
                'filename': os.path.basename(path),
                'prediction': pred,
                'confidence': conf
            } for path, pred, conf in results]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@model_api.route('/predictions/history', methods=['GET'])
def prediction_history():
    """Endpoint to get prediction history"""
    try:
        # TODO: Implement prediction history tracking
        return jsonify({'message': 'Prediction history endpoint'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@model_api.route('/label', methods=['POST'])
def label():
    """Endpoint for saving labeled data"""
    data = request.get_json()
    if not data or 'filename' not in data or 'label' not in data:
        return jsonify({'error': 'Invalid request'}), 400
        
    try:
        src_path = os.path.join(UPLOAD_FOLDER, data['filename'])
        dest_dir = os.path.join('data/train', data['label'])
        os.makedirs(dest_dir, exist_ok=True)
        os.rename(src_path, os.path.join(dest_dir, data['filename']))
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
