import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from typing import Tuple, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class DataLoader:
    def __init__(self, data_path: str = None):
        self.data_path = data_path or os.path.join('server', 'data', 'youtube_comments.csv')
        self.label_encoder = LabelEncoder()
        self.train_val_test_split = tuple(map(float, os.getenv('TRAIN_VAL_TEST_SPLIT', '0.7,0.15,0.15').split(',')))
        
    def load_data(self) -> pd.DataFrame:
        """Load data from CSV or MongoDB"""
        if os.path.exists(self.data_path):
    
            df = pd.read_csv(self.data_path)
            
            # Verify required columns
            required_columns = ['text', 'sentiment']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
                
            return df
        else:
            raise FileNotFoundError(f"Data file not found at {self.data_path}. Please place your CSV file in the server/data directory.")
    
    def preprocess_text(self, text: str) -> str:
        """Basic text preprocessing"""
        if not isinstance(text, str):
            return ""
        text = text.lower().strip()
        # Add more preprocessing steps as needed
        return text
    
    def prepare_data(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Prepare data for training and evaluation"""
        # Load and preprocess data
        df = self.load_data()
        df['processed_text'] = df['text'].apply(self.preprocess_text)
        
        # Encode labels
        df['label'] = self.label_encoder.fit_transform(df['sentiment'])
        
        # Split data
        train_ratio, val_ratio, test_ratio = self.train_val_test_split
        val_test_ratio = val_ratio / (val_ratio + test_ratio)
        
        train_df, temp_df = train_test_split(df, train_size=train_ratio, random_state=42)
        val_df, test_df = train_test_split(temp_df, train_size=val_test_ratio, random_state=42)
        
        return {
            'train': train_df,
            'val': val_df,
            'test': test_df
        }, {
            'label_encoder': self.label_encoder,
            'label_mapping': dict(zip(self.label_encoder.classes_, self.label_encoder.transform(self.label_encoder.classes_)))
        }
    
    def get_class_weights(self, labels: np.ndarray) -> Dict[int, float]:
        """Calculate class weights for imbalanced datasets"""
        class_counts = np.bincount(labels)
        total_samples = len(labels)
        class_weights = {i: total_samples / (len(class_counts) * count) 
                        for i, count in enumerate(class_counts)}
        return class_weights 