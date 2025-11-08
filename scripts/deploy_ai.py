#!/usr/bin/env python3
"""
AI Deployment Script for Phone Unlock System
Deploys and activates all AI models
"""

import os
import sys
import logging
import argparse
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AIDeployer:
    def __init__(self):
        self.setup_logging()
        self.deployment_status = {}
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ai_deployment.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AIDeployer')
    
    def deploy_all_ai(self) -> Dict[str, Any]:
        """Deploy all AI models and agents"""
        self.logger.info("Starting AI deployment...")
        
        deployment_steps = [
            self.deploy_phone_detection_ai,
            self.deploy_unlock_recommender_ai,
            self.deploy_self_healing_ai,
            self.deploy_multi_agent_system,
            self.deploy_risk_assessment_ai,
            self.activate_ai_orchestrator
        ]
        
        for step in deployment_steps:
            try:
                step_name = step.__name__
                self.logger.info(f"Executing: {step_name}")
                result = step()
                self.deployment_status[step_name] = {
                    'status': 'success',
                    'result': result
                }
            except Exception as e:
                self.logger.error(f"Failed {step_name}: {str(e)}")
                self.deployment_status[step_name] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        return self._generate_deployment_report()
    
    def deploy_phone_detection_ai(self) -> Dict[str, Any]:
        """Deploy phone detection AI model"""
        try:
            from ai_models.phone_detection.model import PhoneDetectionAI
            
            # Initialize model
            detector = PhoneDetectionAI()
            
            # Load pre-trained weights
            model_path = 'ai_models/phone_detection/phone_detection_model.pth'
            if os.path.exists(model_path):
                detector.load_model(model_path)
                self.logger.info("Phone detection model loaded successfully")
            else:
                self.logger.warning("No pre-trained model found, using default initialization")
            
            # Test prediction
            test_data = {
                'vendor_id': '04e8',
                'product_id': '6860'
            }
            test_prediction = detector.predict_phone(test_data)
            
            return {
                'model': 'PhoneDetectionAI',
                'status': 'deployed',
                'test_prediction': test_prediction,
                'version': '1.0'
            }
            
        except Exception as e:
            raise Exception(f"Phone detection AI deployment failed: {str(e)}")
    
    def deploy_unlock_recommender_ai(self) -> Dict[str, Any]:
        """Deploy unlock recommender AI model"""
        try:
            from ai_models.unlock_recommender.model import UnlockRecommenderAI
            
            # Initialize model
            recommender = UnlockRecommenderAI()
            
            # Load trained model
            model_path = 'ai_models/unlock_recommender/unlock_model.joblib'
            if os.path.exists(model_path):
                recommender.load_model(model_path)
                self.logger.info("Unlock recommender model loaded successfully")
            else:
                self.logger.warning("No trained model found, will train on first use")
            
            # Test recommendation
            test_phone = {
                'brand': 'Samsung',
                'model': 'Galaxy S21',
                'android_version': '12',
                'lock_type': 'frp'
            }
            test_recommendation = recommender.recommend_method(test_phone, 'frp')
            
            return {
                'model': 'UnlockRecommenderAI',
                'status': 'deployed',
                'test_recommendation': test_recommendation,
                'version': '1.0'
            }
            
        except Exception as e:
            raise Exception(f"Unlock recommender AI deployment failed: {str(e)}")
    
    def deploy_self_healing_ai(self) -> Dict[str, Any]:
        """Deploy self-healing AI system"""
        try:
            from ai_models.self_healing.model import RiskAssessor, FailurePredictor
            
            # Initialize components
            risk_assessor = RiskAssessor()
            failure_predictor = FailurePredictor()
            
            # Test components
            test_phone_data = {'model': 'HLTE230E', 'lock_type': 'frp'}
            risk_assessment = risk_assessor.assess_unlock_risk(test_phone_data)
            
            test_metrics = {
                'cpu_percent': 75,
                'memory_percent': 80,
                'disk_percent': 85
            }
            failure_prediction = failure_predictor.predict_failures(test_metrics)
            
            return {
                'components': ['RiskAssessor', 'FailurePredictor'],
                'status': 'deployed',
                'test_assessment': risk_assessment,
                'test_prediction': failure_prediction,
                'version': '1.0'
            }
            
        except Exception as e:
            raise Exception(f"Self-healing AI deployment failed: {str(e)}")
    
    def deploy_multi_agent_system(self) -> Dict[str, Any]:
        """Deploy multi-agent AI system"""
        try:
            from ai_models.multi_agent.orchestrator import StrategyGenerator
            from backend.services.ai_orchestrator import AIOrchestrator
            
            # Initialize orchestrator
            orchestrator = AIOrchestrator()
            strategy_generator = StrategyGenerator()
            
            # Test strategy generation
            test_phone = {'model': 'HLTE230E', 'lock_type': 'frp'}
            test_strategy = strategy_generator.generate_unlock_strategy(test_phone)
            
            return {
                'system': 'MultiAgentAI',
                'status': 'deployed',
                'test_strategy': test_strategy,
                'orchestrator_ready': True,
                'version': '1.0'
            }
            
        except Exception as e:
            raise Exception(f"Multi-agent system deployment failed: {str(e)}")
    
    def deploy_risk_assessment_ai(self) -> Dict[str, Any]:
        """Deploy risk assessment AI"""
        try:
            from ai_models.self_healing.model import RiskAssessor
            
            risk_ai = RiskAssessor()
            
            # Test risk assessment
            test_case = {
                'model': 'HLTE230E',
                'lock_type': 'frp',
                'bootloader_status': 'locked'
            }
            risk_assessment = risk_ai.assess_unlock_risk(test_case)
            
            return {
                'model': 'RiskAssessor',
                'status': 'deployed',
                'test_assessment': risk_assessment,
                'version': '1.0'
            }
            
        except Exception as e:
            raise Exception(f"Risk assessment AI deployment failed: {str(e)}")
    
    def activate_ai_orchestrator(self) -> Dict[str, Any]:
        """Activate the AI orchestrator"""
        try:
            from backend.services.ai_orchestrator import AIOrchestrator
            import asyncio
            
            orchestrator = AIOrchestrator()
            
            # Test activation with sample data
            test_phone = {
                'model': 'HLTE230E',
                'lock_type': 'frp',
                'connection_type': 'usb'
            }
            
            # Run async test
            async def test_orchestrator():
                return await orchestrator.activate_all_ai(test_phone)
            
            # For testing, we'll run it synchronously
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            test_result = loop.run_until_complete(test_orchestrator())
            loop.close()
            
            return {
                'orchestrator': 'AIOrchestrator',
                'status': 'activated',
                'test_activation': test_result is not None,
                'agents_activated': len(test_result.get('agent_results', {})),
                'version': '1.0'
            }
            
        except Exception as e:
            raise Exception(f"AI orchestrator activation failed: {str(e)}")
    
    def _generate_deployment_report(self) -> Dict[str, Any]:
        """Generate comprehensive deployment report"""
        successful = sum(1 for status in self.deployment_status.values() 
                        if status['status'] == 'success')
        total = len(self.deployment_status)
        
        report = {
            'summary': {
                'total_components': total,
                'successful_deployments': successful,
                'success_rate': successful / total if total > 0 else 0,
                'overall_status': 'success' if successful == total else 'partial'
            },
            'components': self.deployment_status,
            'recommendations': self._get_deployment_recommendations()
        }
        
        self.logger.info(f"Deployment completed: {successful}/{total} successful")
        
        return report
    
    def _get_deployment_recommendations(self) -> List[str]:
        """Get recommendations based on deployment results"""
        recommendations = []
        
        failed_components = [
            name for name, status in self.deployment_status.items() 
            if status['status'] == 'failed'
        ]
        
        if failed_components:
            recommendations.append(f"Investigate failed components: {', '.join(failed_components)}")
        
        if any('hisense' in str(status.get('result', {})).lower() 
               for status in self.deployment_status.values()):
            recommendations.append("Hisense AI models deployed successfully")
        
        if self.deployment_status.get('activate_ai_orchestrator', {}).get('status') == 'success':
            recommendations.append("AI orchestrator ready for phone unlocking operations")
        
        return recommendations

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='Deploy AI models for phone unlock system')
    parser.add_argument('--component', type=str, help='Specific component to deploy')
    parser.add_argument('--force', action='store_true', help='Force redeployment')
    
    args = parser.parse_args()
    
    deployer = AIDeployer()
    
    if args.component:
        # Deploy specific component
        if hasattr(deployer, f'deploy_{args.component}'):
            result = getattr(deployer, f'deploy_{args.component}')()
            print(f"Deployed {args.component}: {result}")
        else:
            print(f"Unknown component: {args.component}")
    else:
        # Deploy all components
        report = deployer.deploy_all_ai()
        print("AI Deployment Report:")
        print(f"Status: {report['summary']['overall_status']}")
        print(f"Success Rate: {report['summary']['success_rate']:.1%}")
        
        for comp_name, comp_status in report['components'].items():
            status_icon = "✅" if comp_status['status'] == 'success' else "❌"
            print(f"{status_icon} {comp_name}: {comp_status['status']}")

if __name__ == "__main__":
    main()
