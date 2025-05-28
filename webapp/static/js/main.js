/**
 * Bili2Text Web 主要JavaScript文件
 * 包含通用功能、通知系统、设置管理等
 */

// 全局配置
const CONFIG = {
    API_BASE_URL: '/api',
    WS_BASE_URL: `ws://${window.location.host}/ws`,
    NOTIFICATION_TIMEOUT: 5000,
    AUTO_REFRESH_INTERVAL: 5000,
    MAX_RETRY_ATTEMPTS: 3
};

// 应用状态
const AppState = {
    currentTask: null,
    settings: {
        defaultModel: 'medium',
        autoRefresh: true,
        keepAudio: true,
        browserNotifications: false
    },
    isOnline: navigator.onLine
};

/**
 * 通知系统
 */
class NotificationManager {
    constructor() {
        this.container = document.getElementById('notificationContainer');
        this.requestPermission();
    }

    // 请求浏览器通知权限
    async requestPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            await Notification.requestPermission();
        }
    }

    // 显示通知
    show(message, type = 'info', options = {}) {
        // 页面内通知
        this.showInPage(message, type, options);
        
        // 浏览器通知
        if (AppState.settings.browserNotifications && 'Notification' in window && Notification.permission === 'granted') {
            this.showBrowserNotification(message, type);
        }
    }

    // 页面内通知
    showInPage(message, type, options) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification`;
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${this.getIcon(type)} me-2"></i>
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        this.container.appendChild(notification);

        // 自动移除
        if (!options.persistent) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, options.timeout || CONFIG.NOTIFICATION_TIMEOUT);
        }
    }

    // 浏览器通知
    showBrowserNotification(message, type) {
        const notification = new Notification('Bili2Text Web', {
            body: message,
            icon: '/static/images/icon.png',
            tag: 'bili2text-notification'
        });

        setTimeout(() => notification.close(), CONFIG.NOTIFICATION_TIMEOUT);
    }

    // 获取图标
    getIcon(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'danger': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    // 清除所有通知
    clear() {
        this.container.innerHTML = '';
    }
}

/**
 * API客户端
 */
class ApiClient {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
        this.retryAttempts = 0;
        this.maxRetryAttempts = 3;
        this.retryDelay = 1000;
    }

    // 通用请求方法
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            timeout: options.timeout || 30000,
            ...options
        };

        try {
            // 创建带超时的fetch请求
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), config.timeout);
            
            const response = await fetch(url, {
                ...config,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            // 处理HTTP错误状态
            if (!response.ok) {
                const errorData = await this.parseErrorResponse(response);
                throw {
                    response: {
                        status: response.status,
                        statusText: response.statusText,
                        data: errorData
                    }
                };
            }

            const data = await response.json();
            this.retryAttempts = 0; // 重置重试次数
            return data;
            
        } catch (error) {
            // 处理不同类型的错误
            const processedError = this.processError(error, endpoint, options);
            
            // 重试逻辑
            if (this.shouldRetry(processedError) && this.retryAttempts < this.maxRetryAttempts) {
                this.retryAttempts++;
                await this.delay(this.retryDelay * this.retryAttempts);
                return this.request(endpoint, options);
            }
            
            // 使用错误处理器处理错误
            if (window.errorHandler && !options.silent) {
                window.errorHandler.handleError(processedError, 'api_request', {
                    retryCallback: options.retryCallback,
                    showDetails: options.showErrorDetails !== false
                });
            }
            
            throw processedError;
        }
    }

    // 解析错误响应
    async parseErrorResponse(response) {
        try {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                const text = await response.text();
                return {
                    error: {
                        code: `HTTP_${response.status}`,
                        message: text || response.statusText
                    }
                };
            }
        } catch (e) {
            return {
                error: {
                    code: `HTTP_${response.status}`,
                    message: response.statusText
                }
            };
        }
    }

    // 处理错误
    processError(error, endpoint, options) {
        let processedError = {
            code: 'UNKNOWN_ERROR',
            message: '请求失败',
            endpoint: endpoint,
            options: options
        };

        if (error.name === 'AbortError') {
            processedError.code = 'TIMEOUT_ERROR';
            processedError.message = '请求超时';
        } else if (error.message && error.message.includes('Failed to fetch')) {
            processedError.code = 'NETWORK_ERROR';
            processedError.message = '网络连接失败';
        } else if (error.response) {
            // HTTP错误响应
            const response = error.response;
            processedError = {
                ...processedError,
                ...error,
                code: response.data?.error?.code || `HTTP_${response.status}`,
                message: response.data?.error?.message || response.statusText,
                details: response.data?.error?.details,
                status: response.status
            };
        } else if (error.code) {
            // 已处理的错误
            processedError = { ...processedError, ...error };
        } else {
            // 其他错误
            processedError.message = error.message || '未知错误';
            processedError.stack = error.stack;
        }

        return processedError;
    }

    // 判断是否应该重试
    shouldRetry(error) {
        const retryableCodes = [
            'NETWORK_ERROR',
            'TIMEOUT_ERROR',
            'HTTP_500',
            'HTTP_502',
            'HTTP_503',
            'HTTP_504'
        ];
        
        return retryableCodes.includes(error.code) || 
               (error.status >= 500 && error.status < 600);
    }

    // 延迟函数
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // GET请求
    async get(endpoint, params = {}, options = {}) {
        const url = new URL(`${this.baseURL}${endpoint}`, window.location.origin);
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.append(key, params[key]);
            }
        });
        
        return this.request(url.pathname + url.search, {
            method: 'GET',
            ...options
        });
    }

    // POST请求
    async post(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options
        });
    }

    // PUT请求
    async put(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
            ...options
        });
    }

    // DELETE请求
    async delete(endpoint, options = {}) {
        return this.request(endpoint, {
            method: 'DELETE',
            ...options
        });
    }

    // 文件上传
    async upload(endpoint, formData, options = {}) {
        const config = {
            method: 'POST',
            body: formData,
            ...options
        };
        
        // 移除Content-Type，让浏览器自动设置
        delete config.headers;
        
        return this.request(endpoint, config);
    }

    // 带进度的请求
    async requestWithProgress(endpoint, options = {}, onProgress = null) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            // 设置进度回调
            if (onProgress && xhr.upload) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const progress = (e.loaded / e.total) * 100;
                        onProgress(progress);
                    }
                });
            }
            
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const data = JSON.parse(xhr.responseText);
                        resolve(data);
                    } catch (e) {
                        resolve(xhr.responseText);
                    }
                } else {
                    const error = {
                        response: {
                            status: xhr.status,
                            statusText: xhr.statusText,
                            data: xhr.responseText
                        }
                    };
                    reject(this.processError(error, endpoint, options));
                }
            });
            
            xhr.addEventListener('error', () => {
                reject(this.processError(new Error('Network error'), endpoint, options));
            });
            
            xhr.addEventListener('timeout', () => {
                reject(this.processError(new Error('Request timeout'), endpoint, options));
            });
            
            const url = `${this.baseURL}${endpoint}`;
            xhr.open(options.method || 'GET', url);
            
            // 设置请求头
            if (options.headers) {
                Object.keys(options.headers).forEach(key => {
                    xhr.setRequestHeader(key, options.headers[key]);
                });
            }
            
            // 设置超时
            xhr.timeout = options.timeout || 30000;
            
            xhr.send(options.body);
        });
    }

    // 健康检查
    async healthCheck() {
        try {
            const response = await this.get('/system/status', {}, { 
                silent: true,
                timeout: 5000 
            });
            return response.success;
        } catch (error) {
            return false;
        }
    }

    // 重置重试计数器
    resetRetryCount() {
        this.retryAttempts = 0;
    }
}

/**
 * 设置管理器
 */
class SettingsManager {
    constructor() {
        this.loadSettings();
        this.bindEvents();
    }

    // 加载设置
    loadSettings() {
        const saved = localStorage.getItem('bili2text-settings');
        if (saved) {
            AppState.settings = { ...AppState.settings, ...JSON.parse(saved) };
        }
        this.applySettings();
    }

    // 保存设置
    saveSettings() {
        localStorage.setItem('bili2text-settings', JSON.stringify(AppState.settings));
        this.applySettings();
        notificationManager.show('设置已保存', 'success');
    }

    // 应用设置
    applySettings() {
        // 更新表单元素
        const elements = {
            'defaultModel': document.getElementById('defaultModel'),
            'autoRefresh': document.getElementById('autoRefresh'),
            'keepAudio': document.getElementById('keepAudio'),
            'browserNotifications': document.getElementById('browserNotifications')
        };

        Object.keys(elements).forEach(key => {
            const element = elements[key];
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = AppState.settings[key];
                } else {
                    element.value = AppState.settings[key];
                }
            }
        });
    }

    // 绑定事件
    bindEvents() {
        const saveButton = document.getElementById('saveSettings');
        if (saveButton) {
            saveButton.addEventListener('click', () => {
                this.updateSettings();
                this.saveSettings();
                
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
                if (modal) {
                    modal.hide();
                }
            });
        }
    }

    // 更新设置
    updateSettings() {
        const elements = {
            'defaultModel': document.getElementById('defaultModel'),
            'autoRefresh': document.getElementById('autoRefresh'),
            'keepAudio': document.getElementById('keepAudio'),
            'browserNotifications': document.getElementById('browserNotifications')
        };

        Object.keys(elements).forEach(key => {
            const element = elements[key];
            if (element) {
                if (element.type === 'checkbox') {
                    AppState.settings[key] = element.checked;
                } else {
                    AppState.settings[key] = element.value;
                }
            }
        });
    }
}

/**
 * 工具函数
 */
const Utils = {
    // 格式化文件大小
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // 格式化时长
    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);

        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        }
    },

    // 格式化相对时间
    formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;

        const minute = 60 * 1000;
        const hour = 60 * minute;
        const day = 24 * hour;

        if (diff < minute) {
            return '刚刚';
        } else if (diff < hour) {
            return `${Math.floor(diff / minute)}分钟前`;
        } else if (diff < day) {
            return `${Math.floor(diff / hour)}小时前`;
        } else if (diff < 7 * day) {
            return `${Math.floor(diff / day)}天前`;
        } else {
            return date.toLocaleDateString('zh-CN');
        }
    },

    // 验证URL
    validateBilibiliUrl(url) {
        const patterns = [
            /^https?:\/\/www\.bilibili\.com\/video\/BV[\w]+/,
            /^https?:\/\/b23\.tv\/[\w]+/,
            /^BV[\w]+$/
        ];
        return patterns.some(pattern => pattern.test(url));
    },

    // 复制到剪贴板
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            notificationManager.show('已复制到剪贴板', 'success');
        } catch (error) {
            console.error('复制失败:', error);
            notificationManager.show('复制失败', 'danger');
        }
    },

    // 下载文件
    downloadFile(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    },

    // 防抖函数
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // 节流函数
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

/**
 * 网络状态监控
 */
class NetworkMonitor {
    constructor() {
        this.bindEvents();
    }

    bindEvents() {
        window.addEventListener('online', () => {
            AppState.isOnline = true;
            notificationManager.show('网络连接已恢复', 'success');
        });

        window.addEventListener('offline', () => {
            AppState.isOnline = false;
            notificationManager.show('网络连接已断开', 'warning', { persistent: true });
        });
    }
}

// 全局实例
let notificationManager;
let apiClient;
let settingsManager;
let networkMonitor;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化全局组件
    notificationManager = new NotificationManager();
    apiClient = new ApiClient();
    settingsManager = new SettingsManager();
    networkMonitor = new NetworkMonitor();

    // 绑定全局事件
    bindGlobalEvents();

    // 初始化工具提示
    initializeTooltips();

    console.log('Bili2Text Web 应用已初始化');
});

// 绑定全局事件
function bindGlobalEvents() {
    // 粘贴按钮事件
    const pasteBtn = document.getElementById('pasteBtn');
    if (pasteBtn) {
        pasteBtn.addEventListener('click', async () => {
            try {
                const text = await navigator.clipboard.readText();
                const urlInput = document.getElementById('videoUrl');
                if (urlInput) {
                    urlInput.value = text;
                    urlInput.focus();
                }
            } catch (error) {
                notificationManager.show('无法读取剪贴板内容', 'warning');
            }
        });
    }

    // 清空表单按钮
    const clearBtn = document.getElementById('clearForm');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            const form = document.getElementById('transcriptionForm');
            if (form) {
                form.reset();
                // 重新设置默认值
                const mediumRadio = document.getElementById('model-medium');
                if (mediumRadio) {
                    mediumRadio.checked = true;
                }
                const keepAudioCheckbox = document.getElementById('keepAudio');
                if (keepAudioCheckbox) {
                    keepAudioCheckbox.checked = true;
                }
            }
        });
    }

    // 键盘快捷键
    document.addEventListener('keydown', (e) => {
        // Ctrl+Enter 或 Cmd+Enter 提交表单
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const submitBtn = document.getElementById('startTranscription');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.click();
            }
        }
        
        // Esc 关闭模态框
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });

    // 表单验证
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// 初始化工具提示
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 导出全局对象供其他脚本使用
window.Bili2Text = {
    CONFIG,
    AppState,
    NotificationManager,
    ApiClient,
    SettingsManager,
    Utils,
    notificationManager,
    apiClient,
    settingsManager
}; 