"""
screenshot_classifier.py

A pilot project to classify screenshots into categories such as "code", "document", and "web" 
using transfer learning with MobileNetV2.
"""

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
import numpy as np
import os

# ------- Configuration -------
train_dir = 'data/train'         # Training data directory
val_dir = 'data/validation'      # Validation data directory

img_height = 224
img_width = 224
batch_size = 32
num_classes = 3                  # E.g., code, document, web

# ------- Data Generators -------
# Enhanced augmentation with minority class focus
train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=40,
    zoom_range=0.3,
    width_shift_range=0.3,
    height_shift_range=0.3,
    shear_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode="reflect"
)

val_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input
)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical'
)

val_generator = val_datagen.flow_from_directory(
    val_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical'
)

# ------- Build the Model -------
# Load MobileNetV2 without the top classification layers; use pre-trained weights from ImageNet.
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(img_height, img_width, 3))

# Freeze the base model layers so that they are not updated during the initial training phase.
for layer in base_model.layers:
    layer.trainable = False

# Add custom classification layers on top.
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
predictions = Dense(num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)
# Focal loss implementation
def focal_loss(gamma=2., alpha=0.25):
    def focal_loss_fixed(y_true, y_pred):
        pt = tf.where(tf.equal(y_true, 1), y_pred, 1-y_pred)
        return -tf.reduce_mean(alpha * tf.pow(1. - pt, gamma) * tf.math.log(pt))
    return focal_loss_fixed

# Calculate class weights
class_weights = {
    0: 5.5,  # code
    1: 1.0,  # document
    2: 11.0  # web
}

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss=focal_loss(),
    metrics=['accuracy']
)
model.summary()

# ------- Callbacks -------
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint, EarlyStopping
from datetime import datetime

log_dir = "logs/fit/" + datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1)
checkpoint_callback = ModelCheckpoint(
    filepath='models/screenshot_classifier_{epoch:02d}.keras',
    save_best_only=True,
    monitor='val_accuracy',
    mode='max'
)
early_stopping = EarlyStopping(monitor='val_loss', patience=3)

# ------- Train the Model -------
epochs = 20  # Increased epochs with early stopping
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // batch_size,
    validation_data=val_generator,
    validation_steps=val_generator.samples // batch_size,
    epochs=epochs,
    class_weight=class_weights,
    callbacks=[tensorboard_callback, checkpoint_callback, early_stopping]
)

# Save the final trained model.
os.makedirs('models', exist_ok=True)
model.save('models/screenshot_classifier_final.keras')

# ------- Evaluation Metrics -------
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def evaluate_model(model, generator):
    """Generate comprehensive evaluation metrics"""
    # Get true labels and predictions
    y_true = generator.classes
    y_pred = model.predict(generator).argmax(axis=1)
    
    # Classification report
    print("Classification Report:")
    print(classification_report(y_true, y_pred, target_names=generator.class_indices.keys()))
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', 
                xticklabels=generator.class_indices.keys(),
                yticklabels=generator.class_indices.keys())
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.savefig('reports/confusion_matrix.png')
    plt.close()
    
    # Save metrics to CSV
    report = classification_report(y_true, y_pred, 
                                 target_names=generator.class_indices.keys(),
                                 output_dict=True)
    pd.DataFrame(report).transpose().to_csv('reports/classification_metrics.csv')

# Create reports directory
os.makedirs('reports', exist_ok=True)

# Evaluate on validation set
print("\nValidation Set Evaluation:")
evaluate_model(model, val_generator)

# ------- Inference Function -------
def classify_screenshot(image_path, return_confidence=False):
    """
    Classify a screenshot and optionally return confidence scores.
    Args:
        image_path: Path to image file
        return_confidence: If True, returns (class, confidence) tuple
    Returns:
        Predicted class or (class, confidence) if return_confidence=True
    """
    image = load_img(image_path, target_size=(img_height, img_width))
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)
    prediction = model.predict(image)[0]
    
    classes = train_generator.class_indices
    inv_classes = {v: k for k, v in classes.items()}
    pred_idx = np.argmax(prediction)
    pred_class = inv_classes[pred_idx]
    confidence = float(prediction[pred_idx])
    
    if return_confidence:
        return pred_class, confidence
    return pred_class

def classify_batch(image_paths):
    """
    Classify multiple screenshots in batch.
    Args:
        image_paths: List of image file paths
    Returns:
        List of (filename, class, confidence) tuples
    """
    batch = []
    for path in image_paths:
        try:
            img = load_img(path, target_size=(img_height, img_width))
            img = img_to_array(img)
            batch.append(img)
        except Exception as e:
            print(f"Error loading {path}: {str(e)}")
            continue
            
    if not batch:
        return []
        
    batch = np.array(batch)
    batch = preprocess_input(batch)
    predictions = model.predict(batch)
    
    classes = train_generator.class_indices
    inv_classes = {v: k for k, v in classes.items()}
    results = []
    
    for i, path in enumerate(image_paths):
        if i >= len(predictions):
            break
        pred = predictions[i]
        pred_idx = np.argmax(pred)
        results.append((
            os.path.basename(path),
            inv_classes[pred_idx],
            float(pred[pred_idx])
        ))
    
    return results

# ------- Example Usage -------
if __name__ == '__main__':
    test_image = 'sample_screenshot.png'  # Replace with your screenshot path.
    result = classify_screenshot(test_image)
    print(f'Predicted category for {test_image}: {result}')
