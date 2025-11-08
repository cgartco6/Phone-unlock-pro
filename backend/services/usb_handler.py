import subprocess
import platform
from typing import Dict, List, Any
from .universal_usb_detector import UniversalUSBDetector

class USBHandler:
    """Enhanced USB handler with universal device detection"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.universal_detector = UniversalUSBDetector()
    
    def detect_connected_device(self) -> Dict[str, Any]:
        """Detect any connected phone using universal methods"""
        try:
            # Use universal detector first
            result = self.universal_detector.detect_any_phone()
            
            if result.get('success'):
                return self._enhance_detection_result(result)
            else:
                return self._fallback_detection()
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'error_fallback'
            }
    
    def detect_specific_device(self, vendor_id: str, product_id: str) -> Dict[str, Any]:
        """Force detection of specific USB device"""
        return self.universal_detector.force_device_recognition(vendor_id, product_id)
    
    def get_detection_help(self) -> Dict[str, Any]:
        """Get help for device detection"""
        return {
            'universal_methods': [
                'ADB detection - requires USB debugging',
                'Fastboot detection - for bootloader mode',
                'Emergency mode detection - download/EDL modes',
                'USB raw detection - works with any USB device',
                'System enumeration - OS-specific detection'
            ],
            'troubleshooting': [
                'Try different USB cables',
                'Check device manager for unknown devices',
                'Enable USB debugging on Android',
                'Install universal ADB drivers',
                'Try different USB ports',
                'Restart device and computer'
            ],
            'emergency_modes': [
                'Samsung: Volume Down + Home + Power',
                'Most Android: Volume Down + Power',
                'Mediatek: Volume Up + Power (or test points)',
                'Qualcomm: Volume Up + Power (or EDL cable)'
            ]
        }
    
    def _enhance_detection_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance detection result with additional information"""
        if not result.get('success'):
            return result
        
        primary_device = result.get('primary_device', {})
        
        # Add connection quality assessment
        connection_quality = self._assess_connection_quality(primary_device)
        result['connection_quality'] = connection_quality
        
        # Add detection reliability score
        reliability = self._calculate_reliability(result)
        result['reliability_score'] = reliability
        
        # Add suggestions for improvement
        if reliability < 0.7:
            result['improvement_suggestions'] = self._get_improvement_suggestions(primary_device)
        
        return result
    
    def _assess_connection_quality(self, device_info: Dict[str, Any]) -> str:
        """Assess the quality of USB connection"""
        connection_type = device_info.get('connection_type', '')
        
        if any(mode in connection_type for mode in ['adb', 'fastboot', 'emergency']):
            return 'excellent'
        elif 'bootloader' in connection_type:
            return 'good'
        elif 'usb' in connection_type:
            return 'fair'
        else:
            return 'poor'
    
    def _calculate_reliability(self, result: Dict[str, Any]) -> float:
        """Calculate reliability score for detection"""
        confidence = result.get('confidence', 0)
        methods_used = len(result.get('detection_methods', []))
        connection_quality = result.get('connection_quality', 'poor')
        
        # Base reliability on confidence
        reliability = confidence
        
        # Bonus for multiple detection methods
        if methods_used > 1:
            reliability += 0.1
        
        # Adjust based on connection quality
        quality_bonus = {
            'excellent': 0.2,
            'good': 0.1,
            'fair': 0.0,
            'poor': -0.1
        }
        reliability += quality_bonus.get(connection_quality, 0)
        
        return min(1.0, max(0.0, reliability))
    
    def _get_improvement_suggestions(self, device_info: Dict[str, Any]) -> List[str]:
        """Get suggestions to improve detection"""
        suggestions = []
        connection_type = device_info.get('connection_type', '')
        
        if 'unknown' in connection_type:
            suggestions.extend([
                "Install device-specific drivers",
                "Try universal ADB drivers",
                "Check if device is in correct mode"
            ])
        
        if 'usb' in connection_type and 'adb' not in connection_type:
            suggestions.extend([
                "Enable USB debugging on device",
                "Change USB connection mode to File Transfer",
                "Try different USB cable"
            ])
        
        if not suggestions:
            suggestions.append("Try universal detection mode for better results")
        
        return suggestions
    
    def _fallback_detection(self) -> Dict[str, Any]:
        """Fallback when universal detection fails"""
        # Try traditional methods as fallback
        try:
            if self.system == 'windows':
                return self._windows_fallback()
            elif self.system == 'linux':
                return self._linux_fallback()
            elif self.system == 'darwin':
                return self._macos_fallback()
            else:
                return self._generic_fallback()
        except Exception as e:
            return self._generic_fallback()
    
    def _windows_fallback(self) -> Dict[str, Any]:
        """Windows fallback detection"""
        try:
            result = subprocess.run([
                'powershell', 
                'Get-PnpDevice -Class USB | Where-Object {$_.Status -eq "OK"} | Select-Object FriendlyName, DeviceID'
            ], capture_output=True, text=True)
            
            devices = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('FriendlyName'):
                    devices.append(line.strip())
            
            if devices:
                return {
                    'success': True,
                    'method': 'windows_fallback',
                    'devices_found': len(devices),
                    'device_list': devices,
                    'confidence': 0.4,
                    'note': 'USB devices detected but not specifically identified as phones'
                }
        except:
            pass
        
        return self._generic_fallback()
    
    def _linux_fallback(self) -> Dict[str, Any]:
        """Linux fallback detection"""
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            
            devices = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    devices.append(line.strip())
            
            if devices:
                return {
                    'success': True,
                    'method': 'linux_fallback',
                    'devices_found': len(devices),
                    'device_list': devices,
                    'confidence': 0.5,
                    'note': 'USB devices detected via lsusb'
                }
        except:
            pass
        
        return self._generic_fallback()
    
    def _macos_fallback(self) -> Dict[str, Any]:
        """macOS fallback detection"""
        try:
            result = subprocess.run([
                'system_profiler', 'SPUSBDataType'
            ], capture_output=True, text=True)
            
            devices = []
            in_phone_section = False
            for line in result.stdout.split('\n'):
                if 'iPhone' in line or 'iPad' in line or 'Android' in line:
                    in_phone_section = True
                if in_phone_section and line.strip():
                    devices.append(line.strip())
                    if line.startswith('          '):  # End of device section
                        in_phone_section = False
            
            if devices:
                return {
                    'success': True,
                    'method': 'macos_fallback',
                    'devices_found': len(devices),
                    'device_list': devices,
                    'confidence': 0.6,
                    'note': 'Possible phone devices detected'
                }
        except:
            pass
        
        return self._generic_fallback()
    
    def _generic_fallback(self) -> Dict[str, Any]:
        """Generic fallback when all detection fails"""
        return {
            'success': False,
            'error': 'No devices detected',
            'suggestions': [
                'Check USB cable and connection',
                'Try different USB port',
                'Enable USB debugging on Android devices',
                'Install universal ADB drivers',
                'Restart both device and computer',
                'Try putting device in download mode'
            ],
            'emergency_help': 'Use manual device selection if automatic detection fails'
        }
