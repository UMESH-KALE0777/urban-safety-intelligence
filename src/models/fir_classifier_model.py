import pandas as pd
import numpy as np
import pickle
import os
import re
import logging
from typing import Tuple, List, Optional
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_data(file_path: str) -> pd.DataFrame:
    """Load dataset from the specified path."""
    try:
        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path, low_memory=False)
        
        # take only 10,000 rows
        df = df.sample(n=10000, random_state=42)
        
        if 'text' not in df.columns or 'crime_type' not in df.columns:
            # specifically for the fir_dataset.csv structure
            if 'ActSection' in df.columns and 'CrimeGroup_Name' in df.columns:
                logger.info("Mapping 'ActSection' to 'text' and 'CrimeGroup_Name' to 'crime_type'")
                df = df.rename(columns={'ActSection': 'text', 'CrimeGroup_Name': 'crime_type'})
            else:
                raise ValueError("Dataset must contain 'text' and 'crime_type' columns.")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def clean_text(text: str) -> str:
    """Clean the raw text."""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

label_map = {
    "theft": "theft",
    "robbery": "theft",
    "burglary": "theft",
    "snatching": "theft",

    "assault": "assault",
    "hurt": "assault",

    "fraud": "fraud",
    "cheating": "fraud",
    "cyber": "fraud",

    "harassment": "harassment",
    "outraging modesty": "harassment",

    "murder": "violent",
    "kidnapping": "violent"
}

def map_labels(df):

    def map_category(text):
        text = str(text).lower()

        for key in label_map:
            if key in text:
                return label_map[key]

        return "other"

    df["crime_type"] = df["crime_type"].apply(map_category)

    return df

def preprocess_data(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """Clean text, remove nulls, and split features/labels."""
    logger.info("Preprocessing data")
    df = df.dropna(subset=['text', 'crime_type']).copy()
    
    df["text"] = df["text"].str.lower()
    
    df = map_labels(df)
    
    # Remove "other" class (optional but improves accuracy)
    df = df[df["crime_type"] != "other"]
    
    print(df["crime_type"].value_counts())
    
    df['text_clean'] = df['text'].apply(clean_text)
    
    # Remove rows that became empty after cleaning
    df = df[df['text_clean'] != ""]
    
    return df['text_clean'], df['crime_type']

def build_pipeline(
    text_data: pd.Series, 
    labels: pd.Series, 
    max_features: int = 3000, 
    test_size: float = 0.2, 
    random_state: int = 42
) -> Tuple[LogisticRegression, TfidfVectorizer, float]:
    """Train the TF-IDF vectorizer and Logistic Regression model, evaluate its accuracy."""
    logger.info("Splitting data into train and test sets")
    
    X_train, X_test, y_train, y_test = train_test_split(
        text_data, labels, test_size=test_size, random_state=random_state
    )
    
    logger.info("Fitting TF-IDF vectorizer")
    vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english', ngram_range=(1,2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    logger.info("Training Logistic Regression model")
    model = LogisticRegression(random_state=random_state, max_iter=200)
    model.fit(X_train_vec, y_train)
    
    logger.info("Evaluating model")
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    
    return model, vectorizer, accuracy

def save_artifacts(model: LogisticRegression, vectorizer: TfidfVectorizer, model_path: str, vectorizer_path: str) -> None:
    """Save the trained model and vectorizer to disk."""
    try:
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        os.makedirs(os.path.dirname(vectorizer_path), exist_ok=True)
        
        logger.info(f"Saving model to {model_path}")
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
            
        logger.info(f"Saving vectorizer to {vectorizer_path}")
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)
            
        logger.info("Artifacts saved successfully")
    except Exception as e:
        logger.error(f"Error saving artifacts: {e}")
        raise

def predict(text: str, model: LogisticRegression, vectorizer: TfidfVectorizer) -> str:
    """Predict the crime type for a given raw text."""
    cleaned = clean_text(text)
    if not cleaned:
        raise ValueError("Input text is empty after cleaning.")
    
    vec = vectorizer.transform([cleaned])
    prediction = model.predict(vec)[0]
    return prediction

def load_artifacts(model_path: str, vectorizer_path: str) -> Tuple[LogisticRegression, TfidfVectorizer]:
    """Load trained model and vectorizer from disk."""
    try:
        logger.info("Loading model and vectorizer artifacts")
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        return model, vectorizer
    except Exception as e:
        logger.error(f"Error loading artifacts: {e}")
        raise

if __name__ == "__main__":
    # Define paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'fir_dataset.csv')
    MODEL_DIR = os.path.join(BASE_DIR, 'models')
    MODEL_PATH = os.path.join(MODEL_DIR, 'fir_model.pkl')
    VECTORIZER_PATH = os.path.join(MODEL_DIR, 'vectorizer.pkl')

    try:
        if not os.path.exists(DATA_PATH):
            logger.warning(f"Dataset not found at {DATA_PATH}. Please ensure the data file exists to train the model.")
        else:
            # 1. Load Data
            df = load_data(DATA_PATH)
            
            # 2. Preprocess Data
            X, y = preprocess_data(df)
            
            # 3. Build and Evaluate Model
            if len(X) > 0:
                model, vectorizer, accuracy = build_pipeline(X, y)
                logger.info("====================================")
                logger.info("   Model Training Completed         ")
                logger.info("====================================")
                logger.info(f"Training/Validation Accuracy: {accuracy:.4f}")
                
                # 4. Save Artifacts
                save_artifacts(model, vectorizer, MODEL_PATH, VECTORIZER_PATH)
                
                # 5. Make a Sample Prediction
                sample_text = "Thieves broke into the house from the back door and stole gold jewelry and cash."
                logger.info("====================================")
                logger.info(f"Sample Input: '{sample_text}'")
                pred = predict(sample_text, model, vectorizer)
                logger.info(f"Predicted Crime Type: {pred}")
                logger.info("====================================")
            else:
                logger.error("No valid data available after preprocessing.")
            
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
