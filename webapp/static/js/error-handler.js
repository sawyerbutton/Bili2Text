/**
 * 错误处理器
 * 统一处理前端错误和用户反馈
 */

class ErrorHandler {
    constructor() {
        this.errorCodes = {
            // 网络错误
            'NETWORK_ERROR': '网络连接失败，请检查网络设置',
            'TIMEOUT_ERROR': '请求超时，请稍后重试',
            'CONNECTION_REFUSED': '无法连接到服务器',
            
            // 认证错误
            'UNAUTHORIZED': '未授权访问，请重新登录',
            'FORBIDDEN': '权限不足，无法执行此操作',
            'TOKEN_EXPIRED': '登录已过期，请重新登录',
            
            // 业务错误
            'INVALID_URL': '请输入有效的哔哩哔哩视频链接',
            'INVALID_MODEL': '选择的模型不支持',
            'TASK_NOT_FOUND': '任务不存在或已被删除',
            'FILE_NOT_FOUND': '文件不存在或已被删除',
            'SYSTEM_OVERLOAD': '系统负载过高，请稍后重试',
            
            // 文件错误
            'FILE_TOO_LARGE': '文件大小超出限制',
            'INVALID_FILE_TYPE': '不支持的文件类型',
            'UPLOAD_FAILED': '文件上传失败',
            
            // 系统错误
            'INTERNAL_ERROR': '服务器内部错误，请联系管理员',
            'DATABASE_ERROR': '数据库连接失败',
            'SERVICE_UNAVAILABLE': '服务暂时不可用',
            
            // 默认错误
            'UNKNOWN_ERROR': '发生未知错误，请稍后重试'
        };
        
        this.retryableErrors = [
            'NETWORK_ERROR',
            'TIMEOUT_ERROR',
            'CONNECTION_REFUSED',
            'SYSTEM_OVERLOAD',
            'SERVICE_UNAVAILABLE'
        ];
        
        this.initializeGlobalErrorHandlers();
    }

    /**
     * 初始化全局错误处理器
     */
    initializeGlobalErrorHandlers() {
        // 捕获未处理的Promise错误
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.handleError(event.reason, 'promise_rejection');
            event.preventDefault();
        });

        // 捕获JavaScript运行时错误
        window.addEventListener('error', (event) => {
            console.error('JavaScript error:', event.error);
            this.handleError(event.error, 'javascript_error');
        });

        // 捕获资源加载错误
        window.addEventListener('error', (event) => {
            if (event.target !== window) {
                console.error('Resource loading error:', event.target.src || event.target.href);
                this.showNotification('资源加载失败', 'warning');
            }
        }, true);
    }

    /**
     * 处理错误
     * @param {Error|Object|String} error - 错误对象
     * @param {String} context - 错误上下文
     * @param {Object} options - 处理选项
     */
    handleError(error, context = 'unknown', options = {}) {
        const errorInfo = this.parseError(error);
        
        // 记录错误日志
        this.logError(errorInfo, context);
        
        // 显示用户友好的错误信息
        if (!options.silent) {
            this.showErrorToUser(errorInfo, options);
        }
        
        // 如果是可重试的错误，提供重试选项
        if (this.isRetryableError(errorInfo.code) && options.retryCallback) {
            this.showRetryOption(errorInfo, options.retryCallback);
        }
        
        return errorInfo;
    }

    /**
     * 解析错误对象
     * @param {Error|Object|String} error - 错误
     * @returns {Object} 标准化的错误信息
     */
    parseError(error) {
        let errorInfo = {
            code: 'UNKNOWN_ERROR',
            message: '发生未知错误',
            details: null,
            timestamp: new Date().toISOString(),
            stack: null
        };

        if (typeof error === 'string') {
            errorInfo.message = error;
        } else if (error instanceof Error) {
            errorInfo.message = error.message;
            errorInfo.stack = error.stack;
            
            // 网络错误检测
            if (error.name === 'NetworkError' || error.message.includes('fetch')) {
                errorInfo.code = 'NETWORK_ERROR';
            } else if (error.name === 'TimeoutError') {
                errorInfo.code = 'TIMEOUT_ERROR';
            }
        } else if (error && typeof error === 'object') {
            // API错误响应
            if (error.response) {
                const response = error.response;
                errorInfo.code = response.data?.error?.code || `HTTP_${response.status}`;
                errorInfo.message = response.data?.error?.message || response.statusText;
                errorInfo.details = response.data?.error?.details;
            } else if (error.error) {
                errorInfo.code = error.error.code || 'API_ERROR';
                errorInfo.message = error.error.message || '接口调用失败';
                errorInfo.details = error.error.details;
            } else {
                errorInfo.code = error.code || 'UNKNOWN_ERROR';
                errorInfo.message = error.message || '发生未知错误';
                errorInfo.details = error.details;
            }
        }

        // 使用预定义的用户友好消息
        if (this.errorCodes[errorInfo.code]) {
            errorInfo.userMessage = this.errorCodes[errorInfo.code];
        } else {
            errorInfo.userMessage = errorInfo.message;
        }

        return errorInfo;
    }

    /**
     * 记录错误日志
     * @param {Object} errorInfo - 错误信息
     * @param {String} context - 错误上下文
     */
    logError(errorInfo, context) {
        const logEntry = {
            timestamp: errorInfo.timestamp,
            context: context,
            code: errorInfo.code,
            message: errorInfo.message,
            userAgent: navigator.userAgent,
            url: window.location.href,
            stack: errorInfo.stack,
            details: errorInfo.details
        };

        // 发送到控制台
        console.error('Error logged:', logEntry);

        // 发送到服务器（可选）
        if (window.apiClient) {
            window.apiClient.post('/api/logs/error', logEntry).catch(() => {
                // 忽略日志发送失败
            });
        }

        // 存储到本地存储（用于离线分析）
        this.storeErrorLocally(logEntry);
    }

    /**
     * 本地存储错误日志
     * @param {Object} logEntry - 日志条目
     */
    storeErrorLocally(logEntry) {
        try {
            const errors = JSON.parse(localStorage.getItem('error_logs') || '[]');
            errors.push(logEntry);
            
            // 只保留最近100条错误
            if (errors.length > 100) {
                errors.splice(0, errors.length - 100);
            }
            
            localStorage.setItem('error_logs', JSON.stringify(errors));
        } catch (e) {
            console.warn('Failed to store error log locally:', e);
        }
    }

    /**
     * 向用户显示错误信息
     * @param {Object} errorInfo - 错误信息
     * @param {Object} options - 显示选项
     */
    showErrorToUser(errorInfo, options = {}) {
        const severity = this.getErrorSeverity(errorInfo.code);
        
        if (options.modal) {
            this.showErrorModal(errorInfo);
        } else {
            this.showNotification(errorInfo.userMessage, severity, {
                duration: options.duration || (severity === 'error' ? 8000 : 5000),
                showDetails: options.showDetails !== false
            });
        }
    }

    /**
     * 显示错误模态框
     * @param {Object} errorInfo - 错误信息
     */
    showErrorModal(errorInfo) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'errorModal';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            错误详情
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-danger">
                            <strong>错误代码:</strong> ${errorInfo.code}
                        </div>
                        <p><strong>错误描述:</strong></p>
                        <p>${errorInfo.userMessage}</p>
                        
                        ${errorInfo.details ? `
                            <div class="mt-3">
                                <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#errorDetails">
                                    显示技术详情
                                </button>
                                <div class="collapse mt-2" id="errorDetails">
                                    <div class="card card-body bg-light">
                                        <small class="text-muted">
                                            <strong>详细信息:</strong><br>
                                            ${JSON.stringify(errorInfo.details, null, 2)}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        ` : ''}
                        
                        <div class="mt-3">
                            <small class="text-muted">
                                <strong>时间:</strong> ${new Date(errorInfo.timestamp).toLocaleString()}<br>
                                <strong>错误ID:</strong> ${errorInfo.timestamp}
                            </small>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        <button type="button" class="btn btn-primary" onclick="window.errorHandler.reportError('${errorInfo.timestamp}')">
                            <i class="fas fa-bug me-1"></i>报告问题
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // 模态框关闭后移除DOM元素
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    /**
     * 显示通知
     * @param {String} message - 消息内容
     * @param {String} type - 消息类型
     * @param {Object} options - 选项
     */
    showNotification(message, type = 'info', options = {}) {
        if (window.notificationManager) {
            window.notificationManager.show(message, type, options);
        } else {
            // 降级到alert
            alert(`${type.toUpperCase()}: ${message}`);
        }
    }

    /**
     * 显示重试选项
     * @param {Object} errorInfo - 错误信息
     * @param {Function} retryCallback - 重试回调
     */
    showRetryOption(errorInfo, retryCallback) {
        const retryNotification = document.createElement('div');
        retryNotification.className = 'alert alert-warning alert-dismissible fade show position-fixed';
        retryNotification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        retryNotification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <div class="flex-grow-1">
                    <strong>操作失败</strong><br>
                    <small>${errorInfo.userMessage}</small>
                </div>
                <button type="button" class="btn btn-sm btn-warning ms-2" onclick="this.parentElement.parentElement.retryCallback()">
                    <i class="fas fa-redo me-1"></i>重试
                </button>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        retryNotification.retryCallback = retryCallback;
        document.body.appendChild(retryNotification);

        // 10秒后自动移除
        setTimeout(() => {
            if (retryNotification.parentElement) {
                retryNotification.parentElement.removeChild(retryNotification);
            }
        }, 10000);
    }

    /**
     * 获取错误严重程度
     * @param {String} errorCode - 错误代码
     * @returns {String} 严重程度
     */
    getErrorSeverity(errorCode) {
        const criticalErrors = ['INTERNAL_ERROR', 'DATABASE_ERROR', 'SYSTEM_OVERLOAD'];
        const warningErrors = ['NETWORK_ERROR', 'TIMEOUT_ERROR', 'SERVICE_UNAVAILABLE'];
        
        if (criticalErrors.includes(errorCode)) {
            return 'error';
        } else if (warningErrors.includes(errorCode)) {
            return 'warning';
        } else {
            return 'info';
        }
    }

    /**
     * 检查是否为可重试错误
     * @param {String} errorCode - 错误代码
     * @returns {Boolean} 是否可重试
     */
    isRetryableError(errorCode) {
        return this.retryableErrors.includes(errorCode);
    }

    /**
     * 报告错误
     * @param {String} errorId - 错误ID
     */
    reportError(errorId) {
        const errors = JSON.parse(localStorage.getItem('error_logs') || '[]');
        const error = errors.find(e => e.timestamp === errorId);
        
        if (error && window.apiClient) {
            window.apiClient.post('/api/errors/report', {
                errorId: errorId,
                error: error,
                userFeedback: prompt('请描述您遇到的问题（可选）:') || ''
            }).then(() => {
                this.showNotification('问题报告已提交，感谢您的反馈！', 'success');
            }).catch(() => {
                this.showNotification('问题报告提交失败，请稍后重试', 'error');
            });
        }
    }

    /**
     * 获取本地错误日志
     * @returns {Array} 错误日志列表
     */
    getLocalErrorLogs() {
        try {
            return JSON.parse(localStorage.getItem('error_logs') || '[]');
        } catch (e) {
            return [];
        }
    }

    /**
     * 清除本地错误日志
     */
    clearLocalErrorLogs() {
        localStorage.removeItem('error_logs');
    }

    /**
     * 创建错误边界组件
     * @param {Function} component - 组件函数
     * @returns {Function} 包装后的组件
     */
    createErrorBoundary(component) {
        return function errorBoundaryWrapper(...args) {
            try {
                return component.apply(this, args);
            } catch (error) {
                window.errorHandler.handleError(error, 'component_error');
                return null;
            }
        };
    }
}

// 创建全局错误处理器实例
window.errorHandler = new ErrorHandler();

// 导出错误处理器
window.ErrorHandler = ErrorHandler; 