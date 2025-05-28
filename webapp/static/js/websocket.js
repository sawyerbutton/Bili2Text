/**
 * WebSocket 通信管理器
 * 用于实时任务状态更新和系统监控
 */

class WebSocketManager {
    constructor() {
        this.connections = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.heartbeatInterval = 30000; // 30秒心跳
        this.heartbeatTimer = null;
    }

    /**
     * 连接到任务WebSocket
     * @param {string} taskId - 任务ID
     * @param {function} onMessage - 消息处理回调
     * @param {function} onError - 错误处理回调
     */
    connectToTask(taskId, onMessage, onError) {
        const wsUrl = `${window.Bili2Text.CONFIG.WS_BASE_URL}/tasks/${taskId}`;
        return this.connect(`task_${taskId}`, wsUrl, onMessage, onError);
    }

    /**
     * 连接到系统WebSocket
     * @param {function} onMessage - 消息处理回调
     * @param {function} onError - 错误处理回调
     */
    connectToSystem(onMessage, onError) {
        const wsUrl = `${window.Bili2Text.CONFIG.WS_BASE_URL}/system`;
        return this.connect('system', wsUrl, onMessage, onError);
    }

    /**
     * 通用连接方法
     * @param {string} key - 连接标识
     * @param {string} url - WebSocket URL
     * @param {function} onMessage - 消息处理回调
     * @param {function} onError - 错误处理回调
     */
    connect(key, url, onMessage, onError) {
        // 如果已存在连接，先关闭
        if (this.connections.has(key)) {
            this.disconnect(key);
        }

        try {
            const ws = new WebSocket(url);
            const connection = {
                ws,
                url,
                onMessage,
                onError,
                isConnected: false,
                lastPing: Date.now()
            };

            // 连接打开
            ws.onopen = () => {
                console.log(`WebSocket连接已建立: ${key}`);
                connection.isConnected = true;
                this.reconnectAttempts = 0;
                this.startHeartbeat(key);
                
                // 发送连接确认
                this.send(key, { type: 'ping' });
            };

            // 接收消息
            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    
                    // 处理心跳响应
                    if (data.type === 'pong') {
                        connection.lastPing = Date.now();
                        return;
                    }

                    // 调用消息处理回调
                    if (onMessage) {
                        onMessage(data);
                    }
                } catch (error) {
                    console.error('WebSocket消息解析失败:', error);
                }
            };

            // 连接关闭
            ws.onclose = (event) => {
                console.log(`WebSocket连接已关闭: ${key}`, event.code, event.reason);
                connection.isConnected = false;
                this.stopHeartbeat();
                
                // 如果不是主动关闭，尝试重连
                if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.scheduleReconnect(key, url, onMessage, onError);
                }
            };

            // 连接错误
            ws.onerror = (error) => {
                console.error(`WebSocket连接错误: ${key}`, error);
                connection.isConnected = false;
                
                if (onError) {
                    onError(error);
                }
            };

            this.connections.set(key, connection);
            return connection;

        } catch (error) {
            console.error('WebSocket连接创建失败:', error);
            if (onError) {
                onError(error);
            }
            return null;
        }
    }

    /**
     * 发送消息
     * @param {string} key - 连接标识
     * @param {object} data - 要发送的数据
     */
    send(key, data) {
        const connection = this.connections.get(key);
        if (connection && connection.isConnected && connection.ws.readyState === WebSocket.OPEN) {
            try {
                connection.ws.send(JSON.stringify(data));
                return true;
            } catch (error) {
                console.error('WebSocket发送消息失败:', error);
                return false;
            }
        }
        return false;
    }

    /**
     * 断开连接
     * @param {string} key - 连接标识
     */
    disconnect(key) {
        const connection = this.connections.get(key);
        if (connection) {
            connection.isConnected = false;
            if (connection.ws.readyState === WebSocket.OPEN) {
                connection.ws.close(1000, 'Normal closure');
            }
            this.connections.delete(key);
        }
        this.stopHeartbeat();
    }

    /**
     * 断开所有连接
     */
    disconnectAll() {
        for (const key of this.connections.keys()) {
            this.disconnect(key);
        }
        this.stopHeartbeat();
    }

    /**
     * 计划重连
     * @param {string} key - 连接标识
     * @param {string} url - WebSocket URL
     * @param {function} onMessage - 消息处理回调
     * @param {function} onError - 错误处理回调
     */
    scheduleReconnect(key, url, onMessage, onError) {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // 指数退避
        
        console.log(`${delay}ms后尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts}): ${key}`);
        
        setTimeout(() => {
            if (this.reconnectAttempts <= this.maxReconnectAttempts) {
                this.connect(key, url, onMessage, onError);
            } else {
                console.error(`WebSocket重连失败，已达到最大重试次数: ${key}`);
                if (window.notificationManager) {
                    window.notificationManager.show('连接已断开，请刷新页面重试', 'danger', { persistent: true });
                }
            }
        }, delay);
    }

    /**
     * 开始心跳检测
     * @param {string} key - 连接标识
     */
    startHeartbeat(key) {
        this.stopHeartbeat();
        
        this.heartbeatTimer = setInterval(() => {
            const connection = this.connections.get(key);
            if (connection && connection.isConnected) {
                // 检查上次心跳时间
                const timeSinceLastPing = Date.now() - connection.lastPing;
                if (timeSinceLastPing > this.heartbeatInterval * 2) {
                    console.warn('WebSocket心跳超时，重新连接');
                    this.disconnect(key);
                    this.scheduleReconnect(key, connection.url, connection.onMessage, connection.onError);
                } else {
                    // 发送心跳
                    this.send(key, { type: 'ping', timestamp: Date.now() });
                }
            }
        }, this.heartbeatInterval);
    }

    /**
     * 停止心跳检测
     */
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    /**
     * 获取连接状态
     * @param {string} key - 连接标识
     */
    getConnectionStatus(key) {
        const connection = this.connections.get(key);
        if (!connection) {
            return 'disconnected';
        }
        
        switch (connection.ws.readyState) {
            case WebSocket.CONNECTING:
                return 'connecting';
            case WebSocket.OPEN:
                return connection.isConnected ? 'connected' : 'connecting';
            case WebSocket.CLOSING:
                return 'disconnecting';
            case WebSocket.CLOSED:
                return 'disconnected';
            default:
                return 'unknown';
        }
    }

    /**
     * 获取所有连接状态
     */
    getAllConnectionStatus() {
        const status = {};
        for (const [key] of this.connections) {
            status[key] = this.getConnectionStatus(key);
        }
        return status;
    }
}

/**
 * 任务状态WebSocket管理器
 */
class TaskWebSocketManager {
    constructor() {
        this.wsManager = new WebSocketManager();
        this.currentTaskId = null;
        this.statusUpdateCallbacks = [];
    }

    /**
     * 监听任务状态
     * @param {string} taskId - 任务ID
     */
    watchTask(taskId) {
        if (this.currentTaskId === taskId) {
            return; // 已经在监听该任务
        }

        // 断开之前的连接
        if (this.currentTaskId) {
            this.unwatchTask();
        }

        this.currentTaskId = taskId;
        
        const onMessage = (data) => {
            this.handleTaskUpdate(data);
        };

        const onError = (error) => {
            console.error('任务WebSocket连接错误:', error);
            if (window.notificationManager) {
                window.notificationManager.show('任务状态连接异常', 'warning');
            }
        };

        this.wsManager.connectToTask(taskId, onMessage, onError);
    }

    /**
     * 停止监听任务
     */
    unwatchTask() {
        if (this.currentTaskId) {
            this.wsManager.disconnect(`task_${this.currentTaskId}`);
            this.currentTaskId = null;
        }
    }

    /**
     * 处理任务状态更新
     * @param {object} data - 状态数据
     */
    handleTaskUpdate(data) {
        console.log('收到任务状态更新:', data);
        
        // 更新应用状态
        if (window.Bili2Text && window.Bili2Text.AppState) {
            window.Bili2Text.AppState.currentTask = data;
        }

        // 调用所有注册的回调函数
        this.statusUpdateCallbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error('任务状态更新回调执行失败:', error);
            }
        });

        // 显示通知
        this.showTaskNotification(data);
    }

    /**
     * 显示任务通知
     * @param {object} data - 任务数据
     */
    showTaskNotification(data) {
        if (!window.notificationManager) return;

        const { type, task_id, status, message } = data;
        
        if (type === 'task_update') {
            switch (status) {
                case 'completed':
                    window.notificationManager.show(`任务 ${task_id} 转录完成`, 'success');
                    break;
                case 'failed':
                    window.notificationManager.show(`任务 ${task_id} 转录失败: ${message}`, 'danger');
                    break;
                case 'cancelled':
                    window.notificationManager.show(`任务 ${task_id} 已取消`, 'warning');
                    break;
            }
        }
    }

    /**
     * 注册状态更新回调
     * @param {function} callback - 回调函数
     */
    onStatusUpdate(callback) {
        if (typeof callback === 'function') {
            this.statusUpdateCallbacks.push(callback);
        }
    }

    /**
     * 移除状态更新回调
     * @param {function} callback - 回调函数
     */
    offStatusUpdate(callback) {
        const index = this.statusUpdateCallbacks.indexOf(callback);
        if (index > -1) {
            this.statusUpdateCallbacks.splice(index, 1);
        }
    }

    /**
     * 获取连接状态
     */
    getConnectionStatus() {
        if (!this.currentTaskId) {
            return 'disconnected';
        }
        return this.wsManager.getConnectionStatus(`task_${this.currentTaskId}`);
    }
}

/**
 * 系统状态WebSocket管理器
 */
class SystemWebSocketManager {
    constructor() {
        this.wsManager = new WebSocketManager();
        this.isConnected = false;
        this.statusUpdateCallbacks = [];
    }

    /**
     * 开始监听系统状态
     */
    startMonitoring() {
        if (this.isConnected) {
            return; // 已经在监听
        }

        const onMessage = (data) => {
            this.handleSystemUpdate(data);
        };

        const onError = (error) => {
            console.error('系统WebSocket连接错误:', error);
        };

        this.wsManager.connectToSystem(onMessage, onError);
        this.isConnected = true;
    }

    /**
     * 停止监听系统状态
     */
    stopMonitoring() {
        if (this.isConnected) {
            this.wsManager.disconnect('system');
            this.isConnected = false;
        }
    }

    /**
     * 处理系统状态更新
     * @param {object} data - 系统状态数据
     */
    handleSystemUpdate(data) {
        console.log('收到系统状态更新:', data);
        
        // 调用所有注册的回调函数
        this.statusUpdateCallbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error('系统状态更新回调执行失败:', error);
            }
        });
    }

    /**
     * 注册状态更新回调
     * @param {function} callback - 回调函数
     */
    onStatusUpdate(callback) {
        if (typeof callback === 'function') {
            this.statusUpdateCallbacks.push(callback);
        }
    }

    /**
     * 移除状态更新回调
     * @param {function} callback - 回调函数
     */
    offStatusUpdate(callback) {
        const index = this.statusUpdateCallbacks.indexOf(callback);
        if (index > -1) {
            this.statusUpdateCallbacks.splice(index, 1);
        }
    }

    /**
     * 获取连接状态
     */
    getConnectionStatus() {
        return this.wsManager.getConnectionStatus('system');
    }
}

// 页面卸载时清理WebSocket连接
window.addEventListener('beforeunload', () => {
    if (window.taskWebSocketManager) {
        window.taskWebSocketManager.unwatchTask();
    }
    if (window.systemWebSocketManager) {
        window.systemWebSocketManager.stopMonitoring();
    }
});

// 导出到全局
window.WebSocketManager = WebSocketManager;
window.TaskWebSocketManager = TaskWebSocketManager;
window.SystemWebSocketManager = SystemWebSocketManager; 