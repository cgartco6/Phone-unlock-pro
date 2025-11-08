-- Phone database schema
CREATE TABLE IF NOT EXISTS phones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    model_number TEXT,
    android_version TEXT,
    supported_locks TEXT,  -- JSON array of supported locks
    notes TEXT,
    vendor_id TEXT,
    product_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS firmware (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    version TEXT NOT NULL,
    region TEXT,
    download_url TEXT,
    file_size INTEGER,
    checksum TEXT,
    android_version TEXT,
    build_date TEXT,
    is_latest BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS unlock_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lock_type TEXT NOT NULL,
    phone_brand TEXT NOT NULL,
    phone_model TEXT,
    method_name TEXT NOT NULL,
    tools_required TEXT,  -- JSON array
    steps TEXT,  -- JSON array of steps
    success_rate REAL,
    difficulty TEXT,
    risks TEXT,  -- JSON array
    requirements TEXT,  -- JSON array
    estimated_time TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tool_integration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT NOT NULL,
    version TEXT,
    supported_brands TEXT,  -- JSON array
    supported_locks TEXT,  -- JSON array
    api_endpoint TEXT,
    commands TEXT,  -- JSON object of commands
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO phones (brand, model, model_number, android_version, supported_locks, vendor_id, product_id) VALUES
('Samsung', 'Galaxy S21', 'SM-G991U', '12', '["frp", "kg_lock", "bootloader", "screen_lock"]', '04e8', '6860'),
('Apple', 'iPhone 13', 'A2483', '15', '["icloud", "screen_lock"]', '05ac', '12a8'),
('Xiaomi', 'Redmi Note 10', 'M2101K7AG', '11', '["frp", "bootloader", "screen_lock"]', '2717', 'ff40');

INSERT INTO firmware (brand, model, version, region, android_version, download_url, is_latest) VALUES
('Samsung', 'Galaxy S21', 'G991USQU5CVA5', 'USA (TMB)', '12', 'https://firmware.samsung.com/G991USQU5CVA5', 1),
('Samsung', 'Galaxy S21', 'G991USQU5CVB2', 'USA (XAA)', '12', 'https://firmware.samsung.com/G991USQU5CVB2', 0);

INSERT INTO unlock_methods (lock_type, phone_brand, phone_model, method_name, tools_required, success_rate, difficulty) VALUES
('frp', 'Samsung', 'Galaxy S21', 'Combination File Flash', '["Odin", "Octoplus"]', 0.85, 'easy'),
('kg_lock', 'Samsung', 'Galaxy S21', 'Bootloader Patch', '["Octoplus", "Z3X"]', 0.6, 'hard'),
('icloud', 'Apple', 'iPhone 13', 'Server Bypass', '["Cheetah Pro"]', 0.7, 'medium');
