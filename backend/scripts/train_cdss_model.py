import numpy as np
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

def generate_synthetic_data(n_samples=2000):
    np.random.seed(42)
    
    # 0 = Normal/Low, 1 = Moderate, 2 = High, 3 = Critical
    
    # Features
    age = np.random.randint(18, 90, n_samples)
    
    # Vitals
    hr = np.random.normal(80, 15, n_samples)
    sbp = np.random.normal(120, 20, n_samples)
    dbp = np.random.normal(80, 10, n_samples)
    rr = np.random.normal(16, 4, n_samples)
    spo2 = np.random.normal(97, 2, n_samples)
    temp = np.random.normal(37, 0.8, n_samples)
    
    # Labs (Synthetic)
    wbc = np.random.normal(7.5, 3.0, n_samples) # 4.5-11.0 normal
    creatinine = np.random.normal(1.0, 0.5, n_samples) # 0.7-1.3 normal
    bun = np.random.normal(15, 8, n_samples) # 7-20 normal
    
    # Comorbidities
    diabetes = np.random.binomial(1, 0.2, n_samples)
    hypertension = np.random.binomial(1, 0.3, n_samples)
    heart_failure = np.random.binomial(1, 0.05, n_samples)
    
    df = pd.DataFrame({
        'age': age,
        'heart_rate': hr,
        'systolic_bp': sbp,
        'diastolic_bp': dbp,
        'respiratory_rate': rr,
        'spo2': spo2,
        'temperature': temp,
        'wbc': wbc,
        'creatinine': creatinine,
        'bun': bun,
        'diabetes': diabetes,
        'hypertension': hypertension,
        'heart_failure': heart_failure
    })
    
    # Risk calculation heuristic for synthetic labels
    # Baseline risk
    risk_score = (age / 100) * 0.1
    
    # Vitals risk
    risk_score += np.where((hr > 110) | (hr < 50), 0.3, 0)
    risk_score += np.where((sbp < 90) | (sbp > 180), 0.3, 0)
    risk_score += np.where((rr > 24) | (rr < 10), 0.3, 0)
    risk_score += np.where(spo2 < 92, 0.5, 0)
    risk_score += np.where((temp > 39) | (temp < 35), 0.2, 0)
    
    # Labs risk
    risk_score += np.where((wbc > 15) | (wbc < 3), 0.2, 0)
    risk_score += np.where(creatinine > 2.0, 0.2, 0)
    
    # Comorb risk
    risk_score += heart_failure * 0.2
    
    # Add some noise
    risk_score += np.random.normal(0, 0.1, n_samples)
    
    # Map to classes
    labels = np.zeros(n_samples, dtype=int)
    labels[risk_score > 0.4] = 1 # MODERATE
    labels[risk_score > 0.8] = 2 # HIGH
    labels[risk_score > 1.2] = 3 # CRITICAL
    
    df['deterioration_risk'] = labels
    return df

def train_models():
    print("Generating synthetic data for CDSS...")
    df = generate_synthetic_data(3000)
    
    X = df.drop('deterioration_risk', axis=1)
    y = df['deterioration_risk']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("\n--- Training Logistic Regression Baseline ---")
    logreg = LogisticRegression(max_iter=1000)
    logreg.fit(X_train, y_train)
    
    lr_preds = logreg.predict(X_test)
    lr_probs = logreg.predict_proba(X_test)
    
    print(f"Accuracy:  {accuracy_score(y_test, lr_preds):.3f}")
    print(f"Precision: {precision_score(y_test, lr_preds, average='weighted'):.3f}")
    print(f"Recall:    {recall_score(y_test, lr_preds, average='weighted'):.3f}")
    print(f"F1-Score:  {f1_score(y_test, lr_preds, average='weighted'):.3f}")
    print(f"ROC-AUC:   {roc_auc_score(y_test, lr_probs, multi_class='ovr'):.3f}")
    
    print("\n--- Training XGBoost Primary Model ---")
    xgb_model = xgb.XGBClassifier(
        objective='multi:softprob', 
        num_class=4, 
        eval_metric='mlogloss',
        use_label_encoder=False,
        random_state=42
    )
    xgb_model.fit(X_train, y_train)
    
    xgb_preds = xgb_model.predict(X_test)
    xgb_probs = xgb_model.predict_proba(X_test)
    
    print(f"Accuracy:  {accuracy_score(y_test, xgb_preds):.3f}")
    print(f"Precision: {precision_score(y_test, xgb_preds, average='weighted'):.3f}")
    print(f"Recall:    {recall_score(y_test, xgb_preds, average='weighted'):.3f}")
    print(f"F1-Score:  {f1_score(y_test, xgb_preds, average='weighted'):.3f}")
    print(f"ROC-AUC:   {roc_auc_score(y_test, xgb_probs, multi_class='ovr'):.3f}")
    print("Confusion Matrix:\n", confusion_matrix(y_test, xgb_preds))
    
    # Save models
    os.makedirs('models', exist_ok=True)
    joblib.dump(logreg, 'models/cdss_deterioration_logreg.joblib')
    joblib.dump(xgb_model, 'models/cdss_deterioration_xgboost.joblib')
    print("\nModels saved to models/ directory.")

if __name__ == "__main__":
    train_models()
