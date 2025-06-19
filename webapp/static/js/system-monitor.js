/**
 * 系统监控JavaScript
 * 用于系统状态页面的图表显示和实时更新
 */

class SystemMonitor {
    constructor() {
        this.charts = {};
        this.systemWebSocket = null;
        this.autoRefresh = true;
        this.refreshInterval = null;
        
        this.initializeCharts();
        this.bindEvents();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    /**
     * 初始化图表
     */
    initializeCharts() {
        // CPU使用率图表
        this.charts.cpu = new Chart(document.getElementById('cpuChart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU使用率 (%)',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    x: {
                        type: 'time',
                        time: {
                            displayFormats: {
                                minute: 'HH:mm'
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        // 内存使用率图表
        this.charts.memory = new Chart(document.getElementById('memoryChart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '内存使用率 (%)',
                    data: [],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    x: {
                        type: 'time',
                        time: {
                            displayFormats: {
                                minute: 'HH:mm'
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        // 任务处理趋势图表
        this.charts.taskTrend = new Chart(document.getElementById('taskTrendChart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: '已完成',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.1
                    },
                    {
                        label: '失败',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.1
                    },
                    {
                        label: '活跃',
                        data: [],
                        borderColor: 'rgb(255, 205, 86)',
                        backgroundColor: 'rgba(255, 205, 86, 0.1)',
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    },
                    x: {
                        type: 'time',
                        time: {
                            displayFormats: {
                                minute: 'HH:mm'
                            }
                        }
                    }
                }
            }
        });

        // 任务状态分布饼图
        this.charts.taskStatus = new Chart(document.getElementById('taskStatusChart'), {
            type: 'doughnut',
            data: {
                labels: ['已完成', '失败', '等待中', '处理中'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        'rgb(75, 192, 192)',
                        'rgb(255, 99, 132)',
                        'rgb(255, 205, 86)',
                        'rgb(54, 162, 235)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 刷新按钮
        const refreshBtn = document.getElementById('refreshStatus');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshSystemStatus();
            });
        }

        // 自动刷新开关
        const autoRefreshToggle = document.getElementById('autoRefresh');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                this.autoRefresh = e.target.checked;
                if (this.autoRefresh) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }
    }

    /**
     * 加载初始数据
     */
    async loadInitialData() {
        try {
            await this.refreshSystemStatus();
            await this.loadPerformanceHistory();
            await this.loadServiceStatus();
            await this.loadAvailableModels();
        } catch (error) {
            console.error('加载初始数据失败:', error);
            window.notificationManager.show('加载系统数据失败', 'danger');
        }
    }

    /**
     * 刷新系统状态
     */
    async refreshSystemStatus() {
        try {
            const response = await window.apiClient.get('/system/status');
            if (response.success) {
                this.updateSystemOverview(response.data);
                this.updateTaskStatistics(response.data);
            }
        } catch (error) {
            console.error('刷新系统状态失败:', error);
        }
    }

    /**
     * 加载性能历史数据
     */
    async loadPerformanceHistory() {
        try {
            // 这里应该调用获取性能历史的API
            // 暂时使用模拟数据
            const now = new Date();
            const labels = [];
            const cpuData = [];
            const memoryData = [];

            for (let i = 59; i >= 0; i--) {
                const time = new Date(now.getTime() - i * 60000);
                labels.push(time);
                cpuData.push(Math.random() * 100);
                memoryData.push(Math.random() * 100);
            }

            this.updateChart('cpu', labels, cpuData);
            this.updateChart('memory', labels, memoryData);
        } catch (error) {
            console.error('加载性能历史失败:', error);
        }
    }

    /**
     * 加载服务状态
     */
    async loadServiceStatus() {
        try {
            // 模拟服务状态数据
            const services = {
                'database': { status: 'running', message: '数据库连接正常' },
                'task_manager': { status: 'running', message: '活跃任务: 2, 队列: 1' },
                'file_manager': { status: 'running', message: '管理文件: 156' },
                'whisper': { status: 'warning', message: 'Whisper未安装，使用模拟模式' },
                'yt_dlp': { status: 'running', message: 'yt-dlp 2023.12.30' }
            };

            this.updateServiceStatus(services);
        } catch (error) {
            console.error('加载服务状态失败:', error);
        }
    }

    /**
     * 加载可用模型
     */
    async loadAvailableModels() {
        try {
            const response = await window.apiClient.get('/system/models');
            if (response.success) {
                this.updateAvailableModels(response.data.models);
            }
        } catch (error) {
            console.error('加载可用模型失败:', error);
        }
    }

    /**
     * 更新系统概览
     */
    updateSystemOverview(data) {
        // 更新系统状态
        const statusElement = document.getElementById('systemStatus');
        if (statusElement) {
            statusElement.textContent = data.status === 'healthy' ? '运行中' : '异常';
            statusElement.className = data.status === 'healthy' ? 'text-success' : 'text-danger';
        }

        // 更新运行时间
        const uptimeElement = document.getElementById('uptime');
        if (uptimeElement) {
            uptimeElement.textContent = this.formatUptime(data.uptime || 0);
        }

        // 更新活跃任务
        const activeTasksElement = document.getElementById('activeTasks');
        if (activeTasksElement) {
            activeTasksElement.textContent = data.active_tasks || 0;
        }

        // 更新工作进程
        const activeWorkersElement = document.getElementById('activeWorkers');
        if (activeWorkersElement) {
            activeWorkersElement.textContent = data.workers?.active || 3;
        }
    }

    /**
     * 更新任务统计
     */
    updateTaskStatistics(data) {
        const taskData = [
            data.completed_tasks || 0,
            data.failed_tasks || 0,
            data.pending_tasks || 0,
            data.active_tasks || 0
        ];

        this.charts.taskStatus.data.datasets[0].data = taskData;
        this.charts.taskStatus.update();
    }

    /**
     * 更新图表
     */
    updateChart(chartName, labels, data) {
        if (!this.charts[chartName]) return;

        this.charts[chartName].data.labels = labels;
        this.charts[chartName].data.datasets[0].data = data;
        this.charts[chartName].update();
    }

    /**
     * 更新服务状态
     */
    updateServiceStatus(services) {
        const container = document.getElementById('serviceStatus');
        if (!container) return;

        container.innerHTML = '';

        Object.entries(services).forEach(([serviceName, serviceInfo]) => {
            const statusClass = this.getStatusClass(serviceInfo.status);
            const statusIcon = this.getStatusIcon(serviceInfo.status);
            
            const serviceElement = document.createElement('div');
            serviceElement.className = 'list-group-item d-flex justify-content-between align-items-center';
            serviceElement.innerHTML = `
                <div>
                    <strong>${this.getServiceDisplayName(serviceName)}</strong>
                    <div class="small text-muted">${serviceInfo.message}</div>
                </div>
                <span class="badge bg-${statusClass}">
                    <i class="${statusIcon} me-1"></i>${this.getStatusText(serviceInfo.status)}
                </span>
            `;
            
            container.appendChild(serviceElement);
        });
    }

    /**
     * 更新可用模型
     */
    updateAvailableModels(models) {
        const container = document.getElementById('availableModels');
        if (!container) return;

        container.innerHTML = '';

        models.forEach(model => {
            const modelElement = document.createElement('div');
            modelElement.className = 'card mb-2';
            modelElement.innerHTML = `
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="card-title mb-1">
                                ${model.name}
                                ${model.default ? '<span class="badge bg-primary ms-1">推荐</span>' : ''}
                            </h6>
                            <p class="card-text small text-muted mb-1">${model.recommended_for}</p>
                            <div class="small">
                                <span class="me-3"><i class="fas fa-download me-1"></i>${model.size}</span>
                                <span class="me-3"><i class="fas fa-memory me-1"></i>${model.memory_required}</span>
                                <span><i class="fas fa-tachometer-alt me-1"></i>${this.getSpeedText(model.speed)}</span>
                            </div>
                        </div>
                        <div class="text-end">
                            ${this.getAccuracyStars(model.accuracy)}
                        </div>
                    </div>
                </div>
            `;
            
            container.appendChild(modelElement);
        });
    }

    /**
     * 开始自动刷新
     */
    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        this.refreshInterval = setInterval(() => {
            if (this.autoRefresh) {
                this.refreshSystemStatus();
            }
        }, 5000); // 每5秒刷新一次

        // 启动WebSocket连接
        this.startWebSocketConnection();
    }

    /**
     * 停止自动刷新
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }

        // 关闭WebSocket连接
        this.stopWebSocketConnection();
    }

    /**
     * 启动WebSocket连接
     */
    startWebSocketConnection() {
        if (typeof SystemWebSocketManager !== 'undefined') {
            this.systemWebSocket = new SystemWebSocketManager();
            this.systemWebSocket.onStatusUpdate((data) => {
                this.handleWebSocketUpdate(data);
            });
            this.systemWebSocket.startMonitoring();
        }
    }

    /**
     * 停止WebSocket连接
     */
    stopWebSocketConnection() {
        if (this.systemWebSocket) {
            this.systemWebSocket.stopMonitoring();
            this.systemWebSocket = null;
        }
    }

    /**
     * 处理WebSocket更新
     */
    handleWebSocketUpdate(data) {
        if (data.type === 'system_update') {
            this.updateSystemOverview(data.data);
            this.updateTaskStatistics(data.data);
            
            // 更新性能图表
            const now = new Date();
            this.addDataPoint('cpu', now, data.data.cpu_usage);
            this.addDataPoint('memory', now, data.data.memory_usage);
        }
    }

    /**
     * 添加数据点到图表
     */
    addDataPoint(chartName, timestamp, value) {
        if (!this.charts[chartName]) return;

        const chart = this.charts[chartName];
        chart.data.labels.push(timestamp);
        chart.data.datasets[0].data.push(value);

        // 保持最多60个数据点
        if (chart.data.labels.length > 60) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update('none'); // 无动画更新
    }

    /**
     * 格式化运行时间
     */
    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);

        if (days > 0) {
            return `${days}天${hours}小时`;
        } else if (hours > 0) {
            return `${hours}小时${minutes}分钟`;
        } else {
            return `${minutes}分钟`;
        }
    }

    /**
     * 获取状态样式类
     */
    getStatusClass(status) {
        const classes = {
            'running': 'success',
            'warning': 'warning',
            'error': 'danger',
            'stopped': 'secondary'
        };
        return classes[status] || 'secondary';
    }

    /**
     * 获取状态图标
     */
    getStatusIcon(status) {
        const icons = {
            'running': 'fas fa-check-circle',
            'warning': 'fas fa-exclamation-triangle',
            'error': 'fas fa-times-circle',
            'stopped': 'fas fa-stop-circle'
        };
        return icons[status] || 'fas fa-question-circle';
    }

    /**
     * 获取状态文本
     */
    getStatusText(status) {
        const texts = {
            'running': '运行中',
            'warning': '警告',
            'error': '错误',
            'stopped': '已停止'
        };
        return texts[status] || '未知';
    }

    /**
     * 获取服务显示名称
     */
    getServiceDisplayName(serviceName) {
        const names = {
            'database': '数据库',
            'task_manager': '任务管理器',
            'file_manager': '文件管理器',
            'whisper': 'Whisper引擎',
            'yt_dlp': '视频下载器'
        };
        return names[serviceName] || serviceName;
    }

    /**
     * 获取速度文本
     */
    getSpeedText(speed) {
        const texts = {
            'very_fast': '极快',
            'fast': '快',
            'medium': '中等',
            'slow': '慢'
        };
        return texts[speed] || speed;
    }

    /**
     * 获取精度星级
     */
    getAccuracyStars(accuracy) {
        const levels = {
            'low': 2,
            'medium': 3,
            'high': 4,
            'very_high': 5
        };
        
        const starCount = levels[accuracy] || 3;
        let stars = '';
        
        for (let i = 0; i < 5; i++) {
            if (i < starCount) {
                stars += '<i class="fas fa-star text-warning"></i>';
            } else {
                stars += '<i class="far fa-star text-muted"></i>';
            }
        }
        
        return stars;
    }
}

// 导出到全局
window.SystemMonitor = SystemMonitor; 