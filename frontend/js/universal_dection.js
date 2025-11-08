// Universal Phone Detection JavaScript
class UniversalPhoneDetection {
    constructor() {
        this.detectionMethods = [
            'adb',
            'fastboot', 
            'usb_raw',
            'emergency_modes',
            'bootloader',
            'system_enumeration'
        ];
        this.currentDetection = null;
    }

    async startUniversalDetection() {
        this.showDetectionStatus('Starting universal phone detection...', 'detecting');
        
        try {
            const response = await fetch('/api/detect-any-phone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.handleDetectionSuccess(result);
            } else {
                this.handleDetectionError(result);
            }
        } catch (error) {
            this.handleDetectionError({ error: error.message });
        }
    }

    async forceDetectDevice(vendorId, productId) {
        this.showDetectionStatus(`Forcing detection of device ${vendorId}:${productId}...`, 'detecting');
        
        try {
            const response = await fetch('/api/force-detect-device', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    vendor_id: vendorId,
                    product_id: productId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.handleDetectionSuccess(result);
            } else {
                this.handleDetectionError(result);
            }
        } catch (error) {
            this.handleDetectionError({ error: error.message });
        }
    }

    handleDetectionSuccess(result) {
        const detection = result.detection;
        const identification = result.identification;
        
        this.currentDetection = {
            detection: detection,
            identification: identification,
            confidence: result.combined_confidence || 0.5
        };
        
        this.updateDetectionUI(detection, identification);
        this.showDetectionStatus('Device detected successfully!', 'success');
        
        // Update the main app's current device
        if (window.app) {
            window.app.currentDevice = identification;
        }
    }

    handleDetectionError(result) {
        this.showDetectionStatus(`Detection failed: ${result.error}`, 'error');
        
        // Show help suggestions
        if (result.suggestions) {
            this.showDetectionHelp(result.suggestions);
        }
        
        this.showUniversalDetectionHelp();
    }

    updateDetectionUI(detection, identification) {
        // Update detection methods used
        const methodsElement = document.getElementById('detection-methods');
        if (methodsElement && detection.detection_methods) {
            methodsElement.innerHTML = detection.detection_methods.map(method => 
                `<span class="detection-method">${method}</span>`
            ).join('');
        }
        
        // Update connection quality
        const qualityElement = document.getElementById('connection-quality');
        if (qualityElement && detection.connection_quality) {
            qualityElement.textContent = detection.connection_quality;
            qualityElement.className = `quality-${detection.connection_quality}`;
        }
        
        // Update reliability score
        const reliabilityElement = document.getElementById('reliability-score');
        if (reliabilityElement && detection.reliability_score) {
            const score = Math.round(detection.reliability_score * 100);
            reliabilityElement.textContent = `${score}%`;
            reliabilityElement.style.background = this.getReliabilityColor(score);
        }
        
        // Show the detected device
        this.showDetectedDevice(identification, detection);
    }

    showDetectedDevice(identification, detection) {
        const deviceElement = document.getElementById('detected-device');
        const modelElement = document.getElementById('detected-model');
        const detailsElement = document.getElementById('detected-details');
        const confidenceElement = document.getElementById('confidence-badge');
        
        if (!deviceElement) return;
        
        modelElement.textContent = `${identification.brand} ${identification.model}`;
        
        let details = [];
        if (identification.model_number && identification.model_number !== 'N/A') {
            details.push(`Model: ${identification.model_number}`);
        }
        if (identification.android_version && identification.android_version !== 'Unknown') {
            details.push(`Android: ${identification.android_version}`);
        }
        if (identification.supported_locks) {
            details.push(`Supported: ${identification.supported_locks.join(', ')}`);
        }
        
        detailsElement.textContent = details.join(' • ') || 'Device details not available';
        
        // Confidence badge
        const confidence = Math.round(identification.detection_confidence * 100);
        confidenceElement.textContent = `${confidence}%`;
        
        // Color code confidence
        if (confidence >= 80) {
            confidenceElement.style.background = '#10b981';
        } else if (confidence >= 60) {
            confidenceElement.style.background = '#f59e0b';
        } else {
            confidenceElement.style.background = '#ef4444';
        }
        
        // Show detection method
        const methodElement = document.createElement('div');
        methodElement.className = 'detection-method-info';
        methodElement.textContent = `Detected via: ${identification.detection_method}`;
        detailsElement.appendChild(methodElement);
        
        deviceElement.style.display = 'block';
        
        // Show improvement suggestions if any
        if (detection.improvement_suggestions) {
            this.showImprovementSuggestions(detection.improvement_suggestions);
        }
    }

    showDetectionStatus(message, status) {
        const statusElement = document.getElementById('detection-status');
        if (!statusElement) return;
        
        const messageElement = statusElement.querySelector('.status-message');
        const indicator = statusElement.querySelector('.status-indicator');
        
        if (messageElement) {
            messageElement.textContent = message;
        }
        
        indicator.className = 'status-indicator ' + status;
        
        // Add to detection log
        this.addToDetectionLog(message, status);
    }

    addToDetectionLog(message, type) {
        const logElement = document.getElementById('detection-log');
        if (!logElement) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        logEntry.innerHTML = `
            <span class="log-time">[${timestamp}]</span>
            <span class="log-message">${message}</span>
        `;
        
        logEntry.appendChild(logEntry);
        logElement.scrollTop = logElement.scrollHeight;
    }

    showDetectionHelp(suggestions) {
        const helpElement = document.getElementById('detection-help');
        if (!helpElement) return;
        
        helpElement.innerHTML = `
            <h4>Detection Help</h4>
            <ul>
                ${suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
            </ul>
        `;
        helpElement.style.display = 'block';
    }

    showImprovementSuggestions(suggestions) {
        const suggestionsElement = document.getElementById('improvement-suggestions');
        if (!suggestionsElement) return;
        
        suggestionsElement.innerHTML = `
            <h5>Improve Detection:</h5>
            <ul>
                ${suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
            </ul>
        `;
        suggestionsElement.style.display = 'block';
    }

    async showUniversalDetectionHelp() {
        try {
            const response = await fetch('/api/detection-help');
            const result = await response.json();
            
            if (result.success) {
                this.displayUniversalHelp(result.help);
            }
        } catch (error) {
            console.error('Error loading detection help:', error);
        }
    }

    displayUniversalHelp(helpInfo) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        modal.innerHTML = `
            <div class="modal-content large">
                <div class="modal-header">
                    <h3>Universal Phone Detection Help</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="help-section">
                        <h4>Detection Methods</h4>
                        <ul>
                            ${helpInfo.universal_methods.map(method => `<li>${method}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div class="help-section">
                        <h4>Troubleshooting</h4>
                        <ul>
                            ${helpInfo.troubleshooting.map(step => `<li>${step}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div class="help-section">
                        <h4>Emergency Mode Entry</h4>
                        <ul>
                            ${helpInfo.emergency_modes.map(mode => `<li>${mode}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div class="help-section">
                        <h4>Manual Device Selection</h4>
                        <p>If automatic detection fails, you can manually select your device:</p>
                        <button class="btn btn-primary" onclick="app.showManualSelection()">
                            Select Device Manually
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    getReliabilityColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#f59e0b';
        return '#ef4444';
    }

    // USB Port Fixing Methods
    async fixUSBRecognition() {
        this.showDetectionStatus('Attempting to fix USB recognition...', 'detecting');
        
        try {
            // Try different detection methods sequentially
            const methods = ['adb', 'fastboot', 'usb_raw', 'emergency_modes'];
            
            for (const method of methods) {
                this.showDetectionStatus(`Trying ${method} detection...`, 'detecting');
                
                // Simulate method attempt (in real implementation, this would call specific endpoints)
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                // Check if device is now detected
                const response = await fetch('/api/detect-any-phone', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    this.handleDetectionSuccess(result);
                    return;
                }
            }
            
            this.showDetectionStatus('USB recognition fix attempts completed', 'error');
            this.showUniversalDetectionHelp();
            
        } catch (error) {
            this.handleDetectionError({ error: error.message });
        }
    }

    // Method to handle unrecognized USB devices
    handleUnrecognizedUSB(vendorId, productId) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Unrecognized USB Device</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <p>Device detected but not recognized as a phone:</p>
                    <div class="device-info">
                        <strong>Vendor ID:</strong> ${vendorId}<br>
                        <strong>Product ID:</strong> ${productId}
                    </div>
                    
                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="universalDetection.forceDetectDevice('${vendorId}', '${productId}')">
                            Force Detection
                        </button>
                        <button class="btn btn-outline" onclick="universalDetection.fixUSBRecognition()">
                            Fix USB Recognition
                        </button>
                        <button class="btn btn-secondary" onclick="app.showManualSelection()">
                            Select Manually
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
}

// Initialize universal detection
const universalDetection = new UniversalPhoneDetection();

// Add universal detection styles
const universalStyles = `
.detection-methods {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 16px;
}

.detection-method {
    background: #3b82f6;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
}

.connection-quality {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    margin-left: 8px;
}

.quality-excellent { background: #10b981; color: white; }
.quality-good { background: #f59e0b; color: white; }
.quality-fair { background: #f59e0b; color: white; }
.quality-poor { background: #ef4444; color: white; }

.reliability-score {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 4px;
    color: white;
    font-size: 12px;
    font-weight: 500;
}

.detection-method-info {
    font-size: 12px;
    color: #6b7280;
    margin-top: 8px;
    font-style: italic;
}

#detection-log {
    background: #1f2937;
    color: #d1d5db;
    padding: 12px;
    border-radius: 8px;
    max-height: 200px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    margin-top: 16px;
}

.log-entry {
    margin-bottom: 4px;
    padding: 2px 0;
}

.log-detecting { color: #f59e0b; }
.log-success { color: #10b981; }
.log-error { color: #ef4444; }

#detection-help,
#improvement-suggestions {
    background: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 8px;
    padding: 16px;
    margin-top: 16px;
}

#detection-help h4,
#improvement-suggestions h5 {
    color: #92400e;
    margin-bottom: 8px;
}

#detection-help ul,
#improvement-suggestions ul {
    color: #92400e;
    margin-left: 20px;
}

.help-section {
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #e5e7eb;
}

.help-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
}

.help-section h4 {
    color: #374151;
    margin-bottom: 12px;
}

.action-buttons {
    display: flex;
    gap: 12px;
    margin-top: 16px;
    flex-wrap: wrap;
}

.device-info {
    background: #f3f4f6;
    padding: 12px;
    border-radius: 6px;
    margin: 12px 0;
    font-family: 'Courier New', monospace;
}

.universal-detection-mode {
    border-left: 4px solid #3b82f6;
    background: #f0f9ff;
}

.universal-detection-mode .method-card {
    border-color: #3b82f6;
}
`;

// Inject universal detection styles
const universalStyleSheet = document.createElement('style');
universalStyleSheet.textContent = universalStyles;
document.head.appendChild(universalStyleSheet);
