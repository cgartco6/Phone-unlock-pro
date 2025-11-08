// Hisense-specific functionality
class HisenseUnlockInterface {
    constructor() {
        this.supportedModels = ['HLTE230E', 'HLTE202E', 'HLTE300E'];
    }

    async detectHisenseDevice() {
        try {
            const response = await fetch('/api/detect-hisense', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
            return await response.json();
        } catch (error) {
            console.error('Hisense detection failed:', error);
            return {success: false, error: error.message};
        }
    }

    async unlockHisenseDevice(model, lockType, method = 'auto') {
        try {
            const response = await fetch('/api/unlock-hisense', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    model: model,
                    lock_type: lockType,
                    method: method
                })
            });
            return await response.json();
        } catch (error) {
            console.error('Hisense unlock failed:', error);
            return {success: false, error: error.message};
        }
    }

    getHisenseDeviceInfo(model) {
        const deviceInfo = {
            'HLTE230E': {
                name: 'Infinity H40 Lite',
                chipset: 'Unisoc SC9863A',
                android: '10',
                ram: '3GB',
                storage: '32GB',
                specialNotes: [
                    'Uses Unisoc chipset - requires special tools',
                    'FRP can be bypassed with combination files',
                    'No bootloader unlock available'
                ]
            }
        };
        return deviceInfo[model] || null;
    }

    displayHisenseUnlockMethods(model) {
        const methods = this.getHisenseUnlockMethods(model);
        const container = document.getElementById('hisense-methods-container');
        
        if (container && methods) {
            container.innerHTML = methods.map(method => `
                <div class="method-card hisense-method">
                    <h4>${method.name}</h4>
                    <p>Success Rate: ${(method.successRate * 100)}%</p>
                    <p>Data Loss: ${method.dataLoss}</p>
                    <button onclick="hisenseInterface.executeUnlockMethod('${model}', '${method.lockType}', '${method.name}')">
                        Use This Method
                    </button>
                </div>
            `).join('');
        }
    }

    getHisenseUnlockMethods(model) {
        const methods = {
            'HLTE230E': [
                {
                    name: 'Combination File FRP Bypass',
                    lockType: 'frp',
                    successRate: 0.85,
                    dataLoss: 'Complete',
                    tools: ['Hisense Tool v2.3', 'Octoplus Box']
                },
                {
                    name: 'Firmware Flash',
                    lockType: 'screen_lock', 
                    successRate: 0.95,
                    dataLoss: 'Complete',
                    tools: ['Hisense Tool v2.3', 'Odin']
                }
            ]
        };
        return methods[model] || [];
    }

    async executeUnlockMethod(model, lockType, methodName) {
        const result = await this.unlockHisenseDevice(model, lockType, methodName);
        
        if (result.success) {
            this.showSuccess(`Hisense ${model} unlocked successfully!`);
            this.displayUnlockLogs(result.logs);
        } else {
            this.showError(`Unlock failed: ${result.error}`);
        }
    }

    showSuccess(message) {
        // Implementation for success notification
        console.log('SUCCESS:', message);
    }

    showError(message) {
        // Implementation for error notification  
        console.error('ERROR:', message);
    }

    displayUnlockLogs(logs) {
        const logContainer = document.getElementById('unlock-logs');
        if (logContainer) {
            logContainer.innerHTML = logs.map(log => `<div class="log-entry">${log}</div>`).join('');
        }
    }
}

// Initialize Hisense interface
const hisenseInterface = new HisenseUnlockInterface();

// AI Activation Functions
async function activateAllAI() {
    try {
        showLoading('Activating all AI systems...');
        
        const response = await fetch('/api/activate-ai', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('All AI systems activated successfully!');
            updateAIAgentsStatus(result.agents);
        } else {
            showError('AI activation failed: ' + result.error);
        }
    } catch (error) {
        showError('AI activation error: ' + error.message);
    } finally {
        hideLoading();
    }
}

function updateAIAgentsStatus(agents) {
    const container = document.getElementById('ai-agents-status');
    if (container) {
        container.innerHTML = Object.entries(agents).map(([name, status]) => `
            <div class="ai-agent-status ${status}">
                <span class="agent-name">${name}</span>
                <span class="agent-status">${status}</span>
            </div>
        `).join('');
    }
}

// Self-healing monitoring
async function startSelfHealingMonitor() {
    try {
        const response = await fetch('/api/health-status');
        const health = await response.json();
        
        updateHealthDisplay(health);
        
        if (health.overall_health !== 'healthy') {
            showWarning('System health issues detected. Self-healing activated.');
        }
    } catch (error) {
        console.error('Health monitoring error:', error);
    }
}

function updateHealthDisplay(health) {
    const healthElement = document.getElementById('system-health');
    if (healthElement) {
        healthElement.className = `health-status ${health.overall_health}`;
        healthElement.innerHTML = `
            System Health: <strong>${health.overall_health.toUpperCase()}</strong>
            ${health.issues.length ? `<br><small>Issues: ${health.issues.join(', ')}</small>` : ''}
        `;
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Start health monitoring
    setInterval(startSelfHealingMonitor, 30000); // Every 30 seconds
    
    // Check for Hisense devices
    checkForHisenseDevices();
});

async function checkForHisenseDevices() {
    const detection = await hisenseInterface.detectHisenseDevice();
    if (detection.success && hisenseInterface.supportedModels.includes(detection.model)) {
        showHisenseUnlockInterface(detection.model);
    }
}

function showHisenseUnlockInterface(model) {
    // Show Hisense-specific unlock interface
    const hisenseSection = document.getElementById('hisense-unlock-section');
    if (hisenseSection) {
        hisenseSection.style.display = 'block';
        hisenseInterface.displayHisenseUnlockMethods(model);
    }
}
