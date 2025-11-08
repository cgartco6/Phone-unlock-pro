import asyncio
import logging
from typing import Dict, List, Any
import json

class AIOrchestrator:
    def __init__(self):
        self.active_agents = {}
        self.agent_results = {}
        
    async def activate_all_ai(self, phone_data: Dict[str, Any]) -> Dict[str, Any]:
        """Activate all AI agents for comprehensive phone analysis"""
        tasks = []
        
        # Phone Detection Agent
        tasks.append(self._run_phone_detection_agent(phone_data))
        
        # Lock Analysis Agent
        tasks.append(self._run_lock_analysis_agent(phone_data))
        
        # Firmware Recommendation Agent
        tasks.append(self._run_firmware_agent(phone_data))
        
        # Unlock Strategy Agent
        tasks.append(self._run_strategy_agent(phone_data))
        
        # Risk Assessment Agent
        tasks.append(self._run_risk_agent(phone_data))
        
        # Execute all agents concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile results
        compiled_results = self._compile_agent_results(results)
        
        # Generate master unlock plan
        master_plan = self._generate_master_plan(compiled_results)
        
        return {
            'agent_results': compiled_results,
            'master_unlock_plan': master_plan,
            'confidence_score': self._calculate_confidence(compiled_results),
            'recommended_actions': self._get_recommended_actions(compiled_results)
        }
    
    async def _run_phone_detection_agent(self, phone_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI agent for advanced phone detection"""
        try:
            from ai_models.phone_detection.model import PhoneDetectionAI
            from backend.services.usb_handler import USBHandler
            
            detector = PhoneDetectionAI()
            usb_handler = USBHandler()
            
            # Get USB data
            usb_data = usb_handler.detect_connected_device()
            
            # AI prediction
            prediction = detector.predict_phone(usb_data)
            
            return {
                'agent': 'phone_detection',
                'status': 'completed',
                'data': prediction,
                'confidence': prediction.get('confidence', 0.5)
            }
        except Exception as e:
            return {
                'agent': 'phone_detection',
                'status': 'failed',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _run_lock_analysis_agent(self, phone_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI agent for lock type analysis"""
        try:
            from ai_models.unlock_recommender.model import UnlockRecommenderAI
            from backend.models.unlock_analyzer import UnlockAnalyzer
            
            analyzer = UnlockAnalyzer()
            ai_recommender = UnlockRecommenderAI()
            
            # Analyze lock
            analysis = analyzer.analyze_lock(
                phone_data.get('model', ''),
                phone_data.get('lock_type', 'auto')
            )
            
            # AI recommendation
            recommendation = ai_recommender.recommend_method(
                analysis, 
                phone_data.get('lock_type', 'auto')
            )
            
            return {
                'agent': 'lock_analysis',
                'status': 'completed',
                'data': {
                    'analysis': analysis,
                    'ai_recommendation': recommendation
                },
                'confidence': recommendation.get('confidence', 0.5)
            }
        except Exception as e:
            return {
                'agent': 'lock_analysis',
                'status': 'failed',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _run_firmware_agent(self, phone_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI agent for firmware matching and recommendation"""
        try:
            from backend.models.firmware_matcher import FirmwareMatcher
            from services.ai_analyzer import AIAnalyzer
            
            matcher = FirmwareMatcher()
            ai_analyzer = AIAnalyzer()
            
            # Find firmware
            firmware_list = matcher.find_firmware(
                phone_data.get('model', ''),
                phone_data.get('region', '')
            )
            
            # AI recommendation
            recommendation = ai_analyzer.recommend_firmware(
                firmware_list, 
                phone_data.get('model', '')
            )
            
            return {
                'agent': 'firmware_recommendation',
                'status': 'completed',
                'data': {
                    'available_firmware': firmware_list,
                    'ai_recommendation': recommendation
                },
                'confidence': recommendation.get('confidence', 0.5)
            }
        except Exception as e:
            return {
                'agent': 'firmware_recommendation',
                'status': 'failed',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _run_strategy_agent(self, phone_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI agent for unlock strategy generation"""
        try:
            from ai_models.multi_agent.orchestrator import StrategyGenerator
            
            strategy_ai = StrategyGenerator()
            strategy = strategy_ai.generate_unlock_strategy(phone_data)
            
            return {
                'agent': 'strategy_generation',
                'status': 'completed',
                'data': strategy,
                'confidence': strategy.get('overall_confidence', 0.5)
            }
        except Exception as e:
            return {
                'agent': 'strategy_generation',
                'status': 'failed',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _run_risk_agent(self, phone_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI agent for risk assessment"""
        try:
            from ai_models.self_healing.model import RiskAssessor
            
            risk_ai = RiskAssessor()
            risk_assessment = risk_ai.assess_unlock_risk(phone_data)
            
            return {
                'agent': 'risk_assessment',
                'status': 'completed',
                'data': risk_assessment,
                'confidence': risk_assessment.get('assessment_confidence', 0.5)
            }
        except Exception as e:
            return {
                'agent': 'risk_assessment',
                'status': 'failed',
                'error': str(e),
                'confidence': 0.0
            }
    
    def _compile_agent_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compile results from all AI agents"""
        compiled = {}
        successful_agents = 0
        
        for result in results:
            if isinstance(result, Exception):
                continue
                
            agent_name = result.get('agent', 'unknown')
            compiled[agent_name] = result
            
            if result.get('status') == 'completed':
                successful_agents += 1
        
        compiled['summary'] = {
            'total_agents': len(results),
            'successful_agents': successful_agents,
            'success_rate': successful_agents / len(results) if results else 0
        }
        
        return compiled
    
    def _generate_master_plan(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate master unlock plan from agent results"""
        # Extract key information from each agent
        phone_info = agent_results.get('phone_detection', {}).get('data', {})
        lock_analysis = agent_results.get('lock_analysis', {}).get('data', {})
        firmware_info = agent_results.get('firmware_recommendation', {}).get('data', {})
        strategy = agent_results.get('strategy_generation', {}).get('data', {})
        risk = agent_results.get('risk_assessment', {}).get('data', {})
        
        master_plan = {
            'phone_identification': phone_info,
            'lock_analysis': lock_analysis.get('analysis', {}),
            'recommended_method': lock_analysis.get('ai_recommendation', {}),
            'firmware_selection': firmware_info.get('ai_recommendation', {}),
            'execution_strategy': strategy,
            'risk_assessment': risk,
            'step_by_step_guide': self._generate_step_by_step_guide(
                phone_info, lock_analysis, strategy
            ),
            'fallback_plans': self._generate_fallback_plans(agent_results)
        }
        
        return master_plan
    
    def _generate_step_by_step_guide(self, phone_info: Dict[str, Any], 
                                   lock_analysis: Dict[str, Any], 
                                   strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed step-by-step unlock guide"""
        steps = []
        
        # Preparation steps
        steps.append({
            'step': 1,
            'action': 'Preparation',
            'description': 'Gather required tools and software',
            'tools': lock_analysis.get('requirements', []),
            'estimated_time': '5 minutes',
            'critical': True
        })
        
        # Connection steps
        steps.append({
            'step': 2,
            'action': 'Phone Connection',
            'description': 'Connect phone in correct mode (Download/EDL)',
            'mode': strategy.get('connection_mode', 'Download'),
            'estimated_time': '2 minutes',
            'critical': True
        })
        
        # Unlock execution steps
        method_steps = lock_analysis.get('analysis', {}).get('methods', [{}])[0].get('steps', [])
        for i, method_step in enumerate(method_steps, 3):
            steps.append({
                'step': i,
                'action': f'Unlock Step {i-2}',
                'description': method_step,
                'estimated_time': 'Varies',
                'critical': i == 3  # First unlock step is critical
            })
        
        # Verification step
        steps.append({
            'step': len(steps) + 1,
            'action': 'Verification',
            'description': 'Verify unlock was successful',
            'estimated_time': '2 minutes',
            'critical': True
        })
        
        return steps
    
    def _generate_fallback_plans(self, agent_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alternative plans if primary method fails"""
        fallbacks = []
        
        lock_analysis = agent_results.get('lock_analysis', {}).get('data', {})
        analysis = lock_analysis.get('analysis', {})
        
        # Alternative methods
        methods = analysis.get('methods', [])
        if len(methods) > 1:
            for i, method in enumerate(methods[1:], 1):  # Skip first (primary) method
                fallbacks.append({
                    'plan_id': f'fallback_{i}',
                    'method': method.get('name', 'Alternative'),
                    'success_rate': method.get('success_rate', 0.5),
                    'difficulty': method.get('difficulty', 'medium'),
                    'description': f'Alternative method if primary fails'
                })
        
        # Emergency recovery
        fallbacks.append({
            'plan_id': 'emergency_recovery',
            'method': 'Firmware Flash',
            'success_rate': 0.8,
            'difficulty': 'medium',
            'description': 'Complete firmware reflash to recover bricked device'
        })
        
        return fallbacks
    
    def _calculate_confidence(self, agent_results: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        confidences = []
        
        for agent_name, result in agent_results.items():
            if agent_name != 'summary' and result.get('status') == 'completed':
                confidences.append(result.get('confidence', 0.0))
        
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def _get_recommended_actions(self, agent_results: Dict[str, Any]) -> List[str]:
        """Get recommended actions based on agent analysis"""
        actions = []
        
        risk_data = agent_results.get('risk_assessment', {}).get('data', {})
        if risk_data.get('risk_level') == 'high':
            actions.append("Proceed with caution - high risk of data loss")
        
        success_rate = agent_results.get('summary', {}).get('success_rate', 0)
        if success_rate < 0.7:
            actions.append("Consider manual verification due to low AI confidence")
        
        return actions
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all AI agents"""
        return {
            'active_agents': self.active_agents,
            'last_results': self.agent_results,
            'system_ready': len(self.active_agents) > 0
        }
