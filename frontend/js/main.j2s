// PhoneUnlock Pro - Main JavaScript File
class PhoneUnlockApp {
    constructor() {
        this.currentDevice = null;
        this.aiAgents = {};
        this.systemHealth = 'healthy';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
        this.startHealthMonitoring();
        this.initializeAI();
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleNavigation(link.getAttribute('href'));
            });
        });

        // Main actions
        document.getElementById('start-unlocking-btn').addEventListener('click', () => {
            this.scrollToSection('detection');
        });

        document.getElementById('learn-more-btn').addEventListener('click', () => {
            this.scrollToSection('unlock');
        });

        // Mobile menu
        document.getElementById('mobile-menu-btn').addEventListener('click', () => {
            this.toggleMobileMenu();
        });

        // AI activation
        document.getElementById('activate-all-ai-btn').addEventListener('click', () => {
            this.activateAllAI();
        });

        document.getElementById('self-heal-btn').addEventListener('click', () => {
            this.runSelfHealing();
        });

        // Settings
        document.getElementById('settings-btn').addEventListener('click', () => {
            this.showSettings();
        });
    }

    handleNavigation(target) {
        const section = document.querySelector(target);
        if (section) {
            section.scrollIntoView({ behavior: 'smooth' });
            
            // Update active nav link
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            document.querySelector(`.nav-link[href="${target}"]`).classList.add('active');
        }
    }

    scrollToSection(sectionId) {
        this.handleNavigation(`#${sectionId}`);
    }

    toggleMobileMenu() {
        const nav = document.querySelector('.nav');
        const menuBtn = document.getElementById('mobile-menu-btn');
        
        nav.classList.toggle('mobile-open');
        menuBtn.classList.toggle('active');
    }

    async loadInitialData() {
        try {
            // Load recent devices
            await this.loadRecentDevices();
            
            // Load unlock methods
            await this.loadUnlockMethods();
            
            // Load tools
            await this.loadTools();
            
            // Update stats
            await this.updateStats();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async loadRecentDevices() {
        try {
            const response = await fetch('/api/recent-devices');
            const devices = await response.json();
            
            const container = document.getElementById('recent-devices-list');
            if (container && devices.success) {
                container.innerHTML = devices.data.map(device => `
                    <div class="recent-device">
                        <div class="device-model">${device.model}</div>
                        <div class="device-date">${new Date(device.detected_at).toLocaleDateString()}</div>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading recent devices:', error);
        }
    }

    async loadUnlockMethods() {
        try {
            const response = await fetch('/api/unlock-methods');
            const methods = await response.json();
            
            const container = document.getElementById('unlock-methods-grid');
            if (container && methods.success) {
                container.innerHTML = methods.data.map(method => `
                    <div class="method-card">
                        <div class="method-icon">${this.getMethodIcon(method.lock_type)}</div>
                        <h3>${this.formatLockType(method.lock_type)}</h3>
                        <p>${method.description}</p>
                        <div class="method-details">
                            <span class="success-rate">${(method.success_rate * 100)}% Success</span>
                            <span class="difficulty ${method.difficulty}">${method.difficulty}</span>
                        </div>
                        <button class="btn btn-primary btn-block" onclick="app.selectUnlockMethod('${method.lock_type}')">
                            Use This Method
                        </button>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading unlock methods:', error);
        }
    }

    async loadTools() {
        try {
            const response = await fetch('/api/tools');
            const tools = await response.json();
            
            const container = document.getElementById('tools-grid');
            if (container && tools.success) {
                container.innerHTML = tools.data.map(tool => `
                    <div class="tool-card">
                        <div class="tool-icon">${this.getToolIcon(tool.name)}</div>
                        <h3>${tool.name}</h3>
                        <p>${tool.description}</p>
                        <div class="tool-features">
                            ${tool.supported_brands.map(brand => `
                                <span class="tool-feature">${brand}</span>
                            `).join('')}
                        </div>
                        <div class="tool-status">
                            <span class="status-indicator ${tool.is_active ? 'success' : 'idle'}"></span>
                            ${tool.is_active ? 'Active' : 'Inactive'}
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading tools:', error);
        }
    }

    async updateStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            if (stats.success) {
                document.getElementById('devices-unlocked').textContent = 
                    stats.data.devices_unlocked.toLocaleString();
                document.getElementById('success-rate').textContent = 
                    stats.data.success_rate + '%';
                document.getElementById('supported-models').textContent = 
                    stats.data.supported_models.toLocaleString();
            }
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    getMethodIcon(lockType) {
        const icons = {
            'frp': '🔓',
            'kg_lock': '🔒',
            'bootloader': '⚙️',
            'screen_lock': '📱',
            'google_account': '👤',
            'icloud': '☁️'
        };
        return icons[lockType] || '🔑';
    }

    getToolIcon(toolName) {
        const icons = {
            'Octoplus': '🛠️',
            'Z3X': '🔧',
            'Odin': '⚡',
            'Cheetah Pro': '🐆'
        };
        return icons[toolName] || '🔨';
    }

    formatLockType(lockType) {
        const formats = {
            'frp': 'FRP Bypass',
            'kg_lock': 'KG Lock Removal',
            'bootloader': 'Bootloader Unlock',
            'screen_lock': 'Screen Lock Removal',
            'google_account': 'Google Account Remove',
            'icloud': 'iCloud Unlock'
        };
        return formats[lockType] || lockType;
    }

    async activateAllAI() {
        this.showLoading('Activating all AI systems...');
        
        try {
            const response = await fetch('/api/activate-ai', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('All AI systems activated successfully!');
                this.updateAIAgentsStatus(result.agents);
            } else {
                this.showError('Failed to activate AI systems: ' + result.error);
            }
        } catch (error) {
            this.showError('Error activating AI: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    async runSelfHealing() {
        this.showLoading('Running self-healing system...');
        
        try {
            const response = await fetch('/api/self-heal', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Self-healing completed successfully!');
                this.updateSystemHealth(result.health_status);
            } else {
                this.showError('Self-healing failed: ' + result.error);
            }
        } catch (error) {
            this.showError('Error running self-healing: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    updateAIAgentsStatus(agents) {
        const container = document.getElementById('ai-agents-status');
        const gridContainer = document.getElementById('ai-agents-grid');
        
        if (container) {
            container.innerHTML = Object.entries(agents).map(([name, status]) => `
                <div class="ai-agent">
                    <span class="agent-name">${this.formatAgentName(name)}</span>
                    <span class="agent-status ${status}">${status}</span>
                </div>
            `).join('');
        }

        if (gridContainer) {
            gridContainer.innerHTML = Object.entries(agents).map(([name, status]) => `
                <div class="ai-agent-card">
                    <div class="ai-agent-header">
                        <div class="ai-agent-icon">🤖</div>
                        <div class="ai-agent-name">${this.formatAgentName(name)}</div>
                        <span class="ai-agent-status ${status}">${status}</span>
                    </div>
                    <p class="ai-agent-description">
                        ${this.getAgentDescription(name)}
                    </p>
                    <div class="ai-agent-controls">
                        <button class="btn btn-sm ${status === 'active' ? 'btn-success' : 'btn-outline'}" 
                                onclick="app.toggleAgent('${name}')">
                            ${status === 'active' ? 'Active' : 'Activate'}
                        </button>
                        <button class="btn btn-sm btn-outline" onclick="app.showAgentDetails('${name}')">
                            Details
                        </button>
                    </div>
                </div>
            `).join('');
        }

        // Update AI metrics
        const activeCount = Object.values(agents).filter(status => status === 'active').length;
        document.getElementById('ai-active-agents').textContent = activeCount;
    }

    formatAgentName(agentName) {
        const names = {
            'phone_detection': 'Phone Detection AI',
            'unlock_recommender': 'Unlock Recommender',
            'risk_assessor': 'Risk Assessment',
            'strategy_generator': 'Strategy Generator',
            'self_healing': 'Self-Healing System'
        };
        return names[agentName] || agentName;
    }

    getAgentDescription(agentName) {
        const descriptions = {
            'phone_detection': 'Automatically detects connected phones using USB data and AI pattern recognition',
            'unlock_recommender': 'Recommends optimal unlock methods based on device and lock type analysis',
            'risk_assessor': 'Evaluates risks and provides mitigation strategies for unlock operations',
            'strategy_generator': 'Creates detailed step-by-step unlock plans with contingency options',
            'self_healing': 'Monitors system health and automatically repairs issues'
        };
        return descriptions[agentName] || 'AI agent for system operations';
    }

    async toggleAgent(agentName) {
        try {
            const response = await fetch(`/api/toggle-agent/${agentName}`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(`${this.formatAgentName(agentName)} ${result.status}`);
                this.updateAIAgentsStatus(result.all_agents);
            } else {
                this.showError(`Failed to toggle ${agentName}: ${result.error}`);
            }
        } catch (error) {
            this.showError('Error toggling agent: ' + error.message);
        }
    }

    showAgentDetails(agentName) {
        // Implementation for showing agent details modal
        this.showInfo(`${this.formatAgentName(agentName)} Details`, 
                     this.getAgentDescription(agentName));
    }

    async startHealthMonitoring() {
        // Initial health check
        await this.checkSystemHealth();
        
        // Periodic health checks every 30 seconds
        setInterval(() => {
            this.checkSystemHealth();
        }, 30000);
    }

    async checkSystemHealth() {
        try {
            const response = await fetch('/api/health-status');
            const health = await response.json();
            
            if (health.success) {
                this.updateSystemHealth(health.data);
            }
        } catch (error) {
            console.error('Error checking system health:', error);
            this.updateSystemHealth({ overall_health: 'unhealthy' });
        }
    }

    updateSystemHealth(health) {
        this.systemHealth = health.overall_health;
        
        const healthElement = document.getElementById('system-health');
        if (healthElement) {
            const indicator = healthElement.querySelector('.health-indicator');
            const text = healthElement.querySelector('.health-text') || healthElement;
            
            indicator.className = 'health-indicator ' + health.overall_health;
            
            let statusText = 'System Ready';
            if (health.overall_health === 'degraded') {
                statusText = 'System Degraded';
            } else if (health.overall_health === 'unhealthy') {
                statusText = 'System Issues';
            }
            
            if (text.classList.contains('health-text')) {
                text.textContent = statusText;
            } else {
                healthElement.innerHTML = `
                    <span class="health-indicator ${health.overall_health}"></span>
                    ${statusText}
                `;
            }
        }
    }

    selectUnlockMethod(lockType) {
        if (!this.currentDevice) {
            this.showWarning('Please detect a phone first before selecting unlock method.');
            this.scrollToSection('detection');
            return;
        }

        this.showLoading(`Preparing ${this.formatLockType(lockType)} method...`);
        
        // Implementation would continue with method-specific logic
        setTimeout(() => {
            this.hideLoading();
            this.showSuccess(`Ready to execute ${this.formatLockType(lockType)} on ${this.currentDevice.model}`);
        }, 2000);
    }

    showSettings() {
        // Implementation for settings modal
        this.showInfo('Settings', 'System configuration options will appear here.');
    }

    // UI Helper Methods
    showLoading(message = 'Processing...') {
        const overlay = document.getElementById('loading-overlay');
        const text = document.getElementById('loading-text');
        
        if (overlay && text) {
            text.textContent = message;
            overlay.style.display = 'flex';
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showWarning(message) {
        this.showNotification(message, 'warning');
    }

    showInfo(title, message) {
        this.showNotification(message, 'info', title);
    }

    showNotification(message, type = 'info', title = '') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }[type] || 'ℹ️';

        notification.innerHTML = `
            <div class="notification-icon">${icon}</div>
            <div class="notification-content">
                ${title ? `<div class="notification-title">${title}</div>` : ''}
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;

        // Add to page
        if (!document.querySelector('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        document.querySelector('.notification-container').appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    initializeAI() {
        // Initialize AI agents status
        this.aiAgents = {
            'phone_detection': 'active',
            'unlock_recommender': 'active',
            'risk_assessor': 'active',
            'strategy_generator': 'active',
            'self_healing': 'active'
        };
        
        this.updateAIAgentsStatus(this.aiAgents);
    }
}

// Initialize the application
const app = new PhoneUnlockApp();

// Global functions for HTML onclick handlers
function activateAllAI() {
    app.activateAllAI();
}

function runSelfHealing() {
    app.runSelfHealing();
}

// Add notification styles dynamically
const notificationStyles = `
.notification-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    max-width: 400px;
}

.notification {
    background: white;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border-left: 4px solid #3b82f6;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    animation: slideIn 0.3s ease-out;
}

.notification-success {
    border-left-color: #10b981;
}

.notification-error {
    border-left-color: #ef4444;
}

.notification-warning {
    border-left-color: #f59e0b;
}

.notification-info {
    border-left-color: #3b82f6;
}

.notification-icon {
    font-size: 16px;
    flex-shrink: 0;
}

.notification-content {
    flex: 1;
}

.notification-title {
    font-weight: 600;
    margin-bottom: 4px;
    color: #1f2937;
}

.notification-message {
    color: #6b7280;
    font-size: 14px;
}

.notification-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: #9ca3af;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.notification-close:hover {
    color: #6b7280;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
`;

// Inject notification styles
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);
