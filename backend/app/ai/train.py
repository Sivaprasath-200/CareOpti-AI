import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
import xgboost as xgb

from app.ai.dataset import generate_synthetic_triage_data

def train_triage_models():
    print("--- Phase 4: AI Triage Model Training ---")
    print("1. Generating Synthetic Dataset...")
    df = generate_synthetic_triage_data(3000)
    
    # Features and Target
    X = df.drop(columns=['severity'])
    y_raw = df['severity']
    
    # Encode target labels
    le = LabelEncoder()
    # Ensure strict ordering if we want, or just let LabelEncoder sort them.
    # Actually for classification metrics we just need consistent encoding.
    y = le.fit_transform(y_raw)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("2. Scaling Features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("\n3. Training Logistic Regression (Interpretable Baseline)...")
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train_scaled, y_train)
    lr_preds = lr.predict(X_test_scaled)
    print("Logistic Regression Accuracy:", accuracy_score(y_test, lr_preds))
    
    print("\n4. Training XGBoost (Primary Model)...")
    xgb_clf = xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
        use_label_encoder=False,
        eval_metric='mlogloss'
    )
    # XGBoost handles scaled or unscaled fine, but let's use scaled for consistency
    xgb_clf.fit(X_train_scaled, y_train)
    xgb_preds = xgb_clf.predict(X_test_scaled)
    
    print("\n==================================================")
    print("XGBOOST MODEL EVALUATION (Synthetic Data ONLY)")
    print("==================================================")
    acc = accuracy_score(y_test, xgb_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, xgb_preds, average='weighted')
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    
    # Detailed report
    target_names = le.inverse_transform(np.unique(y))
    print("\nDetailed Report:\n", classification_report(y_test, xgb_preds, target_names=target_names))
    
    print("\n5. Saving Model Artifacts...")
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    model_path = os.path.join(os.path.dirname(__file__), "triage_xgboost.pkl")
    scaler_path = os.path.join(os.path.dirname(__file__), "triage_scaler.pkl")
    encoder_path = os.path.join(os.path.dirname(__file__), "triage_encoder.pkl")
    
    joblib.dump(xgb_clf, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(le, encoder_path)
    print(f"Models saved to {os.path.dirname(__file__)}")

if __name__ == "__main__":
    train_triage_models()
