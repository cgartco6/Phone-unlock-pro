import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Any

class SelfHealingModel(nn.Module):
    """Neural network for predicting system failures and recommending fixes"""
    
    def __init__(self, input_size: int, hidden_size: int, num_classes: int):
        super(SelfHealingModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc3 = nn.Linear(hidden_size // 2, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

class RiskAssessor:
    """AI model for assessing unlock risks"""
    
    def __init__(self, model_path: str = None):
        self.risk_factors = {
            'brick_risk': 0.0,
            'data_loss_risk': 0.0,
            'warranty_void_risk': 0.0,
            'time_estimate': 0.0
        }
        
    def assess_unlock_risk(self, phone_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks for phone unlock operation"""
        model = phone_data.get('model', '').upper()
        lock_type = phone_data.get('lock_type', 'unknown')
        
        # Base risks
        base_risks = {
            'brick_risk': 0.1,
            'data_loss_risk': 0.3,
            'warranty_void_risk': 0.8,
            'time_estimate': 30  # minutes
        }
        
        # Model-specific adjustments
        if 'HLTE230E' in model:  # Hisense H40 Lite
            base_risks.update({
                'brick_risk': 0.05,  # Lower brick risk for Hisense
                'data_loss_risk': 0.9,  # High data loss (usually requires flash)
                'time_estimate': 45
            })
        elif 'SAMSUNG' in model:
            base_risks.update({
                'brick_risk': 0.15,  # KG lock risks
                'data_loss_risk': 0.6,
                'time_estimate': 25
            })
        elif 'IPHONE' in model:
            base_risks.update({
                'brick_risk': 0.02,  # iPhones are hard to brick
                'data_loss_risk': 0.1,
                'time_estimate': 60
            })
        
        # Lock type adjustments
        if lock_type == 'frp':
            base_risks['data_loss_risk'] = 0.1
        elif lock_type == 'kg_lock':
            base_risks['brick_risk'] = 0.3
        elif lock_type == 'bootloader':
            base_risks['warranty_void_risk'] = 0.95
        
        # Calculate overall risk level
        overall_risk = (base_risks['brick_risk'] * 0.4 + 
                       base_risks['data_loss_risk'] * 0.3 + 
                       base_risks['warranty_void_risk'] * 0.3)
        
        risk_level = 'low' if overall_risk < 0.3 else 'medium' if overall_risk < 0.6 else 'high'
        
        return {
            'risk_factors': base_risks,
            'overall_risk': overall_risk,
            'risk_level': risk_level,
            'assessment_confidence': 0.85,
            'recommendations': self._generate_risk_recommendations(base_risks, risk_level),
            'mitigation_strategies': self._get_mitigation_strategies(base_risks)
        }
    
    def _generate_risk_recommendations(self, risks: Dict[str, float], risk_level: str) -> List[str]:
        """Generate risk-based recommendations"""
        recommendations = []
        
        if risks['brick_risk'] > 0.2:
            recommendations.append("Have backup device ready")
            recommendations.append("Use stable power source")
            
        if risks['data_loss_risk'] > 0.5:
            recommendations.append("Backup data if possible")
            recommendations.append("Inform user about data loss")
            
        if risks['warranty_void_risk'] > 0.7:
            recommendations.append("Check warranty status first")
            recommendations.append("Get user consent for warranty void")
            
        if risk_level == 'high':
            recommendations.append("Consider professional service")
            recommendations.append("Use most reliable method only")
            
        return recommendations
    
    def _get_mitigation_strategies(self, risks: Dict[str, float]) -> List[Dict[str, Any]]:
        """Get strategies to mitigate identified risks"""
        strategies = []
        
        if risks['brick_risk'] > 0.15:
            strategies.append({
                'risk': 'brick_risk',
                'strategy': 'Use test point method for recovery',
                'effectiveness': 0.8
            })
            
        if risks['data_loss_risk'] > 0.4:
            strategies.append({
                'risk': 'data_loss_risk', 
                'strategy': 'Attempt ADB backup first',
                'effectiveness': 0.3
            })
            
        return strategies

class FailurePredictor:
    """AI model for predicting system failures"""
    
    def __init__(self):
        self.failure_patterns = self._load_failure_patterns()
    
    def predict_failures(self, system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Predict potential system failures"""
        predictions = []
        
        # CPU-based predictions
        if system_metrics.get('cpu_percent', 0) > 85:
            predictions.append({
                'component': 'cpu',
                'failure_type': 'performance_degradation',
                'probability': 0.7,
                'timeframe': '24 hours',
                'suggestion': 'Reduce concurrent operations'
            })
        
        # Memory-based predictions
        if system_metrics.get('memory_percent', 0) > 90:
            predictions.append({
                'component': 'memory',
                'failure_type': 'out_of_memory',
                'probability': 0.6,
                'timeframe': '12 hours',
                'suggestion': 'Clear memory cache or add swap'
            })
        
        # Disk-based predictions
        if system_metrics.get('disk_percent', 0) > 95:
            predictions.append({
                'component': 'storage',
                'failure_type': 'out_of_space',
                'probability': 0.9,
                'timeframe': 'immediate',
                'suggestion': 'Clean up temporary files'
            })
        
        # Tool-specific predictions
        tool_health = system_metrics.get('tool_health', {})
        for tool, health in tool_health.items():
            if health.get('status') != 'healthy':
                predictions.append({
                    'component': f'tool_{tool}',
                    'failure_type': 'tool_malfunction',
                    'probability': 0.8,
                    'timeframe': 'next_use',
                    'suggestion': f'Restart {tool} or reinstall'
                })
        
        return {
            'predictions': predictions,
            'overall_risk': len(predictions) / 10.0,  # Normalize
            'preventive_actions': self._get_preventive_actions(predictions)
        }
    
    def _load_failure_patterns(self) -> Dict[str, Any]:
        """Load historical failure patterns"""
        return {
            'high_cpu_usage': {
                'leads_to': ['timeout_errors', 'slow_response'],
                'recovery': ['restart_services', 'reduce_load'],
                'prevention': ['monitor_usage', 'set_limits']
            },
            'low_disk_space': {
                'leads_to': ['write_failures', 'corruption'],
                'recovery': ['clean_temporary', 'expand_storage'],
                'prevention': ['regular_cleanup', 'monitor_usage']
            },
            'tool_crash': {
                'leads_to': ['unlock_failures', 'data_loss'],
                'recovery': ['restart_tool', 'reinstall'],
                'prevention': ['regular_updates', 'health_checks']
            }
        }
    
    def _get_preventive_actions(self, predictions: List[Dict[str, Any]]) -> List[str]:
        """Get preventive actions based on predictions"""
        actions = []
        
        for prediction in predictions:
            component = prediction['component']
            failure_type = prediction['failure_type']
            
            if 'cpu' in component:
                actions.append("Schedule resource-intensive tasks during low usage")
            elif 'memory' in component:
                actions.append("Implement memory usage limits")
            elif 'storage' in component:
                actions.append("Set up automatic cleanup of temporary files")
            elif 'tool' in component:
                actions.append(f"Schedule regular health checks for {component}")
        
        return list(set(actions))  # Remove duplicates
