import logging
import time
import sqlite3
import psutil
from typing import Dict, List, Any
import subprocess
import requests

class SelfHealingSystem:
    def __init__(self):
        self.health_metrics = {}
        self.repair_attempts = {}
        self.max_repair_attempts = 3
        
    def monitor_system_health(self) -> Dict[str, Any]:
        """Monitor all system components"""
        health_status = {
            'timestamp': time.time(),
            'components': {},
            'overall_health': 'healthy',
            'issues': []
        }
        
        # Check backend services
        health_status['components']['backend'] = self._check_backend_health()
        
        # Check AI models
        health_status['components']['ai_models'] = self._check_ai_models_health()
        
        # Check database
        health_status['components']['database'] = self._check_database_health()
        
        # Check tool integrations
        health_status['components']['tools'] = self._check_tools_health()
        
        # Check system resources
        health_status['components']['resources'] = self._check_system_resources()
        
        # Determine overall health
        issues = []
        for component, status in health_status['components'].items():
            if status['status'] != 'healthy':
                issues.append(f"{component}: {status['message']}")
                health_status['overall_health'] = 'degraded'
        
        health_status['issues'] = issues
        self.health_metrics = health_status
        
        # Auto-heal if issues detected
        if issues:
            self.auto_heal(issues)
            
        return health_status
    
    def _check_backend_health(self) -> Dict[str, Any]:
        """Check backend service health"""
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=5)
            if response.status_code == 200:
                return {'status': 'healthy', 'message': 'Backend running'}
            else:
                return {'status': 'degraded', 'message': f'Backend responded with {response.status_code}'}
        except Exception as e:
            return {'status': 'unhealthy', 'message': f'Backend unreachable: {str(e)}'}
    
    def _check_ai_models_health(self) -> Dict[str, Any]:
        """Check AI models health"""
        models_status = {}
        try:
            # Check phone detection model
            from ai_models.phone_detection.model import PhoneDetectionAI
            detector = PhoneDetectionAI()
            models_status['phone_detection'] = {'status': 'healthy', 'message': 'Model loaded'}
        except Exception as e:
            models_status['phone_detection'] = {'status': 'unhealthy', 'message': str(e)}
        
        try:
            # Check unlock recommender
            from ai_models.unlock_recommender.model import UnlockRecommenderAI
            recommender = UnlockRecommenderAI()
            models_status['unlock_recommender'] = {'status': 'healthy', 'message': 'Model loaded'}
        except Exception as e:
            models_status['unlock_recommender'] = {'status': 'unhealthy', 'message': str(e)}
            
        # Overall AI health
        unhealthy_models = [name for name, status in models_status.items() if status['status'] != 'healthy']
        if unhealthy_models:
            return {'status': 'degraded', 'message': f'Unhealthy models: {unhealthy_models}', 'details': models_status}
        else:
            return {'status': 'healthy', 'message': 'All AI models healthy', 'details': models_status}
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            conn = sqlite3.connect('database/phone_database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM phones')
            phone_count = cursor.fetchone()[0]
            conn.close()
            
            return {'status': 'healthy', 'message': f'Database accessible with {phone_count} phones'}
        except Exception as e:
            return {'status': 'unhealthy', 'message': f'Database error: {str(e)}'}
    
    def _check_tools_health(self) -> Dict[str, Any]:
        """Check unlocking tools health"""
        tools_status = {}
        
        # Check Octoplus
        try:
            from tools_integration.octoplus.integration import OctoplusIntegration
            octoplus = OctoplusIntegration()
            tools_status['octoplus'] = {
                'status': 'healthy' if octoplus.check_connection() else 'degraded',
                'message': 'Octoplus connected' if octoplus.check_connection() else 'Octoplus not responding'
            }
        except Exception as e:
            tools_status['octoplus'] = {'status': 'unhealthy', 'message': str(e)}
        
        # Check Hisense tool
        try:
            from tools_integration.hisense.unlocker import HisenseUnlocker
            hisense = HisenseUnlocker()
            tools_status['hisense'] = {
                'status': 'healthy',
                'message': 'Hisense unlocker ready'
            }
        except Exception as e:
            tools_status['hisense'] = {'status': 'unhealthy', 'message': str(e)}
            
        unhealthy_tools = [name for name, status in tools_status.items() if status['status'] != 'healthy']
        if unhealthy_tools:
            return {'status': 'degraded', 'message': f'Unhealthy tools: {unhealthy_tools}', 'details': tools_status}
        else:
            return {'status': 'healthy', 'message': 'All tools healthy', 'details': tools_status}
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        issues = []
        if cpu_percent > 90:
            issues.append(f'High CPU usage: {cpu_percent}%')
        if memory.percent > 90:
            issues.append(f'High memory usage: {memory.percent}%')
        if disk.percent > 90:
            issues.append(f'Low disk space: {disk.percent}%')
            
        status = 'healthy' if not issues else 'degraded'
        
        return {
            'status': status,
            'message': ' | '.join(issues) if issues else 'Resources normal',
            'details': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent
            }
        }
    
    def auto_heal(self, issues: List[str]):
        """Automatically heal detected issues"""
        for issue in issues:
            component = issue.split(':')[0]
            
            # Don't attempt too many repairs
            if self.repair_attempts.get(component, 0) >= self.max_repair_attempts:
                logging.warning(f"Max repair attempts reached for {component}")
                continue
                
            self.repair_attempts[component] = self.repair_attempts.get(component, 0) + 1
            
            try:
                if 'backend' in component:
                    self._heal_backend()
                elif 'database' in component:
                    self._heal_database()
                elif 'ai' in component.lower():
                    self._heal_ai_models()
                elif 'tool' in component.lower():
                    self._heal_tools(component)
                elif 'resource' in component.lower():
                    self._heal_resources()
                    
                logging.info(f"Auto-healed: {component}")
                
            except Exception as e:
                logging.error(f"Failed to heal {component}: {str(e)}")
    
    def _heal_backend(self):
        """Restart backend services"""
        try:
            subprocess.run(['pkill', '-f', 'python app.py'], check=False)
            time.sleep(2)
            subprocess.Popen(['python', 'backend/app.py'], 
                           cwd='.', 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            time.sleep(5)  # Wait for backend to start
        except Exception as e:
            logging.error(f"Backend healing failed: {e}")
    
    def _heal_database(self):
        """Repair database issues"""
        try:
            # Backup current database
            import shutil
            shutil.copy2('database/phone_database.db', 
                        f'database/backup/phone_database_backup_{int(time.time())}.db')
            
            # Reinitialize database
            subprocess.run(['python', 'database/init_db.py'], check=True)
            
        except Exception as e:
            logging.error(f"Database healing failed: {e}")
    
    def _heal_ai_models(self):
        """Reload AI models"""
        try:
            # Clear model cache and reload
            import importlib
            import sys
            
            # Reload AI modules
            for module in ['ai_models.phone_detection.model', 
                          'ai_models.unlock_recommender.model']:
                if module in sys.modules:
                    importlib.reload(sys.modules[module])
                    
        except Exception as e:
            logging.error(f"AI models healing failed: {e}")
    
    def _heal_tools(self, tool_name: str):
        """Restart tool processes"""
        try:
            if 'octoplus' in tool_name.lower():
                subprocess.run(['taskkill', '/F', '/IM', 'octoplus.exe'], check=False, shell=True)
                time.sleep(2)
                # Octoplus will be restarted on next use
            elif 'hisense' in tool_name.lower():
                # Hisense tool doesn't typically run as a service
                pass
                
        except Exception as e:
            logging.error(f"Tool healing failed for {tool_name}: {e}")
    
    def _heal_resources(self):
        """Free up system resources"""
        try:
            # Clear temporary files
            import tempfile
            import os
            temp_dir = tempfile.gettempdir()
            for file in os.listdir(temp_dir):
                if file.startswith('phone_unlock_'):
                    os.remove(os.path.join(temp_dir, file))
            
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            logging.error(f"Resource healing failed: {e}")
    
    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        return {
            'current_health': self.health_metrics,
            'repair_history': self.repair_attempts,
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for system improvement"""
        recommendations = []
        
        if self.repair_attempts:
            recommendations.append("Consider investigating frequent component failures")
        
        resource_details = self.health_metrics.get('components', {}).get('resources', {}).get('details', {})
        if resource_details.get('memory_percent', 0) > 80:
            recommendations.append("Consider adding more RAM or optimizing memory usage")
        
        if resource_details.get('disk_percent', 0) > 80:
            recommendations.append("Consider cleaning up disk space or adding storage")
            
        return recommendations
