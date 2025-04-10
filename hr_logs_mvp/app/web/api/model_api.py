from flask import Blueprint, request, jsonify
from datetime import datetime
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import os
import json

model_api = Blueprint('model_api', __name__, url_prefix='/api/model')

# Initialize model and prediction history
model = None
prediction_history = []

def load_ml_model():
    global model
    model_path = os.path.join(os.path.dirname(__file__), '../../../ml/models/hr_model.h5')
    if os.path.exists(model_path):
        model = load_model(model_path)
    else:
        print("Warning: Model file not found. Please train the model first.")

def preprocess_image(image_file):
    img = load_img(image_file, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array /= 255.0
    return np.expand_dims(img_array, axis=0)

def classify_screenshot(image_file):
    if model is None:
        load_ml_model()
    
    processed = preprocess_image(image_file)
    probabilities = model.predict(processed)[0]
    predicted_index = np.argmax(probabilities)
    confidence = float(probabilities[predicted_index])
    label = get_label_from_index(predicted_index)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "label": label,
        "confidence": confidence
    }
    prediction_history.append(log_entry)
    save_prediction_history()
    return label, confidence

def batch_classify_screenshots(image_files):
    results = []
    for image_file in image_files:
        label, confidence = classify_screenshot(image_file)
        results.append({
            "label": label,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        })
    return results

def get_prediction_history():
    history_path = os.path.join(os.path.dirname(__file__), '../../../ml/data/prediction_history.json')
    if os.path.exists(history_path):
        with open(history_path, 'r') as f:
            return json.load(f)
    return prediction_history

def save_prediction_history():
    history_path = os.path.join(os.path.dirname(__file__), '../../../ml/data/prediction_history.json')
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    with open(history_path, 'w') as f:
        json.dump(prediction_history, f)

def get_label_from_index(index):
    labels = ["attendance", "leave", "performance", "incident", "other"]
    return labels[index] if index < len(labels) else "unknown"

@model_api.route('/predict', methods=['POST'])
def predict_single():
    image = request.files.get('image')
    if not image:
        return jsonify({"error": "Image missing"}), 400

    try:
        label, confidence = classify_screenshot(image)
        return jsonify({
            "label": label,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_api.route('/batch_predict', methods=['POST'])
def predict_batch():
    images = request.files.getlist('images')
    if not images:
        return jsonify({"error": "No images provided"}), 400

    try:
        results = batch_classify_screenshots(images)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_api.route('/prediction_history', methods=['GET'])
def get_history():
    try:
        history = get_prediction_history()
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_api.route('/real_time_status', methods=['GET'])
def real_time_status():
    try:
        history = get_prediction_history()
        recent_predictions = history[-5:] if len(history) >= 5 else history
        
        avg_confidence = np.mean([p['confidence'] for p in recent_predictions]) if recent_predictions else 0
        
        status_data = {
            "current_batch_size": len(recent_predictions),
            "average_confidence": float(avg_confidence),
            "last_update": datetime.utcnow().isoformat(),
            "recent_predictions": recent_predictions
        }
        return jsonify(status_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500 