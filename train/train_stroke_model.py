import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from pathlib import Path

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

def train_stroke_model():
    # Load & preprocess data
    data_path = Path(__file__).parent.parent / 'data' / 'healthcare-dataset-stroke-data.csv'
    df = pd.read_csv(data_path)
    df.drop('id', axis=1, inplace=True)
    df['bmi'] = df['bmi'].fillna(df['bmi'].median())

    # Encode categorical variables
    df = pd.get_dummies(df, columns=['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status'], drop_first=True)

    # Ensure all expected features are present
    expected_features = [
        'age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi',
        'gender_Male', 'ever_married_Yes',
        'work_type_Never_worked', 'work_type_Private', 'work_type_Self_employed', 'work_type_children',
        'Residence_type_Urban',
        'smoking_status_formerly_smoked', 'smoking_status_never_smoked', 'smoking_status_smokes'
    ]
    
    # Add any missing features with 0 values
    for feature in expected_features:
        if feature not in df.columns:
            df[feature] = 0

    # Ensure columns are in the correct order
    df = df[expected_features + ['stroke']]

    # Split data
    X = df.drop('stroke', axis=1)
    y = df['stroke']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    # Balance data with SMOTE
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_resampled)
    X_test_scaled = scaler.transform(X_test)

    # Train Random Forest with cross-validation
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=6,
        class_weight='balanced',
        random_state=42
    )

    # Cross-validation check
    cv_scores = cross_val_score(model, X_train_scaled, y_train_resampled, cv=5, scoring='f1')
    print(f"Cross-Validation F1 Scores: {cv_scores}")
    print(f"Mean F1: {np.mean(cv_scores):.2f}")

    # Final training
    model.fit(X_train_scaled, y_train_resampled)

    # Predict probabilities and tune threshold
    y_probs = model.predict_proba(X_test_scaled)[:, 1]
    y_pred_thresh = (y_probs > 0.3).astype(int)

    # Evaluation
    print("\nClassification Report (threshold = 0.3):")
    print(classification_report(y_test, y_pred_thresh))

    # Feature Importance Plot
    feature_importance = pd.Series(model.feature_importances_, index=X.columns)
    top_features = feature_importance.sort_values(ascending=False).head(10)

    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_features, y=top_features.index, palette="Blues_d")
    plt.title("Top 10 Important Features")
    plt.xlabel("Importance Score")
    plt.ylabel("Features")
    plt.tight_layout()
    
    # Save the plot
    plot_path = Path(__file__).parent.parent / 'models' / 'stroke_feature_importance.png'
    plt.savefig(plot_path)
    plt.close()

    # ROC Curve and AUC Score
    fpr, tpr, thresholds = roc_curve(y_test, y_probs)
    auc = roc_auc_score(y_test, y_probs)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'AUC = {auc:.2f}')
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray')
    plt.title("ROC Curve")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save the ROC curve plot
    roc_path = Path(__file__).parent.parent / 'models' / 'stroke_roc_curve.png'
    plt.savefig(roc_path)
    plt.close()

    # Save model, scaler, and feature names
    model_path = Path(__file__).parent.parent / 'models' / 'stroke_model.pkl'
    scaler_path = Path(__file__).parent.parent / 'models' / 'stroke_scaler.pkl'
    features_path = Path(__file__).parent.parent / 'models' / 'stroke_features.pkl'
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
        
    with open(features_path, 'wb') as f:
        pickle.dump(expected_features, f)

    print("\nModel and scaler saved successfully!")
    print(f"Model saved to: {model_path}")
    print(f"Scaler saved to: {scaler_path}")
    print(f"Features saved to: {features_path}")
    print(f"Feature importance plot saved to: {plot_path}")
    print(f"ROC curve plot saved to: {roc_path}")

if __name__ == "__main__":
    train_stroke_model() 