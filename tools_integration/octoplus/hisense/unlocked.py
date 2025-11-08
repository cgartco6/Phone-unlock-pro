import subprocess
import os
import logging
from typing import Dict, List, Any
import tempfile

class HisenseUnlockTool:
    """Integration with Hisense official unlocking tools"""
    
    def __init__(self, tool_path: str = None):
        self.tool_path = tool_path or self._find_hisense_tool()
        self.logger = logging.getLogger(__name__)
        
    def _find_hisense_tool(self) -> str:
        """Find Hisense unlocking tool"""
        possible_paths = [
            "C:\\Program Files\\Hisense\\HisenseFlashTool.exe",
            "C:\\Hisense\\HisenseTool.exe",
            "/usr/local/bin/hisense_tool",
            "./tools/hisense/hisense_flash"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return "hisense_flash"  # Assume in PATH
    
    def flash_firmware(self, firmware_path: str, model: str) -> Dict[str, Any]:
        """Flash firmware to Hisense device"""
        try:
            cmd = [
                self.tool_path,
                '--model', model,
                '--firmware', firmware_path,
                '--operation', 'flash',
                '--auto-reboot'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            success = 'Flash completed successfully' in result.stdout
            
            return {
                'success': success,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Flash operation timed out (10 minutes)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Flash failed: {str(e)}'
            }
    
    def remove_frp(self, model: str) -> Dict[str, Any]:
        """Remove FRP lock from Hisense device"""
        try:
            cmd = [
                self.tool_path,
                '--model', model,
                '--operation', 'frp_remove'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            success = 'FRP removed' in result.stdout
            
            return {
                'success': success,
                'output': result.stdout,
                'logs': result.stdout.split('\n')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def read_device_info(self) -> Dict[str, Any]:
        """Read information from connected Hisense device"""
        try:
            cmd = [self.tool_path, '--operation', 'read_info']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse device information from output
            info = self._parse_device_info(result.stdout)
            
            return {
                'success': True,
                'device_info': info,
                'raw_output': result.stdout
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_device_info(self, output: str) -> Dict[str, str]:
        """Parse device information from tool output"""
        info = {}
        lines = output.split('\n')
        
        for line in lines:
            if 'Model:' in line:
                info['model'] = line.split('Model:')[-1].strip()
            elif 'Android:' in line:
                info['android_version'] = line.split('Android:')[-1].strip()
            elif 'Build:' in line:
                info['build_number'] = line.split('Build:')[-1].strip()
            elif 'Chipset:' in line:
                info['chipset'] = line.split('Chipset:')[-1].strip()
                
        return info
    
    def format_device(self, model: str) -> Dict[str, Any]:
        """Format Hisense device (factory reset via tool)"""
        try:
            cmd = [
                self.tool_path,
                '--model', model,
                '--operation', 'format'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180  # 3 minutes
            )
            
            success = 'Format completed' in result.stdout
            
            return {
                'success': success,
                'output': result.stdout
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_tool_health(self) -> bool:
        """Check if Hisense tool is working"""
        try:
            result = subprocess.run(
                [self.tool_path, '--version'],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
