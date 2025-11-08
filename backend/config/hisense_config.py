# Hisense-specific configuration
HISENSE_CONFIG = {
    'supported_models': {
        'HLTE230E': {
            'name': 'Infinity H40 Lite',
            'chipset': 'unisoc_sc9863a',
            'android_versions': ['10'],
            'unlock_methods': {
                'frp': {
                    'primary': 'combination_file',
                    'fallback': 'edl_flash',
                    'tools': ['Hisense_Tool_v2.3', 'Octoplus'],
                    'success_rate': 0.85
                },
                'screen_lock': {
                    'primary': 'firmware_flash', 
                    'fallback': 'recovery_wipe',
                    'tools': ['Hisense_Tool_v2.3', 'Odin'],
                    'success_rate': 0.95
                },
                'google_account': {
                    'primary': 'combination_flash',
                    'tools': ['Hisense_Tool_v2.3'],
                    'success_rate': 0.9
                }
            },
            'firmware_sources': [
                'https://hisense-firmware.com/HLTE230E',
                'https://firmwarefile.com/hisense-hlte230e'
            ],
            'special_instructions': [
                'Requires specific USB drivers for Unisoc chipsets',
                'Download mode: Volume Down + Power',
                'Recovery mode: Volume Up + Power',
                'EDL mode: Test points under back cover'
            ]
        }
    },
    'tools': {
        'hisense_tool': {
            'version': '2.3',
            'supported_chipsets': ['unisoc_sc9863a', 'mt6739', 'mt6762'],
            'operations': ['flash', 'frp_remove', 'format', 'read_info']
        }
    },
    'drivers': {
        'unisoc': {
            'windows': 'https://drive.google.com/unisoc_driver.exe',
            'linux': 'builtin_cdc_acm'
        }
    }
}

# Unlock patterns for Hisense devices
HISENSE_UNLOCK_PATTERNS = {
    'download_mode': {
        'button_combo': ['volume_down', 'power'],
        'screen_indicator': 'Download Mode',
        'usb_id': '1782:4d00'
    },
    'recovery_mode': {
        'button_combo': ['volume_up', 'power'],
        'screen_indicator': 'Recovery Mode',
        'operations': ['wipe_cache', 'factory_reset']
    },
    'edl_mode': {
        'method': 'test_points',
        'test_points': ['TP501', 'TP502'],
        'usb_id': '1782:9008'
    }
}

# Firmware database for Hisense
HISENSE_FIRMWARE = {
    'HLTE230E': [
        {
            'version': 'HLTE230E_10_001',
            'android_version': '10',
            'build_date': '2023-05-15',
            'region': 'Global',
            'download_url': 'https://firmware.hisense.com/HLTE230E_10_001.zip',
            'file_size': '2.1GB',
            'checksum': 'a1b2c3d4e5f6'
        },
        {
            'version': 'HLTE230E_10_002', 
            'android_version': '10',
            'build_date': '2023-08-20',
            'region': 'Europe',
            'download_url': 'https://firmware.hisense.com/HLTE230E_10_002.zip',
            'file_size': '2.1GB',
            'checksum': 'b2c3d4e5f6g7'
        }
    ]
}
