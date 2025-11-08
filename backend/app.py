from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import json
import logging
from models.phone_detector import PhoneDetector
from models.unlock_analyzer import UnlockAnalyzer
from models.firmware_matcher import FirmwareMatcher
from services.ai_analyzer import AIAnalyzer
from services.tool_integration import ToolIntegration
from services.usb_handler import USBHandler

app = Flask(__name__)
CORS(app)

# Initialize components
phone_detector = PhoneDetector()
unlock_analyzer = UnlockAnalyzer()
firmware_matcher = FirmwareMatcher()
ai_analyzer = AIAnalyzer()
tool_integration = ToolIntegration()
usb_handler = USBHandler()

@app.route('/api/detect-phone', methods=['POST'])
def detect_phone():
    """Auto-detect connected phone"""
    try:
        detection_data = usb_handler.detect_connected_device()
        if detection_data:
            phone_info = phone_detector.analyze_device(detection_data)
            return jsonify({
                'success': True,
                'phone': phone_info,
                'detection_method': detection_data['method']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No phone detected'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/analyze-lock', methods=['POST'])
def analyze_lock():
    """Analyze phone lock type and recommend solution"""
    data = request.json
    phone_model = data.get('phone_model')
    lock_type = data.get('lock_type', 'auto')
    
    try:
        analysis = unlock_analyzer.analyze_lock(phone_model, lock_type)
        ai_recommendation = ai_analyzer.get_unlock_recommendation(analysis)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'ai_recommendation': ai_recommendation,
            'recommended_tools': tool_integration.get_tools_for_lock(analysis)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/find-firmware', methods=['POST'])
def find_firmware():
    """Find appropriate firmware for phone"""
    data = request.json
    phone_model = data.get('phone_model')
    region = data.get('region', '')
    
    try:
        firmware_list = firmware_matcher.find_firmware(phone_model, region)
        ai_recommendation = ai_analyzer.recommend_firmware(firmware_list, phone_model)
        
        return jsonify({
            'success': True,
            'firmware_list': firmware_list,
            'ai_recommendation': ai_recommendation
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/execute-unlock', methods=['POST'])
def execute_unlock():
    """Execute unlock process using recommended tool"""
    data = request.json
    phone_model = data.get('phone_model')
    lock_type = data.get('lock_type')
    method = data.get('method')
    
    try:
        result = tool_integration.execute_unlock(
            phone_model=phone_model,
            lock_type=lock_type,
            method=method
        )
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'logs': result.get('logs', [])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/phone-database', methods=['GET'])
def get_phone_database():
    """Get all supported phones from database"""
    try:
        conn = sqlite3.connect('database/phone_database.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT brand, model, supported_locks FROM phones')
        phones = cursor.fetchall()
        
        phone_list = []
        for phone in phones:
            phone_list.append({
                'brand': phone[0],
                'model': phone[1],
                'supported_locks': json.loads(phone[2])
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'phones': phone_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
