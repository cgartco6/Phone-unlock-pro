import sqlite3
import json
from datetime import datetime

def init_database():
    """Initialize database with Hisense devices"""
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
    
    # Insert Hisense phones into main phones table
    hisense_phones = [
        ('Hisense', 'Infinity H40 Lite', 'HLTE230E', '10', 
         '["frp", "screen_lock", "google_account", "firmware_flash"]',
         'Unisoc SC9863A chipset - requires special tools', '1782', '4d00'),
        ('Hisense', 'Infinity H30', 'HLTE202E', '10',
         '["frp", "screen_lock", "firmware_flash"]',
         'Mediatek MT6762 - standard Mediatek procedures', '1782', '4d01'),
        ('Hisense', 'Infinity H50', 'HLTE300E', '11',
         '["frp", "screen_lock", "google_account", "firmware_flash"]', 
         'Updated version of H40 Lite', '1782', '4d02')
    ]
    
    for phone in hisense_phones:
        cursor.execute('''
            INSERT OR REPLACE INTO phones 
            (brand, model, model_number, android_version, supported_locks, notes, vendor_id, product_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', phone)
    
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
    
    print("Database initialized with Hisense devices and unlock methods")

if __name__ == "__main__":
    init_database()
