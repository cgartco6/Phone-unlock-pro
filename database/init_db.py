import sqlite3
import json
from datetime import datetime

def init_database():
    """Initialize database with all phone models"""
    conn = sqlite3.connect('database/phone_database.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS phones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            model_number TEXT,
            android_version TEXT,
            supported_locks TEXT,
            notes TEXT,
            vendor_id TEXT,
            product_id TEXT,
            detection_priority INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS hisense_devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL UNIQUE,
            chipset TEXT,
            android_versions TEXT,
            special_instructions TEXT,
            test_points TEXT,
            download_mode_combo TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS universal_detection_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT NOT NULL,
            pattern_data TEXT,
            description TEXT,
            confidence_level REAL DEFAULT 0.7,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    # Insert Hisense devices
    hisense_devices = [
        ('HLTE230E', 'Unisoc SC9863A', '["10"]', 
         'Use combination firmware for FRP bypass', 
         'TP501,TP502', 'Volume Down + Power'),
        ('HLTE202E', 'Mediatek MT6762', '["10"]', 
         'Standard Mediatek flashing procedure',
         'TP201,TP202', 'Volume Down + Power'),
        ('HLTE300E', 'Unisoc SC9863A', '["11"]',
         'Similar to HLTE230E with updated firmware',
         'TP301,TP302', 'Volume Down + Power')
    ]
    
    for device in hisense_devices:
        cursor.execute('''
            INSERT OR REPLACE INTO hisense_devices 
            (model, chipset, android_versions, special_instructions, test_points, download_mode_combo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', device)
    
    # Insert all phones into main phones table
    all_phones = [
        # Hisense devices
        ('Hisense', 'Infinity H40 Lite', 'HLTE230E', '10', 
         '["frp", "screen_lock", "google_account", "firmware_flash"]',
         'Unisoc SC9863A chipset - requires special tools', '1782', '4d00', 1),
        ('Hisense', 'Infinity H30', 'HLTE202E', '10',
         '["frp", "screen_lock", "firmware_flash"]',
         'Mediatek MT6762 - standard Mediatek procedures', '1782', '4d01', 1),
        ('Hisense', 'Infinity H50', 'HLTE300E', '11',
         '["frp", "screen_lock", "google_account", "firmware_flash"]', 
         'Updated version of H40 Lite', '1782', '4d02', 1),
        
        # Samsung devices
        ('Samsung', 'Galaxy A24', 'SM-A245F', '13',
         '["frp", "screen_lock", "google_account", "bootloader"]',
         'Popular budget device with good community support', '04e8', '6860', 1),
        ('Samsung', 'Galaxy A14', 'SM-A145F', '13',
         '["frp", "screen_lock", "google_account", "bootloader"]',
         'Entry-level Samsung with Exynos chipset', '04e8', '6861', 1),
        ('Samsung', 'Galaxy A05s', 'SM-A055F/DS', '13',
         '["frp", "screen_lock", "google_account", "bootloader"]',
         'Dual SIM variant with Snapdragon chipset', '04e8', '6862', 1),
        ('Samsung', 'Galaxy S21', 'SM-G991U', '12',
         '["frp", "kg_lock", "bootloader", "screen_lock"]',
         'Flagship device with KG lock protection', '04e8', '6863', 1),
        
        # Oppo devices
        ('Oppo', 'A78', 'CPH2525', '13',
         '["frp", "screen_lock", "google_account", "bootloader"]',
         'Mid-range Oppo with ColorOS', '22d9', '2764', 2),
        
        # Honor devices
        ('Honor', '90 Lite', 'RKY-LX1', '13',
         '["frp", "screen_lock", "google_account", "bootloader"]',
         'Honor budget device with Magic UI', '12d1', '107e', 2),
        ('Honor', '200', 'RNE-LX1', '14',
         '["frp", "screen_lock", "google_account", "bootloader"]',
         'Latest Honor mid-range device', '12d1', '107f', 2),
        
        # Huawei devices
        ('Huawei', 'X70', 'NOH-AN01', '12',
         '["frp", "screen_lock", "google_account"]',
         'Huawei device with HarmonyOS/EMUI', '12d1', '107b', 2),
        
        # Microsoft devices
        ('Microsoft', 'Lumia 640 LTE', 'RM-1073', '8.1',
         '["screen_lock", "microsoft_account"]',
         'Windows Phone device - different unlock methods', '045e', 'f0ca', 3),
        
        # Apple devices
        ('Apple', 'iPhone 13', 'A2483', '15',
         '["icloud", "screen_lock"]', '05ac', '12a8', 1),
        
        # Xiaomi devices
        ('Xiaomi', 'Redmi Note 10', 'M2101K7AG', '11',
         '["frp", "bootloader", "screen_lock"]', '2717', 'ff40', 1)
    ]
    
    for phone in all_phones:
        cursor.execute('''
            INSERT OR REPLACE INTO phones 
            (brand, model, model_number, android_version, supported_locks, notes, vendor_id, product_id, detection_priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', phone)
    
    # Insert universal detection patterns
    universal_patterns = [
        ('usb_handshake', '{"pattern": "55 53 42 43", "offset": 0}', 'USB control transfer signature'),
        ('adb_protocol', '{"pattern": "48 45 4c 4c 4f", "offset": 0}', 'ADB hello protocol'),
        ('fastboot_protocol', '{"pattern": "46 41 53 54 42 4f 4f 54", "offset": 0}', 'Fastboot protocol signature'),
        ('mtk_preloader', '{"pattern": "4D 4D 4D 01", "offset": 0}', 'Mediatek preloader mode'),
        ('qualcomm_edl', '{"pattern": "51 43 4F 4D 20 42 4F 4F 54 20 4C 4F 41 44 45 52", "offset": 0}', 'Qualcomm EDL mode'),
        ('samsung_download', '{"pattern": "53 41 4D 53 55 4E 47 20 4D 53 4D 20 54 4F 4F 4C 53", "offset": 0}', 'Samsung download mode'),
        ('spreadtrum_sci', '{"pattern": "53 50 52 44 42 4F 4F 54", "offset": 0}', 'Spreadtrum/Unisoc SCI mode')
    ]
    
    for pattern in universal_patterns:
        cursor.execute('''
            INSERT OR REPLACE INTO universal_detection_patterns 
            (pattern_type, pattern_data, description, confidence_level)
            VALUES (?, ?, ?, ?)
        ''', pattern)
    
    # Insert Hisense-specific unlock methods
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hisense_unlock_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            lock_type TEXT NOT NULL,
            method_name TEXT NOT NULL,
            tools_required TEXT,
            steps TEXT,
            success_rate REAL,
            data_loss TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    h40_methods = [
        ('HLTE230E', 'frp', 'Combination File Method', 
         '["Hisense_Tool_v2.3", "Octoplus"]',
         json.dumps([
             "Download combination firmware for HLTE230E",
             "Enter Download mode (Volume Down + Power)",
             "Flash combination firmware",
             "Access hidden menu (*#*#3646633#*#*)",
             "Reset FRP protection",
             "Flash stock firmware"
         ]), 0.85, 'complete'),
        
        ('HLTE230E', 'screen_lock', 'Firmware Flash Method',
         '["Hisense_Tool_v2.3", "Odin"]',
         json.dumps([
             "Download stock firmware for HLTE230E",
             "Enter Download mode",
             "Flash complete firmware package",
             "Wait for automatic reboot"
         ]), 0.95, 'complete'),
        
        ('HLTE230E', 'google_account', 'Factory Reset Method',
         '["Hisense_Tool_v2.3"]',
         json.dumps([
             "Boot to recovery mode (Volume Up + Power)",
             "Perform factory reset",
             "Skip Google account setup",
             "Use test points if recovery inaccessible"
         ]), 0.7, 'complete')
    ]
    
    for method in h40_methods:
        cursor.execute('''
            INSERT INTO hisense_unlock_methods 
            (model, lock_type, method_name, tools_required, steps, success_rate, data_loss)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', method)
    
    conn.commit()
    conn.close()
    
    print("Database initialized with all phone models and universal detection patterns")

if __name__ == "__main__":
    init_database()
