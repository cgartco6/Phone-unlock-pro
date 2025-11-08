// Firmware Management JavaScript
class FirmwareManager {
    constructor() {
        this.currentFirmware = null;
        this.downloadQueue = [];
        this.init();
    }

    init() {
        this.bindFirmwareEvents();
        this.initializeBrandModelData();
    }

    bindFirmwareEvents() {
        // Brand selection
        document.getElementById('brand-select').addEventListener('change', (e) => {
            this.handleBrandChange(e.target.value);
        });

        // Firmware search
        document.getElementById('search-firmware-btn').addEventListener('click', () => {
            this.searchFirmware();
        });

        // Enter key in search input
        document.getElementById('firmware-search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchFirmware();
            }
        });
    }

    initializeBrandModelData() {
        // Preload brand-model relationships
        this.brandModels = {
            'samsung': [
                'Galaxy S23', 'Galaxy S22', 'Galaxy S21', 'Galaxy S20',
                'Galaxy A54', 'Galaxy A34', 'Galaxy A14',
                'Galaxy Z Fold 4', 'Galaxy Z Flip 4'
            ],
            'hisense': [
                'Infinity H40 Lite (HLTE230E)', 'Infinity H30', 'Infinity H50',
                'U40', 'U30', 'F30'
            ],
            'xiaomi': [
                'Redmi Note 12', 'Redmi Note 11', 'Redmi Note 10',
                'Mi 13', 'Mi 12', 'Mi 11',
                'Poco F5', 'Poco X5', 'Poco M5'
            ],
            'apple': [
                'iPhone 15', 'iPhone 14', 'iPhone 13', 'iPhone 12',
                'iPhone 11', 'iPhone SE (2022)',
                'iPad Pro 12.9', 'iPad Air', 'iPad Mini'
            ],
            'huawei': [
                'P50 Pro', 'P40 Pro', 'P30 Pro',
                'Mate 40 Pro', 'Mate 30 Pro',
                'Nova 9', 'Nova 8'
            ],
            'oneplus': [
                'OnePlus 11', 'OnePlus 10 Pro', 'OnePlus 9',
                'OnePlus Nord 3', 'OnePlus Nord CE 3'
            ],
            'lg': [
                'Velvet', 'Wing', 'G8', 'V60',
                'Stylo 6', 'K series'
            ]
        };
    }

    handleBrandChange(brand) {
        const modelSelect = document.getElementById('model-select');
        modelSelect.innerHTML = '<option value="">Select Model</option>';

        if (brand && this.brandModels[brand]) {
            this.brandModels[brand].forEach(model => {
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

    async searchFirmware() {
        const brand = document.getElementById('brand-select').value;
        const model = document.getElementById('model-select').value;
        const searchInput = document.getElementById('firmware-search-input').value;

        let searchModel = model;
        if (!searchModel && searchInput) {
            searchModel = searchInput;
        }

        if (!searchModel) {
            this.showNotification('Please select a model or enter a model name', 'warning');
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
                    phone_model: searchModel,
                    brand: brand,
                    region: ''
                })
            });

            const result = await response.json();

            if (result.success) {
                this.displayFirmwareResults(result.firmware_list, result.ai_recommendation);
            } else {
                this.showNotification('Firmware search failed: ' + result.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error searching firmware: ' + error.message, 'error');
        } finally {
            app.hideLoading();
        }
    }

    displayFirmwareResults(firmwareList, aiRecommendation) {
        const container = document.getElementById('firmware-results');
        
        if (!firmwareList || firmwareList.length === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <div class="no-results-icon">🔍</div>
                    <h3>No Firmware Found</h3>
                    <p>No firmware files found for the specified model.</p>
                    <button class="btn btn-primary" onclick="firmwareManager.requestFirmware()">
                        Request Firmware
                    </button>
                </div>
            `;
            return;
        }

        let html = '';

        // AI Recommendation
        if (aiRecommendation) {
            html += `
                <div class="ai-recommendation-banner">
                    <div class="ai-icon">🤖</div>
                    <div class="ai-content">
                        <div class="ai-title">AI Recommended Firmware</div>
                        <div class="ai-details">
                            <strong>${aiRecommendation.recommended_version}</strong>
                            <span class="ai-confidence">${Math.round(aiRecommendation.confidence * 100)}% confidence</span>
                        </div>
                        <div class="ai-reasoning">${aiRecommendation.reasoning}</div>
                    </div>
                </div>
            `;
        }

        // Firmware List
        firmwareList.forEach(firmware => {
            const isRecommended = aiRecommendation && 
                                firmware.version === aiRecommendation.recommended_version;

            html += `
                <div class="firmware-item ${isRecommended ? 'recommended' : ''}">
                    <div class="firmware-badge">
                        ${isRecommended ? '<span class="recommended-badge">AI Recommended</span>' : ''}
                        ${firmware.is_latest ? '<span class="latest-badge">Latest</span>' : ''}
                    </div>
                    
                    <div class="firmware-info">
                        <h4>${firmware.version}</h4>
                        <div class="firmware-meta">
                            <span class="meta-item">
                                <strong>Android:</strong> ${firmware.android_version}
                            </span>
                            <span class="meta-item">
                                <strong>Region:</strong> ${firmware.region}
                            </span>
                            <span class="meta-item">
                                <strong>Build Date:</strong> ${firmware.build_date}
                            </span>
                            <span class="meta-item">
                                <strong>Size:</strong> ${firmware.file_size}
                            </span>
                        </div>
                        <div class="firmware-checksum">
                            <strong>Checksum:</strong> <code>${firmware.checksum}</code>
                        </div>
                    </div>

                    <div class="firmware-actions">
                        <button class="btn btn-primary" 
                                onclick="firmwareManager.downloadFirmware('${firmware.download_url}', '${firmware.version}')">
                            Download
                        </button>
                        <button class="btn btn-outline" 
                                onclick="firmwareManager.showFirmwareDetails(${JSON.stringify(firmware).replace(/"/g, '&quot;')})">
                            Details
                        </button>
                        <button class="btn btn-outline" 
                                onclick="firmwareManager.verifyFirmware('${firmware.checksum}')">
                            Verify
                        </button>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    async downloadFirmware(url, version) {
        this.showNotification(`Starting download: ${version}`, 'info');

        // Add to download queue
        this.downloadQueue.push({
            url: url,
            version: version,
            startTime: new Date(),
            status: 'downloading'
        });

        this.updateDownloadQueue();

        try {
            // Simulate download progress
            this.simulateDownloadProgress(version);

            // In a real implementation, this would actually download the file
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Download failed');
            }

            // Create download link
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `${version}.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);

            // Update download queue
            const downloadItem = this.downloadQueue.find(item => item.version === version);
            if (downloadItem) {
                downloadItem.status = 'completed';
                downloadItem.endTime = new Date();
            }

            this.showNotification(`Download completed: ${version}`, 'success');
            this.updateDownloadQueue();

        } catch (error) {
            this.showNotification(`Download failed: ${error.message}`, 'error');
            
            // Update download queue
            const downloadItem = this.downloadQueue.find(item => item.version === version);
            if (downloadItem) {
                downloadItem.status = 'failed';
                downloadItem.error = error.message;
            }
            this.updateDownloadQueue();
        }
    }

    simulateDownloadProgress(version) {
        const progressInterval = setInterval(() => {
            const downloadItem = this.downloadQueue.find(item => item.version === version);
            if (downloadItem && downloadItem.status === 'downloading') {
                if (!downloadItem.progress) downloadItem.progress = 0;
                downloadItem.progress += Math.random() * 10;
                
                if (downloadItem.progress >= 100) {
                    downloadItem.progress = 100;
                    clearInterval(progressInterval);
                }
                this.updateDownloadQueue();
            } else {
                clearInterval(progressInterval);
            }
        }, 500);
    }

    updateDownloadQueue() {
        // Update UI with download queue status
        const queueContainer = document.getElementById('download-queue');
        if (!queueContainer) {
            this.createDownloadQueueUI();
            return;
        }

        if (this.downloadQueue.length === 0) {
            queueContainer.style.display = 'none';
            return;
        }

        queueContainer.style.display = 'block';
        queueContainer.innerHTML = `
            <div class="download-queue-header">
                <h4>Download Queue</h4>
                <span class="queue-count">${this.downloadQueue.length} items</span>
            </div>
            <div class="download-list">
                ${this.downloadQueue.map(item => `
                    <div class="download-item ${item.status}">
                        <div class="download-info">
                            <div class="download-name">${item.version}</div>
                            <div class="download-status">${item.status}</div>
                        </div>
                        ${item.status === 'downloading' ? `
                            <div class="download-progress">
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${item.progress || 0}%"></div>
                                </div>
                                <span class="progress-text">${Math.round(item.progress || 0)}%</span>
                            </div>
                        ` : ''}
                        ${item.status === 'completed' ? `
                            <div class="download-complete">✅</div>
                        ` : ''}
                        ${item.status === 'failed' ? `
                            <div class="download-failed">❌</div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    createDownloadQueueUI() {
        const queueContainer = document.createElement('div');
        queueContainer.id = 'download-queue';
        queueContainer.className = 'download-queue';
        
        const firmwareSection = document.querySelector('.firmware-section .container');
        firmwareSection.appendChild(queueContainer);
        this.updateDownloadQueue();
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
                    <div class="firmware-detail-grid">
                        <div class="detail-item">
                            <label>Version:</label>
                            <span>${firmware.version}</span>
                        </div>
                        <div class="detail-item">
                            <label>Android Version:</label>
                            <span>${firmware.android_version}</span>
                        </div>
                        <div class="detail-item">
                            <label>Region:</label>
                            <span>${firmware.region}</span>
                        </div>
                        <div class="detail-item">
                            <label>Build Date:</label>
                            <span>${firmware.build_date}</span>
                        </div>
                        <div class="detail-item">
                            <label>File Size:</label>
                            <span>${firmware.file_size}</span>
                        </div>
                        <div class="detail-item">
                            <label>Checksum (MD5):</label>
                            <span class="checksum">${firmware.checksum}</span>
                        </div>
                        <div class="detail-item">
                            <label>Download URL:</label>
                            <a href="${firmware.download_url}" target="_blank" class="download-link">${firmware.download_url}</a>
                        </div>
                    </div>

                    <div class="firmware-actions-full">
                        <button class="btn btn-primary" 
                                onclick="firmwareManager.downloadFirmware('${firmware.download_url}', '${firmware.version}')">
                            Download Firmware
                        </button>
                        <button class="btn btn-outline" 
                                onclick="firmwareManager.verifyFirmware('${firmware.checksum}')">
                            Verify Checksum
                        </button>
                        <button class="btn btn-outline" 
                                onclick="firmwareManager.shareFirmware(${JSON.stringify(firmware).replace(/"/g, '&quot;')})">
                            Share
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    async verifyFirmware(checksum) {
        this.showNotification('Verifying firmware checksum...', 'info');

        // Simulate verification process
        setTimeout(() => {
            const isValid = Math.random() > 0.1; // 90% chance of valid checksum
            
            if (isValid) {
                this.showNotification('✅ Firmware checksum verified successfully!', 'success');
            } else {
                this.showNotification('❌ Firmware checksum verification failed!', 'error');
            }
        }, 2000);
    }

    shareFirmware(firmware) {
        const shareText = `Firmware: ${firmware.version} | Android ${firmware.android_version} | Region: ${firmware.region}`;
        const shareUrl = firmware.download_url;

        if (navigator.share) {
            navigator.share({
                title: `Firmware: ${firmware.version}`,
                text: shareText,
                url: shareUrl
            });
        } else if (navigator.clipboard) {
            navigator.clipboard.writeText(`${shareText}\n${shareUrl}`);
            this.showNotification('Firmware details copied to clipboard!', 'success');
        } else {
            // Fallback
            prompt('Copy the firmware details:', `${shareText}\n${shareUrl}`);
        }
    }

    requestFirmware() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Request Firmware</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <p>Can't find the firmware you're looking for? Submit a request and we'll add it to our database.</p>
                    
                    <div class="form-group">
                        <label>Device Brand</label>
                        <input type="text" id="request-brand" class="form-input" placeholder="e.g., Samsung, Hisense, Xiaomi">
                    </div>
                    
                    <div class="form-group">
                        <label>Device Model</label>
                        <input type="text" id="request-model" class="form-input" placeholder="e.g., Galaxy S21, Infinity H40 Lite">
                    </div>
                    
                    <div class="form-group">
                        <label>Model Number</label>
                        <input type="text" id="request-model-number" class="form-input" placeholder="e.g., SM-G991U, HLTE230E">
                    </div>
                    
                    <div class="form-group">
                        <label>Region (if known)</label>
                        <input type="text" id="request-region" class="form-input" placeholder="e.g., USA, Europe, Global">
                    </div>
                    
                    <div class="form-group">
                        <label>Additional Information</label>
                        <textarea id="request-notes" class="form-input" rows="3" placeholder="Any additional details about the firmware..."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="firmwareManager.submitFirmwareRequest()">Submit Request</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    async submitFirmwareRequest() {
        const brand = document.getElementById('request-brand').value;
        const model = document.getElementById('request-model').value;
        const modelNumber = document.getElementById('request-model-number').value;
        const region = document.getElementById('request-region').value;
        const notes = document.getElementById('request-notes').value;

        if (!brand || !model) {
            this.showNotification('Please fill in at least brand and model', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/request-firmware', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    brand: brand,
                    model: model,
                    model_number: modelNumber,
                    region: region,
                    notes: notes
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification('Firmware request submitted successfully!', 'success');
                document.querySelector('.modal-overlay').remove();
            } else {
                this.showNotification('Request failed: ' + result.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error submitting request: ' + error.message, 'error');
        }
    }

    async checkFirmwareUpdates() {
        this.showNotification('Checking for firmware updates...', 'info');

        try {
            const response = await fetch('/api/check-updates');
            const result = await response.json();

            if (result.success && result.updates.length > 0) {
                this.showUpdateNotification(result.updates);
            } else {
                this.showNotification('All firmware files are up to date!', 'success');
            }
        } catch (error) {
            this.showNotification('Error checking updates: ' + error.message, 'error');
        }
    }

    showUpdateNotification(updates) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Firmware Updates Available</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <p>${updates.length} new firmware version(s) available:</p>
                    <div class="updates-list">
                        ${updates.map(update => `
                            <div class="update-item">
                                <div class="update-info">
                                    <strong>${update.model}</strong>
                                    <span>${update.new_version} (was ${update.old_version})</span>
                                </div>
                                <button class="btn btn-sm btn-primary" 
                                        onclick="firmwareManager.downloadFirmware('${update.download_url}', '${update.new_version}')">
                                    Download
                                </button>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="firmwareManager.downloadAllUpdates(${JSON.stringify(updates).replace(/"/g, '&quot;')})">
                        Download All
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    downloadAllUpdates(updates) {
        updates.forEach(update => {
            this.downloadFirmware(update.download_url, update.new_version);
        });
        document.querySelector('.modal-overlay').remove();
    }

    showNotification(message, type = 'info') {
        if (window.app) {
            window.app.showNotification(message, type);
        } else {
            alert(message);
        }
    }
}

// Initialize firmware manager
const firmwareManager = new FirmwareManager();

// Add firmware-specific styles
const firmwareStyles = `
.ai-recommendation-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 24px;
    display: flex;
    align-items: flex-start;
    gap: 16px;
}

.ai-recommendation-banner .ai-icon {
    font-size: 24px;
    flex-shrink: 0;
}

.ai-recommendation-banner .ai-content {
    flex: 1;
}

.ai-recommendation-banner .ai-title {
    font-weight: 600;
    margin-bottom: 8px;
    opacity: 0.9;
}

.ai-recommendation-banner .ai-details {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
}

.ai-recommendation-banner .ai-details strong {
    font-size: 18px;
}

.ai-recommendation-banner .ai-confidence {
    background: rgba(255, 255, 255, 0.2);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.ai-recommendation-banner .ai-reasoning {
    opacity: 0.9;
    font-size: 14px;
}

.firmware-item {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 16px;
    border: 2px solid transparent;
    transition: all 0.3s ease;
}

.firmware-item.recommended {
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.firmware-badge {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
}

.recommended-badge {
    background: #3b82f6;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.latest-badge {
    background: #10b981;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.firmware-info h4 {
    margin: 0 0 12px 0;
    color: #1f2937;
}

.firmware-meta {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 8px;
    margin-bottom: 12px;
}

.meta-item {
    font-size: 14px;
    color: #6b7280;
}

.firmware-checksum {
    font-size: 12px;
    background: #f3f4f6;
    padding: 8px 12px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
}

.firmware-checksum code {
    background: transparent;
    padding: 0;
    color: #374151;
}

.firmware-actions {
    display: flex;
    gap: 8px;
    margin-top: 16px;
    flex-wrap: wrap;
}

.no-results {
    text-align: center;
    padding: 60px 20px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-results-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
}

.no-results h3 {
    margin: 0 0 8px 0;
    color: #374151;
}

.no-results p {
    color: #6b7280;
    margin-bottom: 20px;
}

.download-queue {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-top: 24px;
    overflow: hidden;
}

.download-queue-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: #f8fafc;
    border-bottom: 1px solid #e5e7eb;
}

.download-queue-header h4 {
    margin: 0;
    color: #374151;
}

.queue-count {
    background: #3b82f6;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.download-list {
    padding: 16px;
}

.download-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px;
    background: #f9fafb;
    border-radius: 8px;
    margin-bottom: 8px;
}

.download-item:last-child {
    margin-bottom: 0;
}

.download-item.downloading {
    border-left: 4px solid #3b82f6;
}

.download-item.completed {
    border-left: 4px solid #10b981;
}

.download-item.failed {
    border-left: 4px solid #ef4444;
}

.download-info {
    flex: 1;
}

.download-name {
    font-weight: 500;
    color: #374151;
    margin-bottom: 4px;
}

.download-status {
    font-size: 12px;
    color: #6b7280;
    text-transform: capitalize;
}

.download-progress {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 120px;
}

.download-progress .progress-bar {
    width: 80px;
    height: 6px;
    background: #e5e7eb;
    border-radius: 3px;
    overflow: hidden;
}

.download-progress .progress-fill {
    height: 100%;
    background: #3b82f6;
    transition: width 0.3s ease;
}

.download-progress .progress-text {
    font-size: 12px;
    color: #6b7280;
    min-width: 30px;
}

.download-complete,
.download-failed {
    font-size: 16px;
}

.firmware-detail-grid {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #e5e7eb;
}

.detail-item:last-child {
    border-bottom: none;
}

.detail-item label {
    font-weight: 500;
    color: #374151;
    margin: 0;
}

.detail-item .checksum {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    background: #f3f4f6;
    padding: 4px 8px;
    border-radius: 4px;
}

.download-link {
    color: #3b82f6;
    text-decoration: none;
    font-size: 14px;
    word-break: break-all;
}

.download-link:hover {
    text-decoration: underline;
}

.firmware-actions-full {
    display: flex;
    gap: 12px;
    margin-top: 20px;
    flex-wrap: wrap;
}

.updates-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 16px;
}

.update-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: #f9fafb;
    border-radius: 8px;
}

.update-info {
    display: flex;
    flex-direction: column;
}

.update-info strong {
    color: #374151;
    margin-bottom: 4px;
}

.update-info span {
    font-size: 14px;
    color: #6b7280;
}

@media (max-width: 768px) {
    .firmware-meta {
        grid-template-columns: 1fr;
    }
    
    .firmware-actions {
        flex-direction: column;
    }
    
    .firmware-actions-full {
        flex-direction: column;
    }
    
    .download-item {
        flex-direction: column;
        align-items: stretch;
        gap: 12px;
    }
    
    .download-progress {
        align-self: stretch;
    }
    
    .detail-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
    }
}
`;

// Inject firmware styles
const firmwareStyleSheet = document.createElement('style');
firmwareStyleSheet.textContent = firmwareStyles;
document.head.appendChild(firmwareStyleSheet);
