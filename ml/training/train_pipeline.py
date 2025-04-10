"""
train_pipeline.py

Orchestrates the complete training pipeline including:
- Data preparation
- Model training
- Evaluation
- Model deployment
"""

import os
import sys
from datetime import datetime
from screenshot_classifier import (
    train_generator,
    val_generator,
    model,
    evaluate_model
)
import tensorflow as tf

# Configuration
MODEL_DIR = 'models'
REPORT_DIR = 'reports'
LOG_DIR = 'logs/training'

def prepare_directories():
    """Create required directories"""
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

def train_model():
    """Train the model with callbacks"""
    # Callbacks
    callbacks = [
        tf.keras.callbacks.TensorBoard(
            log_dir=os.path.join(LOG_DIR, datetime.now().strftime("%Y%m%d-%H%M%S")),
            histogram_freq=1
        ),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(MODEL_DIR, 'best_model.keras'),
            save_best_only=True,
            monitor='val_accuracy',
            mode='max'
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        tf.keras.callbacks.CSVLogger(
            os.path.join(REPORT_DIR, 'training_log.csv')
        )
    ]

    # Train
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // train_generator.batch_size,
        validation_data=val_generator,
        validation_steps=val_generator.samples // val_generator.batch_size,
        epochs=50,
        callbacks=callbacks
    )

    return history

def evaluate_and_save():
    """Evaluate model and save reports"""
    # Evaluate
    print("\nEvaluating model...")
    evaluate_model(model, val_generator)

    # Save final model
    model.save(os.path.join(MODEL_DIR, 'production_model.keras'))
    print(f"Model saved to {MODEL_DIR}/production_model.keras")

def main():
    print("Starting training pipeline...")
    prepare_directories()
    train_model()
    evaluate_and_save()
    print("Training pipeline completed successfully")

if __name__ == '__main__':
    main()
