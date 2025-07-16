#random forest

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Load dataset
data = pd.read_csv('model/data.csv')

# Clean and preprocess data
data = data.dropna(subset=['medicine'])

# Combine symptoms into a single feature
def combine_symptoms(row):
    symptoms = [row.get('symptom1', 'null'), row.get('symptom2', 'null'), row.get('symptom3', 'null')]
    symptoms = [sym.lower() if pd.notna(sym) else "null" for sym in symptoms]  # Ensure 'null' for missing values
    return ' '.join(symptoms)

data['combined_symptoms'] = data.apply(combine_symptoms, axis=1)

# Prepare features and target
X = data['combined_symptoms']
y = data['medicine']

# Split data with no stratification
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create pipeline with TF-IDF and Random Forest Classifier
model = make_pipeline(
    TfidfVectorizer(stop_words='english', ngram_range=(1,2)),
    RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced', n_jobs=-1)
)

# Hyperparameter tuning with GridSearchCV
param_grid = {
    'randomforestclassifier__n_estimators': [100, 200, 300],  # Number of trees
    'randomforestclassifier__max_depth': [None, 10, 20],  # Tree depth
    'randomforestclassifier__min_samples_split': [2, 5, 10],  # Min samples to split a node
    'randomforestclassifier__min_samples_leaf': [1, 2, 4]  # Min samples in leaf nodes
}

grid_search = GridSearchCV(model, param_grid, cv=5, n_jobs=-1, verbose=0)
print("\033[92mPlease wait... Model is training. This may take up to a minute.\033[0m\n")
grid_search.fit(X_train, y_train)

# Best parameters
print(f"Best parameters: {grid_search.best_params_}")

# Get the best model
best_model = grid_search.best_estimator_

# Predict and evaluate
y_pred = best_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'Model accuracy: {accuracy * 100:.2f}%')

# Detailed classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save the model
joblib.dump(best_model, 'model.pkl')
print("Model training complete and saved.")
