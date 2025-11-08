import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any

class PhoneDetectionModel(nn.Module):
    """Neural network for phone model detection"""
    
    def __init__(self, input_size: int, hidden_size: int, num_classes: int):
        super(PhoneDetectionModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc3 = nn.Linear(hidden_size // 2, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

class PhoneDetectionAI:
    def __init__(self, model_path: str = None):
        self.model = None
        self.classes = []
        self.feature_names = []
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load trained model"""
        try:
            checkpoint = torch.load(model_path)
            self.model = PhoneDetectionModel(
                input_size=checkpoint['input_size'],
                hidden_size=checkpoint['hidden_size'],
                num_classes=checkpoint['num_classes']
            )
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.classes = checkpoint['classes']
            self.feature_names = checkpoint['feature_names']
            self.model.eval()
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def predict_phone(self, usb_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict phone model from USB data"""
        if not self.model:
            return {'error': 'Model not loaded'}
        
        try:
            # Extract features from USB data
            features = self._extract_features(usb_data)
            features_tensor = torch.FloatTensor(features).unsqueeze(0)
            
            with torch.no_grad():
                outputs = self.model(features_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            predicted_class = self.classes[predicted.item()]
            
            return {
                'predicted_model': predicted_class,
                'confidence': confidence.item(),
                'all_probabilities': {
                    cls: prob.item() for cls, prob in zip(self.classes, probabilities[0])
                }
            }
        except Exception as e:
            return {'error': f'Prediction failed: {e}'}
    
    def _extract_features(self, usb_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from USB detection data"""
        features = []
        
        # Vendor ID feature
        if 'vendor_id' in usb_data:
            features.append(int(usb_data['vendor_id'], 16))
        else:
            features.append(0)
        
        # Product ID feature
        if 'product_id' in usb_data:
            features.append(int(usb_data['product_id'], 16))
        else:
            features.append(0)
        
        # Add more features based on available data
        features.extend([0] * (len(self.feature_names) - len(features)))
        
        return np.array(features[:len(self.feature_names)])
