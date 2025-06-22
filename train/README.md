# Model Training Scripts

This directory contains scripts for training the machine learning models used in the PreventWise application.

## Stroke Prediction Model

The stroke prediction model is trained using the `train_stroke_model.py` script. This script:

1. Loads and preprocesses the stroke dataset
2. Trains a Random Forest Classifier
3. Evaluates the model using cross-validation
4. Generates and saves visualization plots
5. Saves the trained model and scaler

### Prerequisites

Make sure you have all required dependencies installed:

```bash
pip install -r requirements.txt
```

### Dataset

Place the stroke dataset (`healthcare-dataset-stroke-data.csv`) in the `data` directory.

### Training the Model

To train the stroke prediction model, run:

```bash
python train_stroke_model.py
```

The script will:

1. Train the model using SMOTE for handling class imbalance
2. Perform cross-validation
3. Generate feature importance plot
4. Generate ROC curve plot
5. Save the model and scaler to the `models` directory

### Output Files

After training, the following files will be generated in the `models` directory:

- `stroke_model.pkl`: The trained model
- `scaler.pkl`: The feature scaler
- `stroke_feature_importance.png`: Plot showing feature importance
- `stroke_roc_curve.png`: ROC curve plot

### Model Performance

The model uses a threshold of 0.3 for prediction to prioritize recall (catching more potential stroke cases). The performance metrics will be printed during training.
