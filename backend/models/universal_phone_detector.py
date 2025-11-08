import sqlite3
import json
import re
from typing import Dict, List, Any
from difflib import SequenceMatcher

class UniversalPhoneDetector:
    """Enhanced phone detector that can identify any connected device"""
    
    def __init__(self):
        self.db_path = 'database/phone_database.db'
        self.detection_methods = [
            self._match_by_usb_ids,
            self._match_by_adb_info,
            self._match_by_fastboot_info,
            self._match_by_emergency_mode,
            self._fuzzy_match_by_name,
            self._match_by_characteristics,
            self._generic_detection
        ]
    
    def identify_device(self, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify device using multiple detection methods"""
        results = []
        
        for method in self.detection_methods:
            try:
                result = method(detection_data)
                if result and result.get('confidence', 0) > 0.1:
                    results.append(result)
                    # Return immediately if we get a high-confidence match
                    if result.get('confidence', 0) > 0.9:
                        return result
            except Exception as e:
                continue
        
        if results:
            # Return the highest confidence result
            best_result = max(results, key=lambda x: x.get('confidence', 0))
            return best_result
        else:
            return self._create_unknown_device(detection_data)
    
    def _match_by_usb_ids(self, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Match device by USB vendor and product IDs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        vendor_id = detection_data.get('vendor_id')
        product_id = detection_data.get('product_id')
        
        if vendor_id and product_id:
            cursor.execute('''
                SELECT * FROM phones 
                WHERE vendor_id = ? AND product_id = ?
            ''', (vendor_id, product_id))
            result = cursor.fetchone()
            
            if result:
                conn.close()
                return self._format_phone_info(result, confidence=0.95)
        
        conn.close()
        return None
    
    def _match_by_adb_info(self, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Match device using ADB information"""
        model = detection_data.get('model')
        brand = detection_data.get('brand')
        
        if model and brand:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Try exact match first
            cursor.execute('''
                SELECT * FROM phones 
                WHERE brand = ? AND model LIKE ?
            ''', (brand, f'%{model}%'))
            result = cursor.fetchone()
            
            if result:
                conn.close()
                return self._format_phone_info(result, confidence=0.9)
            
            conn.close()
        
        return None
    
    def _match_by_fastboot_info(self, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Match device in fastboot mode"""
        # Fastboot devices usually don't provide much info
        # We can try to match by USB IDs or generic detection
        return self._match_by_usb_ids(detection_data)
    
    def _match_by_emergency_mode(self, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Match device in emergency/download modes"""
        vendor_id = detection_data.get('vendor_id')
        mode = detection_data.get('mode', '')
        
        if vendor_id and 'download' in mode.lower() or 'edl' in mode.lower():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Match by vendor ID for emergency modes
            cursor.execute('''
                SELECT * FROM phones 
                WHERE vendor_id = ? AND detection_priority <= 2
                ORDER BY detection_priority
            ''', (vendor_id,))
            result = cursor.fetchone()
            
            if result:
                conn.close()
                return self._format_phone_info(result, confidence=0.8)
            
            conn.close()
        
        return None
    
    def _fuzzy_match_by_name(self, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fuzzy matching for device names"""
        device_name = detection_data.get('device_name') or detection_data.get('product') or ''
        
        if not device_name:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM phones')
        all_phones = cursor.fetchall()
        conn.close()
        
        best_match = None
        best_score = 0
        
        for phone in all_phones:
            phone_name = f"{phone[1]} {phone[2]}"  # brand + model
            score = self._similarity(device_name.lower(), phone_name.lower())
            
            if score > best_score and score > 0.6:
                best_score = score
                best_match = phone
        
        if best_match:
            return self._format_phone_info(best_match, confidence=best_score * 0.8)
        
        return None
    
    def _match_by_characteristics(self, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Match by USB characteristics and patterns"""
        vendor_id = detection_data.get('vendor_id')
        device_class = detection_data.get('device_class')
        
        if not vendor_id:
            return None
        
        # Known patterns for different brands
        brand_patterns = {
            '04e8': ('Samsung', 0.7),  # Samsung
            '12d1': ('Huawei', 0.7),   # Huawei/Honor
            '22d9': ('Oppo', 0.7),     # Oppo
            '2717': ('Xiaomi', 0.7),   # Xiaomi
            '1782': ('Hisense', 0.8),  # Hisense
            '05ac': ('Apple', 0.9),    # Apple
            '045e': ('Microsoft', 0.8) # Microsoft
        }
        
        if vendor_id in brand_patterns:
            brand, base_confidence = brand_patterns[vendor_id]
            
            # Try to find any device from this brand
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM phones 
                WHERE brand = ? 
                ORDER BY detection_priority
                LIMIT 1
            ''', (brand,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return self._format_phone_info(result, confidence=base_confidence)
        
        return None
    
    def _generic_detection(self, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic detection for unknown devices"""
        vendor_id = detection_data.get('vendor_id')
        
        if not vendor_id:
            return None
        
        # Get device type based on vendor ID
        device_types = {
            '04e8': 'Samsung Android Device',
            '12d1': 'Huawei/Honor Android Device', 
            '22d9': 'Oppo/Realme Android Device',
            '2717': 'Xiaomi Android Device',
            '1782': 'Hisense Android Device',
            '05ac': 'Apple iOS Device',
            '045e': 'Microsoft Windows Device',
            '0bb4': 'HTC Android Device',
            '1004': 'LG Android Device',
            '18d1': 'Google Android Device'
        }
        
        device_type = device_types.get(vendor_id, 'Unknown Mobile Device')
        
        return {
            'brand': device_type.split()[0],
            'model': device_type,
            'model_number': 'N/A',
            'android_version': 'Unknown',
            'supported_locks': ['frp', 'screen_lock'],
            'detection_confidence': 0.5,
            'notes': f'Generic detection based on vendor ID {vendor_id}',
            'detection_method': 'generic'
        }
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate string similarity"""
        return SequenceMatcher(None, a, b).ratio()
    
    def _format_phone_info(self, db_record, confidence: float = 0.8) -> Dict[str, Any]:
        """Format database record into phone info"""
        return {
            'brand': db_record[1],
            'model': db_record[2],
            'model_number': db_record[3],
            'android_version': db_record[4],
            'supported_locks': json.loads(db_record[5]),
            'detection_confidence': confidence,
            'notes': db_record[6],
            'vendor_id': db_record[7],
            'product_id': db_record[8],
            'detection_method': 'database_match'
        }
    
    def _create_unknown_device(self, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create info for completely unknown devices"""
        vendor_id = detection_data.get('vendor_id', 'Unknown')
        product_id = detection_data.get('product_id', 'Unknown')
        
        return {
            'brand': 'Unknown',
            'model': f'USB Device {vendor_id}:{product_id}',
            'model_number': 'N/A',
            'android_version': 'Unknown',
            'supported_locks': ['frp', 'screen_lock'],
            'detection_confidence': 0.1,
            'notes': 'Device not recognized. Try different USB modes or cables.',
            'vendor_id': vendor_id,
            'product_id': product_id,
            'detection_method': 'unknown'
        }
    
    def get_detection_help(self, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get help for detecting a specific device"""
        vendor_id = detection_data.get('vendor_id')
        suggestions = []
        
        if vendor_id == 'Unknown' or not vendor_id:
            suggestions.extend([
                "Try different USB cable",
                "Check if device drivers are installed",
                "Try different USB port",
                "Enable USB debugging on Android device",
                "Check if device is in charging-only mode"
            ])
        else:
            suggestions.extend([
                f"Device detected with vendor ID: {vendor_id}",
                "Try putting device in download mode",
                "For Android: Enable OEM unlocking in developer options",
                "Try different USB connection modes (MTP, PTP, MIDI)"
            ])
        
        return {
            'suggestions': suggestions,
            'vendor_id': vendor_id,
            'next_steps': [
                "Check device manager for unknown devices",
                "Install generic ADB drivers",
                "Try universal phone detection mode"
            ]
        }
