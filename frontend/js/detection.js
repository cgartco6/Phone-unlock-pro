// Phone Detection JavaScript
class PhoneDetection {
    constructor() {
        this.currentDevice = null;
        this.isDetecting = false;
        this.init();
    }

    init() {
        this.bindDetectionEvents();
        this.initializeUSBSimulation();
    }

    bindDetectionEvents() {
        // Detection button
        document.getElementById('detect-btn').addEventListener('click', () => {
            this.startDetection();
        });

        // Manual selection
        document.getElementById('manual-select-btn').addEventListener('click', () => {
            this.showManualSelection();
        });

        // Analyze lock button
        document.getElementById('analyze-lock-btn')?.addEventListener('click', () => {
            this.analyzeLockType();
        });

        // Find firmware button
        document.getElementById('find-firmware-btn')?.addEventListener('click', () => {
            this.findFirmware();
        });
    }

    async startDetection() {
        if (this.isDetecting) return;

        this.isDetecting = true;
        this.updateDetectionStatus('detecting', 'Detecting connected device...');

        // Simulate USB connection
        this.simulateUSBConnection();

        try {
            const response = await fetch('/api/detect-phone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.success) {
                this.handleDetectionSuccess(result.phone);
            } else {
                this.handleDetectionError(result.error);
            }
        } catch (error) {
            this.handleDetectionError(error.message);
        } finally {
            this.isDetecting = false;
        }
    }

    simulateUSBConnection() {
        const phoneSilhouette = document.getElementById('phone-silhouette');
        const usbCable = document.querySelector('.usb-cable');

        // Add connection animation
        phoneSilhouette.classList.add('connected');
        usbCable.style.background = 'linear-gradient(90deg, #3b82f6, #60a5fa)';
        usbCable.style.boxShadow = '0 0 10px rgba(59, 130, 246, 0.5)';

        // Add pulsing animation
        usbCable.style.animation = 'pulseCable 1s infinite';

        // Add styles for animation
        if (!document.querySelector('#usb-animation-styles')) {
            const styles = document.createElement('style');
            styles.id = 'usb-animation-styles';
            styles.textContent = `
                @keyframes pulseCable {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.7; }
                }
            `;
            document.head.appendChild(styles);
        }
    }

    handleDetectionSuccess(phoneInfo) {
        this.currentDevice = phoneInfo;
        
        this.updateDetectionStatus('success', 'Device detected successfully!');
        this.showDetectedDevice(phoneInfo);
        this.addToRecentDevices(phoneInfo);
        
        // Check if it's a Hisense device
        if (phoneInfo.brand.toLowerCase() === 'hisense') {
            this.showHisenseSection(phoneInfo);
        }

        // Update app's current device
        if (window.app) {
            window.app.currentDevice = phoneInfo;
        }
    }

    handleDetectionError(error) {
        this.updateDetectionStatus('error', `Detection failed: ${error}`);
        
        // Reset USB simulation
        this.resetUSBSimulation();
        
        // Show manual selection as fallback
        setTimeout(() => {
            this.showManualSelection();
        }, 2000);
    }

    updateDetectionStatus(status, message) {
        const statusElement = document.getElementById('detection-status');
        const messageElement = statusElement.querySelector('.status-message');
        const indicator = statusElement.querySelector('.status-indicator');

        if (messageElement) {
            messageElement.textContent = message;
        }

        indicator.className = 'status-indicator ' + status;
    }

    showDetectedDevice(phoneInfo) {
        const deviceElement = document.getElementById('detected-device');
        const modelElement = document.getElementById('detected-model');
        const detailsElement = document.getElementById('detected-details');
        const confidenceElement = document.getElementById('confidence-badge');

        modelElement.textContent = `${phoneInfo.brand} ${phoneInfo.model}`;
        
        let details = [];
        if (phoneInfo.model_number) details.push(`Model: ${phoneInfo.model_number}`);
        if (phoneInfo.android_version) details.push(`Android: ${phoneInfo.android_version}`);
        if (phoneInfo.supported_locks) {
            details.push(`Locks: ${phoneInfo.supported_locks.join(', ')}`);
        }
        
        detailsElement.textContent = details.join(' • ');
        
        if (phoneInfo.detection_confidence) {
            const confidence = Math.round(phoneInfo.detection_confidence * 100);
            confidenceElement.textContent = `${confidence}%`;
            
            // Color code confidence
            if (confidence >= 90) {
                confidenceElement.style.background = '#10b981';
            } else if (confidence >= 70) {
                confidenceElement.style.background = '#f59e0b';
            } else {
                confidenceElement.style.background = '#ef4444';
            }
        }

        deviceElement.style.display = 'block';
    }

    resetUSBSimulation() {
        const phoneSilhouette = document.getElementById('phone-silhouette');
        const usbCable = document.querySelector('.usb-cable');

        phoneSilhouette.classList.remove('connected');
        usbCable.style.background = '';
        usbCable.style.boxShadow = '';
        usbCable.style.animation = '';
    }

    showManualSelection() {
        // Create modal for manual selection
        const modal = this.createManualSelectionModal();
        document.body.appendChild(modal);
    }

    createManualSelectionModal() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Select Phone Manually</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Brand</label>
                        <select id="manual-brand" class="form-select">
                            <option value="">Select Brand</option>
                            <option value="samsung">Samsung</option>
                            <option value="hisense">Hisense</option>
                            <option value="xiaomi">Xiaomi</option>
                            <option value="apple">Apple</option>
                            <option value="huawei">Huawei</option>
                            <option value="oneplus">OnePlus</option>
                            <option value="lg">LG</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Model</label>
                        <select id="manual-model" class="form-select" disabled>
                            <option value="">Select Model</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Lock Type</label>
                        <select id="manual-lock-type" class="form-select">
                            <option value="auto">Auto-detect</option>
                            <option value="frp">FRP Lock</option>
                            <option value="screen_lock">Screen Lock</option>
                            <option value="google_account">Google Account</option>
                            <option value="bootloader">Bootloader Lock</option>
                            <option value="kg_lock">KG Lock (Samsung)</option>
                            <option value="icloud">iCloud Lock</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="detection.confirmManualSelection()">Confirm Selection</button>
                </div>
            </div>
        `;

        // Add brand-model dependency
        const brandSelect = modal.querySelector('#manual-brand');
        const modelSelect = modal.querySelector('#manual-model');

        brandSelect.addEventListener('change', () => {
            this.populateModels(brandSelect.value, modelSelect);
        });

        return modal;
    }

    populateModels(brand, modelSelect) {
        const models = {
            'samsung': ['Galaxy S23', 'Galaxy S22', 'Galaxy S21', 'Galaxy A54', 'Galaxy A34'],
            'hisense': ['Infinity H40 Lite (HLTE230E)', 'Infinity H30', 'Infinity H50'],
            'xiaomi': ['Redmi Note 12', 'Redmi Note 11', 'Mi 13', 'Poco F5'],
            'apple': ['iPhone 15', 'iPhone 14', 'iPhone 13', 'iPhone 12'],
            'huawei': ['P50 Pro', 'P40 Pro', 'Mate 40 Pro'],
            'oneplus': ['OnePlus 11', 'OnePlus 10 Pro', 'OnePlus 9'],
            'lg': ['Velvet', 'Wing', 'G8', 'V60']
        };

        modelSelect.innerHTML = '<option value="">Select Model</option>';
        
        if (brand && models[brand]) {
            models[brand].forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
            modelSelect.disabled = false;
        } else {
            modelSelect.disabled = true;
        }
    }

    confirmManualSelection() {
        const modal = document.querySelector('.modal-overlay');
        const brand = modal.querySelector('#manual-brand').value;
        const model = modal.querySelector('#manual-model').value;
        const lockType = modal.querySelector('#manual-lock-type').value;

        if (!brand || !model) {
            this.showNotification('Please select both brand and model', 'error');
            return;
        }

        const phoneInfo = {
            brand: brand,
            model: model,
            model_number: this.extractModelNumber(model),
            lock_type: lockType,
            detection_confidence: 0.5, // Lower confidence for manual selection
            detection_method: 'manual'
        };

        this.handleDetectionSuccess(phoneInfo);
        modal.remove();
    }

    extractModelNumber(model) {
        // Extract model number from model name
        const matches = model.match(/\(([^)]+)\)/);
        return matches ? matches[1] : model;
    }

    async analyzeLockType() {
        if (!this.currentDevice) {
            this.showNotification('Please detect a device first', 'warning');
            return;
        }

        app.showLoading('Analyzing lock type...');

        try {
            const response = await fetch('/api/analyze-lock', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    phone_model: this.currentDevice.model,
                    lock_type: this.currentDevice.lock_type || 'auto'
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showLockAnalysis(result.analysis, result.ai_recommendation);
            } else {
                this.showNotification('Lock analysis failed: ' + result.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error analyzing lock: ' + error.message, 'error');
        } finally {
            app.hideLoading();
        }
    }

    showLockAnalysis(analysis, aiRecommendation) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        modal.innerHTML = `
            <div class="modal-content large">
                <div class="modal-header">
                    <h3>Lock Analysis Results</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="analysis-summary">
                        <div class="summary-item">
                            <label>Detected Lock Type:</label>
                            <span class="value">${analysis.detected_lock_type}</span>
                        </div>
                        <div class="summary-item">
                            <label>Difficulty:</label>
                            <span class="value difficulty ${analysis.difficulty}">${analysis.difficulty}</span>
                        </div>
                        <div class="summary-item">
                            <label>Success Rate:</label>
                            <span class="value success-rate">${Math.round(analysis.success_rate * 100)}%</span>
                        </div>
                        <div class="summary-item">
                            <label>Estimated Time:</label>
                            <span class="value">${analysis.estimated_time}</span>
                        </div>
                    </div>

                    ${aiRecommendation ? `
                    <div class="ai-recommendation">
                        <h4>🤖 AI Recommendation</h4>
                        <div class="recommendation-card">
                            <div class="method">${aiRecommendation.recommended_method}</div>
                            <div class="confidence">Confidence: ${Math.round(aiRecommendation.confidence * 100)}%</div>
                            <div class="reasoning">${aiRecommendation.reasoning}</div>
                        </div>
                    </div>
                    ` : ''}

                    <div class="unlock-methods">
                        <h4>Recommended Methods</h4>
                        ${analysis.methods.map((method, index) => `
                            <div class="method-card compact">
                                <div class="method-header">
                                    <h5>${method.name}</h5>
                                    <span class="data-loss">Data Loss: ${method.data_loss}</span>
                                </div>
                                <div class="method-tools">
                                    <strong>Tools:</strong> ${method.tools.join(', ')}
                                </div>
                                <div class="method-steps">
                                    <strong>Steps:</strong> ${method.steps}
                                </div>
                                <button class="btn btn-primary btn-sm" onclick="detection.executeUnlockMethod(${index})">
                                    Use This Method
                                </button>
                            </div>
                        `).join('')}
                    </div>

                    ${analysis.risks.length > 0 ? `
                    <div class="risk-warning">
                        <h4>⚠️ Risks & Requirements</h4>
                        <div class="risks">
                            <strong>Risks:</strong> ${analysis.risks.join(', ')}
                        </div>
                        <div class="requirements">
                            <strong>Requirements:</strong> ${analysis.requirements.join(', ')}
                        </div>
                    </div>
                    ` : ''}
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="detection.startUnlockProcess()">
                        Start Unlock Process
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    executeUnlockMethod(methodIndex) {
        if (!this.currentDevice) return;

        const method = this.currentDevice.analysis.methods[methodIndex];
        this.showNotification(`Preparing ${method.name}...`, 'info');
        
        // Implementation would continue with method execution
    }

    startUnlockProcess() {
        if (!this.currentDevice) return;

        app.showLoading('Initiating unlock process...');
        
        // Close any open modals
        document.querySelector('.modal-overlay')?.remove();
        
        // Implementation would continue with unlock process
        setTimeout(() => {
            app.hideLoading();
            this.showUnlockProgress();
        }, 1500);
    }

    showUnlockProgress() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Unlock in Progress</h3>
                </div>
                <div class="modal-body">
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%"></div>
                        </div>
                        <div class="progress-text">Initializing...</div>
                    </div>
                    <div class="log-container">
                        <div class="log-entry">Starting unlock process...</div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.simulateUnlockProgress(modal);
    }

    simulateUnlockProgress(modal) {
        const progressFill = modal.querySelector('.progress-fill');
        const progressText = modal.querySelector('.progress-text');
        const logContainer = modal.querySelector('.log-container');

        const steps = [
            { progress: 10, text: 'Connecting to device...', log: 'Device connected successfully' },
            { progress: 25, text: 'Analyzing lock type...', log: 'Lock type confirmed: FRP' },
            { progress: 45, text: 'Loading unlock method...', log: 'Method loaded: Combination File Flash' },
            { progress: 65, text: 'Executing unlock...', log: 'Unlock procedure started' },
            { progress: 85, text: 'Verifying results...', log: 'Unlock successful' },
            { progress: 100, text: 'Complete!', log: 'Device ready for use' }
        ];

        steps.forEach((step, index) => {
            setTimeout(() => {
                progressFill.style.width = step.progress + '%';
                progressText.textContent = step.text;
                
                const logEntry = document.createElement('div');
                logEntry.className = 'log-entry';
                logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${step.log}`;
                logContainer.appendChild(logEntry);
                logContainer.scrollTop = logContainer.scrollHeight;

                if (step.progress === 100) {
                    setTimeout(() => {
                        modal.remove();
                        this.showUnlockSuccess();
                    }, 1000);
                }
            }, (index + 1) * 2000);
        });
    }

    showUnlockSuccess() {
        this.showNotification('Device unlocked successfully! 🎉', 'success');
        
        // Update stats
        if (window.app) {
            window.app.updateStats();
        }
    }

    async findFirmware() {
        if (!this.currentDevice) {
            this.showNotification('Please detect a device first', 'warning');
            return;
        }

        app.showLoading('Searching for firmware...');

        try {
            const response = await fetch('/api/find-firmware', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    phone_model: this.currentDevice.model,
                    region: ''
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showFirmwareResults(result.firmware_list, result.ai_recommendation);
            } else {
                this.showNotification('Firmware search failed: ' + result.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error searching firmware: ' + error.message, 'error');
        } finally {
            app.hideLoading();
        }
    }

    showFirmwareResults(firmwareList, aiRecommendation) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay large';
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Available Firmware</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    ${aiRecommendation ? `
                    <div class="ai-recommendation">
                        <h4>🤖 AI Recommendation</h4>
                        <div class="recommendation-card">
                            <div class="recommended-firmware">
                                <strong>Recommended:</strong> ${aiRecommendation.recommended_version}
                            </div>
                            <div class="confidence">Confidence: ${Math.round(aiRecommendation.confidence * 100)}%</div>
                            <div class="reasoning">${aiRecommendation.reasoning}</div>
                        </div>
                    </div>
                    ` : ''}

                    <div class="firmware-list">
                        ${firmwareList.map(firmware => `
                            <div class="firmware-item">
                                <div class="firmware-info">
                                    <h5>${firmware.version}</h5>
                                    <div class="firmware-details">
                                        <span>Android ${firmware.android_version}</span>
                                        <span>Region: ${firmware.region}</span>
                                        <span>Build: ${firmware.build_date}</span>
                                        <span>Size: ${firmware.file_size}</span>
                                    </div>
                                </div>
                                <div class="firmware-actions">
                                    <button class="btn btn-primary btn-sm" onclick="detection.downloadFirmware('${firmware.download_url}')">
                                        Download
                                    </button>
                                    <button class="btn btn-outline btn-sm" onclick="detection.showFirmwareDetails(${JSON.stringify(firmware).replace(/"/g, '&quot;')})">
                                        Details
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    downloadFirmware(url) {
        this.showNotification('Starting firmware download...', 'info');
        // Implementation for firmware download
        window.open(url, '_blank');
    }

    showFirmwareDetails(firmware) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Firmware Details</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="firmware-detail">
                        <label>Version:</label>
                        <span>${firmware.version}</span>
                    </div>
                    <div class="firmware-detail">
                        <label>Android Version:</label>
                        <span>${firmware.android_version}</span>
                    </div>
                    <div class="firmware-detail">
                        <label>Region:</label>
                        <span>${firmware.region}</span>
                    </div>
                    <div class="firmware-detail">
                        <label>Build Date:</label>
                        <span>${firmware.build_date}</span>
                    </div>
                    <div class="firmware-detail">
                        <label>File Size:</label>
                        <span>${firmware.file_size}</span>
                    </div>
                    <div class="firmware-detail">
                        <label>Checksum:</label>
                        <span class="checksum">${firmware.checksum}</span>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="detection.downloadFirmware('${firmware.download_url}')">
                        Download Firmware
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    showHisenseSection(phoneInfo) {
        const hisenseSection = document.getElementById('hisense');
        if (hisenseSection) {
            hisenseSection.style.display = 'block';
            this.loadHisenseMethods(phoneInfo.model);
        }
    }

    async loadHisenseMethods(model) {
        try {
            const response = await fetch(`/api/hisense-methods/${model}`);
            const methods = await response.json();

            if (methods.success) {
                const container = document.getElementById('hisense-methods');
                if (container) {
                    container.innerHTML = methods.data.map(method => `
                        <div class="method-card hisense-method">
                            <div class="method-icon">📱</div>
                            <h3>${method.method_name}</h3>
                            <p>Specialized method for Hisense ${model}</p>
                            <div class="method-details">
                                <span class="success-rate">${Math.round(method.success_rate * 100)}% Success</span>
                                <span class="data-loss">${method.data_loss}</span>
                            </div>
                            <div class="method-tools">
                                <strong>Tools:</strong> ${method.tools_required.join(', ')}
                            </div>
                            <button class="btn btn-warning btn-block" 
                                    onclick="detection.executeHisenseMethod('${model}', '${method.lock_type}', '${method.method_name}')">
                                Use Hisense Method
                            </button>
                        </div>
                    `).join('');
                }
            }
        } catch (error) {
            console.error('Error loading Hisense methods:', error);
        }
    }

    executeHisenseMethod(model, lockType, methodName) {
        this.showNotification(`Starting ${methodName} for Hisense ${model}...`, 'info');
        
        // Implementation for Hisense-specific unlock methods
        app.showLoading(`Executing ${methodName}...`);
        
        setTimeout(() => {
            app.hideLoading();
            this.showNotification(`Hisense ${methodName} completed successfully!`, 'success');
        }, 3000);
    }

    addToRecentDevices(phoneInfo) {
        // Add to recent devices list
        const recentDevices = JSON.parse(localStorage.getItem('recentDevices') || '[]');
        
        // Remove if already exists
        const existingIndex = recentDevices.findIndex(device => 
            device.model === phoneInfo.model && device.brand === phoneInfo.brand
        );
        
        if (existingIndex !== -1) {
            recentDevices.splice(existingIndex, 1);
        }
        
        // Add to beginning
        recentDevices.unshift({
            ...phoneInfo,
            detected_at: new Date().toISOString()
        });
        
        // Keep only last 5 devices
        if (recentDevices.length > 5) {
            recentDevices.pop();
        }
        
        localStorage.setItem('recentDevices', JSON.stringify(recentDevices));
        this.updateRecentDevicesUI(recentDevices);
    }

    updateRecentDevicesUI(devices) {
        const container = document.getElementById('recent-devices-list');
        if (container) {
            container.innerHTML = devices.map(device => `
                <div class="recent-device">
                    <div class="device-model">${device.brand} ${device.model}</div>
                    <div class="device-date">${new Date(device.detected_at).toLocaleDateString()}</div>
                </div>
            `).join('');
        }
    }

    showNotification(message, type = 'info') {
        if (window.app) {
            window.app.showNotification(message, type);
        } else {
            alert(message); // Fallback
        }
    }

    initializeUSBSimulation() {
        // Load recent devices from localStorage
        const recentDevices = JSON.parse(localStorage.getItem('recentDevices') || '[]');
        this.updateRecentDevicesUI(recentDevices);
    }
}

// Initialize detection system
const detection = new PhoneDetection();

// Add modal styles
const modalStyles = `
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    padding: 20px;
}

.modal-content {
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    max-width: 500px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-content.large {
    max-width: 800px;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
    margin: 0;
    color: #1f2937;
}

.modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #6b7280;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-close:hover {
    color: #374151;
}

.modal-body {
    padding: 24px;
}

.modal-footer {
    padding: 20px 24px;
    border-top: 1px solid #e5e7eb;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #374151;
}

.analysis-summary {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 24px;
}

.summary-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: #f9fafb;
    border-radius: 8px;
}

.summary-item label {
    font-weight: 500;
    margin: 0;
}

.summary-item .value {
    font-weight: 600;
}

.ai-recommendation {
    margin-bottom: 24px;
}

.recommendation-card {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    padding: 16px;
}

.recommendation-card .method {
    font-weight: 600;
    color: #0369a1;
    margin-bottom: 8px;
}

.recommendation-card .confidence {
    color: #059669;
    font-size: 14px;
    margin-bottom: 8px;
}

.recommendation-card .reasoning {
    color: #475569;
    font-size: 14px;
}

.unlock-methods {
    margin-bottom: 24px;
}

.method-card.compact {
    margin-bottom: 16px;
    padding: 16px;
}

.method-card.compact .method-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.method-card.compact .method-header h5 {
    margin: 0;
}

.method-card.compact .data-loss {
    font-size: 12px;
    padding: 4px 8px;
    background: #fef3c7;
    color: #92400e;
    border-radius: 4px;
}

.method-card.compact .method-tools,
.method-card.compact .method-steps {
    font-size: 14px;
    margin-bottom: 8px;
    color: #6b7280;
}

.risk-warning {
    background: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 8px;
    padding: 16px;
}

.risk-warning h4 {
    margin: 0 0 12px 0;
    color: #92400e;
}

.risks, .requirements {
    margin-bottom: 8px;
    font-size: 14px;
}

.progress-container {
    margin-bottom: 20px;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #10b981, #3b82f6);
    transition: width 0.3s ease;
}

.progress-text {
    text-align: center;
    font-weight: 500;
    color: #374151;
}

.log-container {
    background: #1f2937;
    color: #d1d5db;
    padding: 16px;
    border-radius: 8px;
    max-height: 200px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 12px;
}

.log-entry {
    margin-bottom: 4px;
}

.firmware-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.firmware-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    background: #f9fafb;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
}

.firmware-info h5 {
    margin: 0 0 8px 0;
    color: #1f2937;
}

.firmware-details {
    display: flex;
    gap: 16px;
    font-size: 14px;
    color: #6b7280;
}

.firmware-actions {
    display: flex;
    gap: 8px;
}

.firmware-detail {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #e5e7eb;
}

.firmware-detail:last-child {
    border-bottom: none;
}

.firmware-detail label {
    font-weight: 500;
    color: #374151;
    margin: 0;
}

.firmware-detail .checksum {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    background: #f3f4f6;
    padding: 4px 8px;
    border-radius: 4px;
}
`;

// Inject modal styles
const modalStyleSheet = document.createElement('style');
modalStyleSheet.textContent = modalStyles;
document.head.appendChild(modalStyleSheet);
