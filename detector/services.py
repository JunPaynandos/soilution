import os
import numpy as np
import joblib
import tensorflow as tf
from django.conf import settings

class CropService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoder = None
        self.model_path = os.path.join(settings.BASE_DIR, 'detector', 'ml_models', 'crop_recommendation_model_v3.keras')
        self.scaler_path = os.path.join(settings.BASE_DIR, 'detector', 'ml_models', 'scaler.pkl')
        self.encoder_path = os.path.join(settings.BASE_DIR, 'detector', 'ml_models', 'encoder.pkl')
        self._load_resources()

    def _load_resources(self):
        """Load model and preprocessors if they exist."""
        try:
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                print("Keras model loaded successfully.")
            else:
                print(f"Model file not found at {self.model_path}")

            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
                print("Scaler loaded successfully.")
            else:
                print(f"Scaler file not found at {self.scaler_path}")

            if os.path.exists(self.encoder_path):
                self.encoder = joblib.load(self.encoder_path)
                print("Encoder loaded successfully.")
            else:
                print(f"Encoder file not found at {self.encoder_path}")

        except Exception as e:
            print(f"Error loading ML resources: {e}")

    def get_crop_recommendations(self, nitrogen, phosphorus, potassium, temperature, moisture, ph, conductivity):
        """
        Predict crop recommendations based on soil parameters.
        Returns a list of dictionaries with crop name and confidence.
        """
        if not all([self.model, self.scaler, self.encoder]):
            return [{"name": "Error", "confidence": 0, "message": "ML resources not loaded"}]

        try:
            # Prepare input array in the correct order
            # IMPORTANT: Ensure this order matches exactly what was used during training
            # Based on your snippet: N, P, K, Temp, Moisture, pH, Conductivity
            input_data = np.array([[nitrogen, phosphorus, potassium, temperature, moisture, ph, conductivity]])
            
            # Scale the features
            input_scaled = self.scaler.transform(input_data)
            
            # Predict
            prediction_probs = self.model.predict(input_scaled)
            
            # Get all predictions
            all_indices = np.argsort(prediction_probs[0])[::-1]
            
            recommendations = []
            for idx in all_indices:
                confidence = float(prediction_probs[0][idx]) * 100
                
                if confidence > 0:
                    # Assuming OneHotEncoder based on your snippet: target_names=encoder.categories_[0]
                    if hasattr(self.encoder, 'categories_'):
                        crop_name = self.encoder.categories_[0][idx]
                    elif hasattr(self.encoder, 'classes_'):
                        crop_name = self.encoder.classes_[idx]
                    else:
                        crop_name = f"Crop {idx}"

                    recommendations.append({
                        "name": crop_name,
                        "confidence": round(confidence, 2)
                    })
            
            # Return top 5
            return recommendations[:5]

        except Exception as e:
            print(f"Prediction error: {e}")
            return [{"name": "Error", "confidence": 0, "message": str(e)}]

class SoilService:
    def analyze_soil(self, nitrogen, phosphorus, potassium, temperature, moisture, ph, conductivity):
        """
        Analyze soil health based on parameters.
        """
        status = "Healthy"
        issues = []

        # Simple rule-based analysis (Customize these thresholds)
        if nitrogen < 20:
            issues.append("Low Nitrogen")
        elif nitrogen > 100:
            issues.append("High Nitrogen")

        if phosphorus < 20:
            issues.append("Low Phosphorus")
        
        if potassium < 20:
            issues.append("Low Potassium")

        if ph < 5.5:
            issues.append("Acidic Soil")
        elif ph > 7.5:
            issues.append("Alkaline Soil")

        if issues:
            status = "Needs Attention"

        return {
            "status": status,
            "issues": issues,
            "details": f"Soil is {status.lower()}. {', '.join(issues)}."
        }

# Create singleton instances
crop_service = CropService()
soil_service = SoilService()
