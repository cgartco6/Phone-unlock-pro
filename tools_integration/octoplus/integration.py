import subprocess
import json
import os
from typing import Dict, Any

class OctoplusIntegration:
    """Integration with Octoplus unlocking tool"""
    
    def __init__(self, tool_path: str = None):
        self.tool_path = tool_path or "C:\\Program Files\\Octoplus\\octoplus.exe"
        self.supported_operations = [
            'frp_unlock', 'kg_reset', 'bootloader_unlock', 'flash_firmware'
        ]
    
    def execute_unlock(self, phone_model: str, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute unlock operation using Octoplus"""
        try:
            # Build command based on operation
            command = self._build_command(phone_model, operation, kwargs)
            
            # Execute command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            return self._parse_result(result, operation)
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Operation timed out',
                'logs': ['Process exceeded time limit']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'logs': [f'Execution failed: {e}']
            }
    
    def _build_command(self, phone_model: str, operation: str, params: Dict[str, Any]) -> list:
        """Build Octoplus command line arguments"""
        base_command = [self.tool_path, '--model', phone_model]
        
        if operation == 'frp_unlock':
            base_command.extend(['--operation', 'frp_bypass'])
            if params.get('method'):
                base_command.extend(['--method', params['method']])
                
        elif operation == 'kg_reset':
            base_command.extend(['--operation', 'kg_reset'])
            base_command.extend(['--force', 'true'])
            
        elif operation == 'bootloader_unlock':
            base_command.extend(['--operation', 'bootloader_unlock'])
            
        elif operation == 'flash_firmware':
            base_command.extend(['--operation', 'flash'])
            if params.get('firmware_path'):
                base_command.extend(['--firmware', params['firmware_path']])
        
        return base_command
    
    def _parse_result(self, result: subprocess.CompletedProcess, operation: str) -> Dict[str, Any]:
        """Parse Octoplus tool output"""
        success_indicators = [
            'successfully', 'completed', 'unlocked', 'bypassed'
        ]
        
        output_lower = result.stdout.lower()
        success = any(indicator in output_lower for indicator in success_indicators)
        
        return {
            'success': success,
            'output': result.stdout,
            'error': result.stderr,
            'return_code': result.returncode,
            'logs': result.stdout.split('\n')
        }
    
    def check_connection(self) -> bool:
        """Check if Octoplus tool is accessible"""
        try:
            result = subprocess.run(
                [self.tool_path, '--version'],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
