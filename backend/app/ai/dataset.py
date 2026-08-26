import pandas as pd
import numpy as np
import random

def generate_synthetic_triage_data(num_samples=2000):
    np.random.seed(42)
    random.seed(42)

    data = []
    
    # 5 target classes
    categories = ['EMERGENCY', 'CRITICAL', 'HIGH', 'MODERATE', 'LOW']
    
    for _ in range(num_samples):
        # Determine base category to generate realistic cluster
        cat = random.choices(categories, weights=[0.1, 0.15, 0.25, 0.3, 0.2])[0]
        
        age = np.random.randint(18, 90)
        
        # Base vital signs
        hr = np.random.normal(75, 10)
        sys_bp = np.random.normal(120, 15)
        dia_bp = np.random.normal(80, 10)
        rr = np.random.normal(16, 2)
        spo2 = np.random.normal(98, 1)
        temp = np.random.normal(37.0, 0.4)
        
        # Base symptoms
        chest_pain = 0
        sob = 0 # shortness of breath
        fever = 0
        bleeding = 0
        consciousness_altered = 0
        
        # Mutate based on category to create separability
        if cat == 'EMERGENCY':
            if random.random() > 0.5:
                hr = np.random.uniform(130, 180) # Tachycardia
                chest_pain = 1
            else:
                spo2 = np.random.uniform(70, 85) # Severe hypoxia
                sob = 1
            if random.random() > 0.7:
                consciousness_altered = 1
                
        elif cat == 'CRITICAL':
            if random.random() > 0.5:
                sys_bp = np.random.uniform(70, 90) # Hypotension
                bleeding = 1
            else:
                spo2 = np.random.uniform(85, 92)
                sob = 1
                
        elif cat == 'HIGH':
            if random.random() > 0.5:
                temp = np.random.uniform(39.0, 41.0) # High fever
                hr = np.random.uniform(100, 120)
                fever = 1
            else:
                sys_bp = np.random.uniform(160, 200) # Hypertension
                
        elif cat == 'MODERATE':
            if random.random() > 0.7:
                temp = np.random.uniform(37.5, 38.5)
                fever = 1
            
        elif cat == 'LOW':
            # Keep vitals normal
            pass

        # Noise
        if random.random() > 0.95: chest_pain = 1
        if random.random() > 0.95: sob = 1
        if random.random() > 0.95: fever = 1
        if random.random() > 0.98: bleeding = 1

        data.append({
            'age': age,
            'heart_rate': hr,
            'systolic_bp': sys_bp,
            'diastolic_bp': dia_bp,
            'respiratory_rate': rr,
            'oxygen_saturation': spo2,
            'temperature': temp,
            'chest_pain': chest_pain,
            'shortness_of_breath': sob,
            'fever': fever,
            'severe_bleeding': bleeding,
            'altered_consciousness': consciousness_altered,
            'severity': cat
        })
        
    df = pd.DataFrame(data)
    
    # Optional clipping to realistic physiological bounds
    df['heart_rate'] = df['heart_rate'].clip(30, 250)
    df['systolic_bp'] = df['systolic_bp'].clip(50, 250)
    df['diastolic_bp'] = df['diastolic_bp'].clip(30, 150)
    df['respiratory_rate'] = df['respiratory_rate'].clip(8, 50)
    df['oxygen_saturation'] = df['oxygen_saturation'].clip(50, 100)
    df['temperature'] = df['temperature'].clip(32.0, 42.0)
    
    return df

if __name__ == "__main__":
    df = generate_synthetic_triage_data(2000)
    print(df.head())
    print(df['severity'].value_counts())
    df.to_csv("triage_dataset.csv", index=False)
