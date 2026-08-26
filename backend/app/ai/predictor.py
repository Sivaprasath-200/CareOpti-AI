import os
import joblib
import numpy as np
import pandas as pd
import shap
from typing import Dict, Any, Tuple, List

MODEL_PATH = os.path.join(os.path.dirname(__file__), "triage_xgboost.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "triage_scaler.pkl")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "triage_encoder.pkl")

class TriagePredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoder = None
        self.explainer = None
        self.feature_names = [
            'age', 'heart_rate', 'systolic_bp', 'diastolic_bp', 
            'respiratory_rate', 'oxygen_saturation', 'temperature', 
            'chest_pain', 'shortness_of_breath', 'fever', 
            'severe_bleeding', 'altered_consciousness'
        ]
        self._load_artifacts()

    def _load_artifacts(self):
        if not os.path.exists(MODEL_PATH):
            raise Exception("AI Triage Model not found. Please train it first.")
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        self.encoder = joblib.load(ENCODER_PATH)
        
        # Initialize SHAP TreeExplainer
        self.explainer = shap.TreeExplainer(self.model)

    def predict(self, input_data: Dict[str, Any]) -> Tuple[str, float, List[Dict[str, Any]]]:
        """
        Predicts triage severity and returns explanation.
        """
        # Prepare vector
        vec = []
        for f in self.feature_names:
            val = input_data.get(f, 0)
            vec.append(val if val is not None else 0)
            
        df = pd.DataFrame([vec], columns=self.feature_names)
        
        # Scale
        X_scaled = self.scaler.transform(df)
        
        # Predict
        probs = self.model.predict_proba(X_scaled)[0]
        class_idx = np.argmax(probs)
        confidence = float(probs[class_idx])
        severity = self.encoder.inverse_transform([class_idx])[0]
        
        # Explainability via SHAP
        shap_values = self.explainer.shap_values(X_scaled)
        
        # For multi-class XGBoost, shap_values is a list of arrays (one per class).
        # We look at the shap values for the predicted class.
        if isinstance(shap_values, list):
            class_shap = shap_values[class_idx][0]
        else:
            # Depending on shap version/model, it might be 3D array (samples, features, classes)
            if len(shap_values.shape) == 3:
                class_shap = shap_values[0, :, class_idx]
            else:
                class_shap = shap_values[0]
                
        # Zip features with their shap contribution
        contributions = []
        for feature_name, shap_val, actual_val in zip(self.feature_names, class_shap, df.iloc[0]):
            contributions.append({
                "feature": feature_name,
                "value": float(actual_val),
                "impact": float(shap_val)
            })
            
        # Sort by absolute impact descending
        contributions.sort(key=lambda x: abs(x["impact"]), reverse=True)
        top_factors = contributions[:5]
        
        return severity, confidence, top_factors

predictor_instance = None

def get_predictor() -> TriagePredictor:
    global predictor_instance
    if predictor_instance is None:
        predictor_instance = TriagePredictor()
    return predictor_instance
