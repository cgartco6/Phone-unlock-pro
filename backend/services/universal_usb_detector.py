import subprocess
import platform
import usb.core
import usb.util
import struct
import time
from typing import Dict, List, Any
import re

class UniversalUSBDetector:
    """Universal USB device detection that works with any connected phone"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.detection_methods = [
            self._try_adb_detection,
            self._try_fastboot_detection,
            self._try_usb_pyusb_detection,
            self._try_system_usb_enumeration,
            self._try_raw_usb_communication,
            self._try_emergency_modes,
            self._try_bootloader_modes
        ]
    
    def detect_any_phone(self) -> Dict[str, Any]:
        """Try all detection methods to find any connected phone"""
        results = []
        
        for method in self.detection_methods:
            try:
                result = method()
                if result and result.get('success'):
                    results.append(result)
                    # If we get a high-confidence detection, return it immediately
                    if result.get('confidence', 0) > 0.8:
                        return self._merge_detection_results([result])
            except Exception as e:
                print(f"Detection method {method.__name__} failed: {e}")
                continue
        
        if results:
            return self._merge_detection_results(results)
        else:
            return self._fallback_detection()
    
    def _try_adb_detection(self) -> Dict[str, Any]:
        """Try ADB-based detection"""
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
            lines = result.stdout.split('\n')[1:]  # Skip first line
            
            devices = []
            for line in lines:
                if line.strip() and 'device' in line and 'offline' not in line:
                    device_id = line.split('\t')[0]
                    
                    # Get detailed device info
                    model = self._get_adb_device_model(device_id)
                    brand = self._get_adb_device_brand(device_id)
                    android_version = self._get_adb_android_version(device_id)
                    
                    devices.append({
                        'device_id': device_id,
                        'model': model,
                        'brand': brand,
                        'android_version': android_version,
                        'connection_type': 'adb'
                    })
            
            if devices:
                return {
                    'success': True,
                    'method': 'adb',
                    'devices': devices,
                    'confidence': 0.95,
                    'primary_device': devices[0]
                }
        except Exception as e:
            pass
        
        return {'success': False, 'method': 'adb'}
    
    def _try_fastboot_detection(self) -> Dict[str, Any]:
        """Try Fastboot-based detection"""
        try:
            result = subprocess.run(['fastboot', 'devices'], capture_output=True, text=True, timeout=10)
            
            devices = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    device_id = line.split('\t')[0]
                    devices.append({
                        'device_id': device_id,
                        'connection_type': 'fastboot',
                        'mode': 'bootloader'
                    })
            
            if devices:
                return {
                    'success': True,
                    'method': 'fastboot',
                    'devices': devices,
                    'confidence': 0.9,
                    'primary_device': devices[0]
                }
        except Exception as e:
            pass
        
        return {'success': False, 'method': 'fastboot'}
    
    def _try_usb_pyusb_detection(self) -> Dict[str, Any]:
        """Try direct USB detection using pyusb"""
        try:
            # Find all USB devices
            devices = usb.core.find(find_all=True)
            
            phone_devices = []
            for dev in devices:
                device_info = self._analyze_usb_device(dev)
                if device_info.get('is_phone', False):
                    phone_devices.append(device_info)
            
            if phone_devices:
                return {
                    'success': True,
                    'method': 'pyusb',
                    'devices': phone_devices,
                    'confidence': 0.85,
                    'primary_device': phone_devices[0]
                }
        except Exception as e:
            pass
        
        return {'success': False, 'method': 'pyusb'}
    
    def _try_system_usb_enumeration(self) -> Dict[str, Any]:
        """Try system-specific USB enumeration"""
        try:
            if self.system == 'windows':
                return self._windows_usb_enumeration()
            elif self.system == 'linux':
                return self._linux_usb_enumeration()
            elif self.system == 'darwin':
                return self._macos_usb_enumeration()
        except Exception as e:
            pass
        
        return {'success': False, 'method': 'system_enumeration'}
    
    def _try_raw_usb_communication(self) -> Dict[str, Any]:
        """Try raw USB communication to identify devices"""
        try:
            # This method attempts to communicate with any USB device
            # that might be a phone, even if it's not properly recognized
            
            devices = usb.core.find(find_all=True)
            identified_devices = []
            
            for dev in devices:
                try:
                    # Try to read device descriptor
                    device_info = {
                        'vendor_id': f'{dev.idVendor:04x}',
                        'product_id': f'{dev.idProduct:04x}',
                        'device_class': dev.bDeviceClass,
                        'device_subclass': dev.bDeviceSubClass
                    }
                    
                    # Try to identify based on USB characteristics
                    identity = self._identify_by_usb_characteristics(device_info)
                    if identity:
                        device_info.update(identity)
                        identified_devices.append(device_info)
                        
                except usb.core.USBError:
                    continue
            
            if identified_devices:
                return {
                    'success': True,
                    'method': 'raw_usb',
                    'devices': identified_devices,
                    'confidence': 0.7,
                    'primary_device': identified_devices[0]
                }
        except Exception as e:
            pass
        
        return {'success': False, 'method': 'raw_usb'}
    
    def _try_emergency_modes(self) -> Dict[str, Any]:
        """Try to detect phones in emergency download modes"""
        emergency_modes = [
            ('Qualcomm EDL', '05c6', '9008'),
            ('Mediatek Preloader', '0e8d', '2000'),
            ('Samsung Download', '04e8', '685d'),
            ('Spreadtrum/Unisoc', '1782', '4d00'),
            ('Xiaomi EDL', '1d4d', '0002')
        ]
        
        try:
            devices = usb.core.find(find_all=True)
            emergency_devices = []
            
            for dev in devices:
                vendor_id = f'{dev.idVendor:04x}'
                product_id = f'{dev.idProduct:04x}'
                
                for mode_name, mode_vendor, mode_product in emergency_modes:
                    if vendor_id == mode_vendor and product_id == mode_product:
                        emergency_devices.append({
                            'mode': mode_name,
                            'vendor_id': vendor_id,
                            'product_id': product_id,
                            'connection_type': 'emergency_download'
                        })
            
            if emergency_devices:
                return {
                    'success': True,
                    'method': 'emergency_modes',
                    'devices': emergency_devices,
                    'confidence': 0.95,
                    'primary_device': emergency_devices[0]
                }
        except Exception as e:
            pass
        
        return {'success': False, 'method': 'emergency_modes'}
    
    def _try_bootloader_modes(self) -> Dict[str, Any]:
        """Try to detect phones in various bootloader modes"""
        bootloader_signatures = [
            ('Android Bootloader', '18d1', 'd001'),
            ('Google Bootloader', '18d1', '4ee0'),
            ('Samsung Bootloader', '04e8', '685d'),
            ('LG Bootloader', '1004', '6000'),
            ('HTC Bootloader', '0bb4', '0ffe')
        ]
        
        try:
            devices = usb.core.find(find_all=True)
            bootloader_devices = []
            
            for dev in devices:
                vendor_id = f'{dev.idVendor:04x}'
                product_id = f'{dev.idProduct:04x}'
                
                for bl_name, bl_vendor, bl_product in bootloader_signatures:
                    if vendor_id == bl_vendor and product_id == bl_product:
                        bootloader_devices.append({
                            'mode': bl_name,
                            'vendor_id': vendor_id,
                            'product_id': product_id,
                            'connection_type': 'bootloader'
                        })
            
            if bootloader_devices:
                return {
                    'success': True,
                    'method': 'bootloader_modes',
                    'devices': bootloader_devices,
                    'confidence': 0.9,
                    'primary_device': bootloader_devices[0]
                }
        except Exception as e:
            pass
        
        return {'success': False, 'method': 'bootloader_modes'}
    
    def _analyze_usb_device(self, dev) -> Dict[str, Any]:
        """Analyze USB device to determine if it's a phone"""
        vendor_id = f'{dev.idVendor:04x}'
        product_id = f'{dev.idProduct:04x}'
        
        # Known phone vendor IDs
        phone_vendors = {
            '04e8': 'Samsung',
            '0bb4': 'HTC',
            '12d1': 'Huawei',
            '18d1': 'Google',
            '22d9': 'Oppo',
            '2717': 'Xiaomi',
            '1782': 'Hisense',
            '05ac': 'Apple',
            '1004': 'LG',
            '0e8d': 'Mediatek',
            '05c6': 'Qualcomm',
            '1d4d': 'Xiaomi',
            '1f3a': 'ODM'
        }
        
        device_info = {
            'vendor_id': vendor_id,
            'product_id': product_id,
            'vendor_name': phone_vendors.get(vendor_id, 'Unknown'),
            'is_phone': vendor_id in phone_vendors,
            'device_class': dev.bDeviceClass,
            'device_subclass': dev.bDeviceSubClass
        }
        
        # Try to get more detailed information
        try:
            device_info['manufacturer'] = usb.util.get_string(dev, dev.iManufacturer)
            device_info['product'] = usb.util.get_string(dev, dev.iProduct)
            device_info['serial_number'] = usb.util.get_string(dev, dev.iSerialNumber)
        except:
            pass
        
        return device_info
    
    def _identify_by_usb_characteristics(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Identify device type based on USB characteristics"""
        vendor_id = device_info['vendor_id']
        product_id = device_info['product_id']
        
        # Common phone patterns
        patterns = [
            # Samsung in various modes
            {'vendor': '04e8', 'product_pattern': '68[0-9a-f]{2}', 'brand': 'Samsung', 'type': 'android'},
            # Huawei/Hisense
            {'vendor': '12d1', 'product_pattern': '.*', 'brand': 'Huawei/Honor', 'type': 'android'},
            {'vendor': '1782', 'product_pattern': '.*', 'brand': 'Hisense', 'type': 'android'},
            # Oppo/Realme
            {'vendor': '22d9', 'product_pattern': '.*', 'brand': 'Oppo', 'type': 'android'},
            # Xiaomi
            {'vendor': '2717', 'product_pattern': '.*', 'brand': 'Xiaomi', 'type': 'android'},
            # Apple
            {'vendor': '05ac', 'product_pattern': '12[0-9a-f]{2}', 'brand': 'Apple', 'type': 'ios'},
            # Microsoft
            {'vendor': '045e', 'product_pattern': 'f0ca', 'brand': 'Microsoft', 'type': 'windows'}
        ]
        
        for pattern in patterns:
            if vendor_id == pattern['vendor']:
                if re.match(pattern['product_pattern'], product_id):
                    return {
                        'brand': pattern['brand'],
                        'device_type': pattern['type'],
                        'confidence': 0.8
                    }
        
        return None
    
    def _get_adb_device_model(self, device_id: str) -> str:
        """Get device model via ADB"""
        try:
            result = subprocess.run([
                'adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model'
            ], capture_output=True, text=True, timeout=5)
            return result.stdout.strip() or 'Unknown'
        except:
            return 'Unknown'
    
    def _get_adb_device_brand(self, device_id: str) -> str:
        """Get device brand via ADB"""
        try:
            result = subprocess.run([
                'adb', '-s', device_id, 'shell', 'getprop', 'ro.product.brand'
            ], capture_output=True, text=True, timeout=5)
            brand = result.stdout.strip()
            return brand.capitalize() if brand else 'Unknown'
        except:
            return 'Unknown'
    
    def _get_adb_android_version(self, device_id: str) -> str:
        """Get Android version via ADB"""
        try:
            result = subprocess.run([
                'adb', '-s', device_id, 'shell', 'getprop', 'ro.build.version.release'
            ], capture_output=True, text=True, timeout=5)
            return result.stdout.strip() or 'Unknown'
        except:
            return 'Unknown'
    
    def _windows_usb_enumeration(self) -> Dict[str, Any]:
        """Windows-specific USB enumeration"""
        try:
            result = subprocess.run([
                'powershell', 
                'Get-PnpDevice -Class USB | Where-Object {$_.Status -eq "OK"} | Select-Object FriendlyName, DeviceID, Status'
            ], capture_output=True, text=True, timeout=10)
            
            devices = []
            for line in result.stdout.split('\n'):
                if any(keyword in line for keyword in ['Android', 'ADB', 'Composite', 'Phone', 'Mobile']):
                    devices.append({
                        'name': line.strip(),
                        'connection_type': 'windows_pnp'
                    })
            
            if devices:
                return {
                    'success': True,
                    'method': 'windows_enumeration',
                    'devices': devices,
                    'confidence': 0.75,
                    'primary_device': devices[0]
                }
        except Exception as e:
            pass
        
        return {'success': False, 'method': 'windows_enumeration'}
    
    def _linux_usb_enumeration(self) -> Dict[str, Any]:
        """Linux-specific USB enumeration"""
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=10)
            
            devices = []
            for line in result.stdout.split('\n'):
                if any(keyword in line.lower() for keyword in ['android', 'google', 'samsung', 'huawei', 'xiaomi', 'oppo', 'hisense']):
                    devices.append({
                        'info': line.strip(),
                        'connection_type': 'linux_lsusb'
                    })
            
            if devices:
                return {
                    'success': True,
                    'method': 'linux_enumeration',
                    'devices': devices,
                    'confidence': 0.8,
                    'primary_device': devices[0]
                }
        except Exception as e:
            pass
        
        return {'success': False, 'method': 'linux_enumeration'}
    
    def _macos_usb_enumeration(self) -> Dict[str, Any]:
        """macOS-specific USB enumeration"""
        try:
            result = subprocess.run([
                'system_profiler', 'SPUSBDataType'
            ], capture_output=True, text=True, timeout=10)
            
            devices = []
            for line in result.stdout.split('\n'):
                if any(keyword in line for keyword in ['iPhone', 'iPad', 'Android']):
                    devices.append({
                        'info': line.strip(),
                        'connection_type': 'macos_system_profiler'
                    })
            
            if devices:
                return {
                    'success': True,
                    'method': 'macos_enumeration',
                    'devices': devices,
                    'confidence': 0.85,
                    'primary_device': devices[0]
                }
        except Exception as e:
            pass
        
        return {'success': False, 'method': 'macos_enumeration'}
    
    def _merge_detection_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple detection results"""
        if not results:
            return {'success': False, 'error': 'No detection results'}
        
        # Get the highest confidence result
        best_result = max(results, key=lambda x: x.get('confidence', 0))
        
        # Merge devices from all successful detections
        all_devices = []
        for result in results:
            if result.get('devices'):
                all_devices.extend(result['devices'])
        
        return {
            'success': True,
            'method': 'combined',
            'devices': all_devices,
            'primary_device': best_result.get('primary_device'),
            'confidence': best_result.get('confidence', 0.7),
            'detection_methods': [r.get('method') for r in results if r.get('success')]
        }
    
    def _fallback_detection(self) -> Dict[str, Any]:
        """Fallback detection when all else fails"""
        # Try to detect any USB device that might be a phone
        try:
            devices = usb.core.find(find_all=True)
            if devices:
                # Return the first USB device as a potential phone
                dev = next(devices)
                return {
                    'success': True,
                    'method': 'fallback_usb',
                    'devices': [{
                        'vendor_id': f'{dev.idVendor:04x}',
                        'product_id': f'{dev.idProduct:04x}',
                        'connection_type': 'unknown_usb',
                        'note': 'Device detected but not recognized as phone'
                    }],
                    'confidence': 0.3,
                    'primary_device': {
                        'vendor_id': f'{dev.idVendor:04x}',
                        'product_id': f'{dev.idProduct:04x}',
                        'connection_type': 'unknown_usb'
                    }
                }
        except:
            pass
        
        return {
            'success': False,
            'error': 'No devices detected',
            'suggestion': 'Check USB connection and try different USB ports'
        }
    
    def force_device_recognition(self, vendor_id: str, product_id: str) -> Dict[str, Any]:
        """Force recognition of a specific USB device"""
        try:
            dev = usb.core.find(idVendor=int(vendor_id, 16), idProduct=int(product_id, 16))
            if dev:
                device_info = self._analyze_usb_device(dev)
                
                # Try to identify using our patterns
                identity = self._identify_by_usb_characteristics({
                    'vendor_id': vendor_id,
                    'product_id': product_id
                })
                
                if identity:
                    device_info.update(identity)
                
                return {
                    'success': True,
                    'device': device_info,
                    'method': 'forced_recognition',
                    'confidence': 0.6
                }
        except Exception as e:
            pass
        
        return {
            'success': False,
            'error': f'Could not force recognition of device {vendor_id}:{product_id}'
        }
