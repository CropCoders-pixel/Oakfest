import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
import logging

logger = logging.getLogger(__name__)

class WasteClassifier:
    def __init__(self, model_path):
        """Initialize the waste classifier with a TensorFlow model"""
        try:
            self.model = tf.saved_model.load(model_path)
            self.class_names = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
            self.last_confidence = 0.0
            logger.info(f"Successfully loaded waste classification model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model from {model_path}: {str(e)}")
            raise
        
    def preprocess_image(self, image_data):
        """Preprocess image for model input"""
        try:
            # Convert bytes to PIL Image if needed
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = Image.open(image_data)
                
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Resize to model's expected size
            image = image.resize((224, 224))
            
            # Convert to numpy array and normalize
            img_array = tf.keras.preprocessing.image.img_to_array(image)
            img_array = tf.expand_dims(img_array, 0)
            
            # Normalize to [0,1]
            img_array = img_array / 255.0
            
            return img_array
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            raise
        
    def classify_image(self, image_data):
        """Classify waste type from image"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_data)
            
            # Get predictions
            predictions = self.model(processed_image)
            
            if isinstance(predictions, dict):
                predictions = predictions['predictions']
                
            # Convert to numpy if needed
            if tf.is_tensor(predictions):
                predictions = predictions.numpy()
            
            # Get the predicted class and confidence
            class_idx = np.argmax(predictions[0])
            self.last_confidence = float(predictions[0][class_idx])
            
            # Get the class name
            predicted_class = self.class_names[class_idx]
            
            logger.info(f"Image classified as {predicted_class} with confidence {self.last_confidence}")
            return predicted_class
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            raise
            
    def get_confidence(self):
        """Get the confidence score of the last prediction"""
        return self.last_confidence
        
    def get_top_predictions(self, predictions, top_k=3):
        """Get top k predictions with their confidence scores"""
        if tf.is_tensor(predictions):
            predictions = predictions.numpy()
            
        # Get indices of top k predictions
        top_indices = np.argsort(predictions[0])[-top_k:][::-1]
        
        return [
            {
                'class': self.class_names[idx],
                'confidence': float(predictions[0][idx])
            }
            for idx in top_indices
        ]
