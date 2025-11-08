from flask import Blueprint, request, jsonify
from models.universal_phone_detector import UniversalPhoneDetector
from services.usb_handler import USBHandler

universal_detection_bp = Blueprint('universal_detection', __name__)
universal_detector = UniversalPhoneDetector()
usb_handler = USBHandler()

@universal_detection_bp.route('/api/detect-any-phone', methods=['POST'])
def detect_any_phone():
    """Universal phone detection that works with any connected device"""
    try:
        # Get detection data from universal detector
        detection_result = usb_handler.detect_connected_device()
        
        if detection_result.get('success'):
            # Identify the device
            identification_result = universal_detector.identify_device(
                detection_result.get('primary_device', {})
            )
            
            return jsonify({
                'success': True,
                'detection': detection_result,
                'identification': identification_result,
                'combined_confidence': identification_result.get('detection_confidence', 0)
            })
        else:
            return jsonify({
                'success': False,
                'error': detection_result.get('error', 'Detection failed'),
                'suggestions': detection_result.get('suggestions', [])
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@universal_detection_bp.route('/api/force-detect-device', methods=['POST'])
def force_detect_device():
    """Force detection of specific USB device"""
    data = request.json
    vendor_id = data.get('vendor_id')
    product_id = data.get('product_id')
    
    if not vendor_id or not product_id:
        return jsonify({
            'success': False,
            'error': 'Vendor ID and Product ID required'
        })
    
    try:
        detection_result = usb_handler.detect_specific_device(vendor_id, product_id)
        identification_result = universal_detector.identify_device(
            detection_result.get('device', {})
        )
        
        return jsonify({
            'success': detection_result.get('success', False),
            'detection': detection_result,
            'identification': identification_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@universal_detection_bp.route('/api/detection-help', methods=['GET'])
def get_detection_help():
    """Get help for device detection"""
    try:
        help_info = usb_handler.get_detection_help()
        
        return jsonify({
            'success': True,
            'help': help_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@universal_detection_bp.route('/api/universal-devices', methods=['GET'])
def get_universal_devices():
    """Get list of all supported devices"""
    try:
        # This would typically come from the database
        supported_devices = [
            {'brand': 'Samsung', 'models': ['A24', 'A14', 'A05s', 'S21']},
            {'brand': 'Oppo', 'models': ['A78']},
            {'brand': 'Honor', 'models': ['90 Lite', '200']},
            {'brand': 'Huawei', 'models': ['X70']},
            {'brand': 'Microsoft', 'models': ['Lumia 640 LTE']},
            {'brand': 'Hisense', 'models': ['Infinity H40 Lite', 'H30', 'H50']},
            {'brand': 'Apple', 'models': ['iPhone 13', 'iPhone 14', 'iPhone 15']},
            {'brand': 'Xiaomi', 'models': ['Redmi Note 10', 'Redmi Note 11']}
        ]
        
        return jsonify({
            'success': True,
            'devices': supported_devices,
            'total_models': sum(len(brand['models']) for brand in supported_devices)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
