import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
from typing import Dict, List, Any

class UnlockRecommenderAI:
    """AI model for recommending unlock methods"""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.label_encoders = {}
        self.feature_columns = [
            'brand', 'model', 'android_version', 'lock_type', 
            'bootloader_status', 'kg_lock_status'
        ]
        
        if model_path:
            self.load_model(model_path)
        else:
            self.initialize_model()
    
    def initialize_model(self):
        """Initialize the recommendation model"""
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
    
    def train(self, training_data: pd.DataFrame):
        """Train the recommendation model"""
        # Prepare features and target
        X = self._prepare_features(training_data)
        y = training_data['recommended_method']
        
        # Train the model
        self.model.fit(X, y)
    
    def recommend_method(self, phone_info: Dict[str, Any], lock_type: str) -> Dict[str, Any]:
        """Recommend unlock method for given phone and lock"""
        try:
            # Prepare input features
            input_data = self._create_input_features(phone_info, lock_type)
            
            # Get prediction
            method_prediction = self.model.predict(input_data)[0]
            probabilities = self.model.predict_proba(input_data)[0]
            
            # Get confidence scores
            confidence = max(probabilities)
            
            return {
                'recommended_method': method_prediction,
                'confidence': confidence,
                'alternative_methods': self._get_alternatives(probabilities),
                'reasoning': self._generate_reasoning(phone_info, method_prediction)
            }
        except Exception as e:
            return {
                'recommended_method': 'generic_frp_bypass',
                'confidence': 0.5,
                'error': str(e)
            }
    
    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for training/prediction"""
        X = data[self.feature_columns].copy()
        
        # Encode categorical variables
        for column in self.feature_columns:
            if X[column].dtype == 'object':
                if column not in self.label_encoders:
                    self.label_encoders[column] = LabelEncoder()
                X[column] = self.label_encoders[column].fit_transform(X[column])
        
        return X
    
    def _create_input_features(self, phone_info: Dict[str, Any], lock_type: str) -> pd.DataFrame:
        """Create input features for prediction"""
        features = {
            'brand': phone_info.get('brand', 'unknown'),
            'model': phone_info.get('model', 'unknown'),
            'android_version': phone_info.get('android_version', 'unknown'),
            'lock_type': lock_type,
            'bootloader_status': phone_info.get('bootloader_status', 'locked'),
            'kg_lock_status': phone_info.get('kg_lock_status', 'unknown')
        }
        
        return pd.DataFrame([features])
    
    def _get_alternatives(self, probabilities: np.ndarray) -> List[Dict[str, Any]]:
        """Get alternative methods based on probabilities"""
        alternatives = []
        class_names = self.model.classes_
        
        # Sort by probability (descending)
        sorted_indices = np.argsort(probabilities)[::-1]
        
        for i in range(1, min(4, len(sorted_indices))):  # Top 3 alternatives
            idx = sorted_indices[i]
            alternatives.append({
                'method': class_names[idx],
                'confidence': probabilities[idx]
            })
        
        return alternatives
    
    def _generate_reasoning(self, phone_info: Dict[str, Any], method: str) -> str:
        """Generate reasoning for the recommendation"""
        brand = phone_info.get('brand', '').lower()
        
        reasoning_templates = {
            'samsung': f"Recommended {method} for Samsung device due to high success rate with KG lock handling.",
            'xiaomi': f"Recommended {method} for Xiaomi device considering bootloader unlock requirements.",
            'huawei': f"Recommended {method} for Huawei device accounting for recent security patches.",
            'generic': f"Recommended {method} as general solution with broad compatibility."
        }
        
        return reasoning_templates.get(brand, reasoning_templates['generic'])
    
    def save_model(self, path: str):
        """Save trained model"""
        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, path)
    
    def load_model(self, path: str):
        """Load trained model"""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.label_encoders = model_data['label_encoders']
        self.feature_columns = model_data['feature_columns']
