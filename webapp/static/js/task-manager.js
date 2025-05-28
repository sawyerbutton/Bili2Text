/**
 * 任务管理器
 * 处理任务创建、状态更新、文件下载等功能
 */

class TaskManager {
    constructor() {
        this.currentTask = null;
        this.taskWebSocket = null;
        this.progressTimer = null;
        this.startTime = null;
        
        this.bindEvents();
        this.initializeWebSocket();
    }

    /**
     * 初始化WebSocket连接
     */
    initializeWebSocket() {
        if (typeof TaskWebSocketManager !== 'undefined') {
            this.taskWebSocket = new TaskWebSocketManager();
            this.taskWebSocket.onStatusUpdate((data) => {
                this.handleTaskUpdate(data);
            });
        }
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 转录表单提交
        const form = document.getElementById('transcriptionForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.startTranscription();
            });
        }

        // 取消任务
        const cancelBtn = document.getElementById('cancelTask');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.cancelTask();
            });
        }

        // 查看任务详情
        const detailBtn = document.getElementById('viewTaskDetail');
        if (detailBtn) {
            detailBtn.addEventListener('click', () => {
                this.showTaskDetail();
            });
        }

        // 下载结果
        const downloadBtn = document.getElementById('downloadResult');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                this.downloadResult();
            });
        }

        // 下载音频
        const downloadAudioBtn = document.getElementById('downloadAudio');
        if (downloadAudioBtn) {
            downloadAudioBtn.addEventListener('click', () => {
                this.downloadAudio();
            });
        }

        // 预览结果
        const previewBtn = document.getElementById('previewResult');
        if (previewBtn) {
            previewBtn.addEventListener('click', () => {
                this.previewResult();
            });
        }

        // 新建任务
        const newTaskBtn = document.getElementById('newTask');
        if (newTaskBtn) {
            newTaskBtn.addEventListener('click', () => {
                this.resetForm();
            });
        }

        // 复制到剪贴板
        const copyBtn = document.getElementById('copyToClipboard');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                this.copyResultToClipboard();
            });
        }

        // 批量处理
        const batchBtn = document.getElementById('startBatchProcessing');
        if (batchBtn) {
            batchBtn.addEventListener('click', () => {
                this.startBatchProcessing();
            });
        }
    }

    /**
     * 开始转录
     */
    async startTranscription() {
        try {
            // 获取表单数据
            const formData = this.getFormData();
            
            // 验证数据
            if (!this.validateFormData(formData)) {
                return;
            }

            // 显示加载状态
            this.showLoadingState();

            // 发送请求，集成错误处理
            const response = await window.apiClient.post('/tasks/', formData, {
                retryCallback: () => this.startTranscription(),
                showErrorDetails: true
            });
            
            this.currentTask = response.data;
            this.startTime = Date.now();
            
            // 显示任务状态卡片
            this.showTaskCard();
            
            // 开始WebSocket监听
            if (this.taskWebSocket) {
                this.taskWebSocket.watchTask(this.currentTask.task_id);
            }
            
            // 开始进度更新
            this.startProgressTimer();
            
            window.notificationManager.show('任务创建成功，开始转录...', 'success');
            
        } catch (error) {
            this.hideLoadingState();
            
            // 错误已经由ErrorHandler处理，这里只需要记录日志
            console.error('开始转录失败:', error);
            
            // 如果是特定的业务错误，提供额外的用户指导
            if (error.code === 'INVALID_URL') {
                this.showUrlHelp();
            } else if (error.code === 'SYSTEM_OVERLOAD') {
                this.showSystemOverloadHelp();
            }
        }
    }

    /**
     * 获取表单数据
     */
    getFormData() {
        const url = document.getElementById('videoUrl').value.trim();
        const model = document.querySelector('input[name="model"]:checked').value;
        const useProxy = document.getElementById('useProxy').checked;
        const keepAudio = document.getElementById('keepAudio').checked;
        const outputFormat = document.getElementById('outputFormat').value;
        const language = document.getElementById('language').value;

        return {
            url,
            model_name: model,
            options: {
                use_proxy: useProxy,
                keep_audio: keepAudio,
                output_format: outputFormat,
                language: language === 'auto' ? null : language
            }
        };
    }

    /**
     * 验证表单数据
     */
    validateFormData(data) {
        if (!data.url) {
            window.notificationManager.show('请输入视频URL', 'warning');
            return false;
        }

        if (!window.Bili2Text.Utils.validateBilibiliUrl(data.url)) {
            window.notificationManager.show('请输入有效的哔哩哔哩视频链接', 'warning');
            return false;
        }

        return true;
    }

    /**
     * 显示加载状态
     */
    showLoadingState() {
        const submitBtn = document.getElementById('startTranscription');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loading-spinner me-2"></span>创建任务中...';
        }
    }

    /**
     * 隐藏加载状态
     */
    hideLoadingState() {
        const submitBtn = document.getElementById('startTranscription');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-play me-1"></i>开始转录';
        }
    }

    /**
     * 显示任务状态卡片
     */
    showTaskCard() {
        const taskCard = document.getElementById('currentTaskCard');
        const resultCard = document.getElementById('taskResultCard');
        
        if (taskCard) {
            taskCard.style.display = 'block';
            taskCard.classList.add('fade-in');
        }
        
        if (resultCard) {
            resultCard.style.display = 'none';
        }

        this.updateTaskInfo();
    }

    /**
     * 更新任务信息
     */
    updateTaskInfo() {
        if (!this.currentTask) return;

        const taskInfo = document.getElementById('taskInfo');
        if (taskInfo) {
            taskInfo.innerHTML = `
                <div class="mb-2">
                    <strong>任务ID:</strong> ${this.currentTask.task_id}
                </div>
                <div class="mb-2">
                    <strong>视频URL:</strong> 
                    <a href="${this.currentTask.url}" target="_blank" class="text-decoration-none">
                        ${this.currentTask.title || this.currentTask.url}
                    </a>
                </div>
                <div class="mb-2">
                    <strong>使用模型:</strong> ${this.currentTask.model_name}
                </div>
            `;
        }
    }

    /**
     * 处理任务状态更新
     */
    handleTaskUpdate(data) {
        if (!data || data.task_id !== this.currentTask?.task_id) {
            return;
        }

        // 更新当前任务数据
        this.currentTask = { ...this.currentTask, ...data };

        // 更新UI
        this.updateProgress(data.progress || 0);
        this.updateStatus(data.status);
        this.updateCurrentStage(data.message || data.current_stage);

        // 如果任务完成或失败，停止进度计时器
        if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
            this.stopProgressTimer();
            
            if (data.status === 'completed') {
                this.showTaskResult();
            }
        }
    }

    /**
     * 更新进度
     */
    updateProgress(progress) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }
        
        if (progressText) {
            progressText.textContent = `${Math.round(progress)}%`;
        }
    }

    /**
     * 更新状态
     */
    updateStatus(status) {
        const statusElement = document.getElementById('taskStatus');
        if (statusElement) {
            const statusMap = {
                'pending': '等待中',
                'downloading': '下载中',
                'transcribing': '转录中',
                'completed': '已完成',
                'failed': '失败',
                'cancelled': '已取消'
            };
            statusElement.textContent = statusMap[status] || status;
        }
    }

    /**
     * 更新当前阶段
     */
    updateCurrentStage(stage) {
        const stageElement = document.getElementById('currentStage');
        if (stageElement && stage) {
            stageElement.textContent = stage;
        }
    }

    /**
     * 开始进度计时器
     */
    startProgressTimer() {
        this.stopProgressTimer();
        
        this.progressTimer = setInterval(() => {
            this.updateElapsedTime();
            this.updateRemainingTime();
        }, 1000);
    }

    /**
     * 停止进度计时器
     */
    stopProgressTimer() {
        if (this.progressTimer) {
            clearInterval(this.progressTimer);
            this.progressTimer = null;
        }
    }

    /**
     * 更新已用时间
     */
    updateElapsedTime() {
        if (!this.startTime) return;
        
        const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
        const elapsedElement = document.getElementById('elapsedTime');
        
        if (elapsedElement) {
            elapsedElement.textContent = window.Bili2Text.Utils.formatDuration(elapsed);
        }
    }

    /**
     * 更新预计剩余时间
     */
    updateRemainingTime() {
        const progress = this.currentTask?.progress || 0;
        const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
        
        if (progress > 0 && progress < 100) {
            const estimated = (elapsed / progress) * (100 - progress);
            const remainingElement = document.getElementById('remainingTime');
            
            if (remainingElement) {
                remainingElement.textContent = window.Bili2Text.Utils.formatDuration(estimated);
            }
        }
    }

    /**
     * 取消任务
     */
    async cancelTask() {
        if (!this.currentTask) return;

        await this.safeApiCall(async () => {
            const response = await window.apiClient.post(`/tasks/${this.currentTask.task_id}/cancel`);
            
            window.notificationManager.show('任务已取消', 'warning');
            this.stopProgressTimer();
            this.updateStatus('cancelled');
        }, 'cancel_task');
    }

    /**
     * 显示任务详情
     */
    async showTaskDetail() {
        if (!this.currentTask) return;

        await this.safeApiCall(async () => {
            const response = await window.apiClient.get(`/tasks/${this.currentTask.task_id}`);
            const task = response.data;
            this.showTaskDetailModal(task);
        }, 'show_task_detail');
    }

    /**
     * 显示任务详情模态框
     */
    showTaskDetailModal(task) {
        const modal = document.getElementById('taskDetailModal');
        const content = document.getElementById('taskDetailContent');
        
        if (content) {
            content.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>基本信息</h6>
                        <table class="table table-sm">
                            <tr><td>任务ID</td><td>${task.task_id}</td></tr>
                            <tr><td>状态</td><td><span class="badge bg-${this.getStatusColor(task.status)}">${task.status}</span></td></tr>
                            <tr><td>进度</td><td>${Math.round(task.progress || 0)}%</td></tr>
                            <tr><td>模型</td><td>${task.model_name}</td></tr>
                            <tr><td>创建时间</td><td>${new Date(task.created_at).toLocaleString('zh-CN')}</td></tr>
                            ${task.completed_at ? `<tr><td>完成时间</td><td>${new Date(task.completed_at).toLocaleString('zh-CN')}</td></tr>` : ''}
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6>文件信息</h6>
                        <table class="table table-sm">
                            <tr><td>视频URL</td><td><a href="${task.url}" target="_blank">${task.title || '查看视频'}</a></td></tr>
                            ${task.file_size ? `<tr><td>文件大小</td><td>${window.Bili2Text.Utils.formatFileSize(task.file_size)}</td></tr>` : ''}
                            ${task.duration ? `<tr><td>音频时长</td><td>${window.Bili2Text.Utils.formatDuration(task.duration)}</td></tr>` : ''}
                            ${task.result_file_path ? `<tr><td>结果文件</td><td>✅ 已生成</td></tr>` : ''}
                            ${task.audio_file_path ? `<tr><td>音频文件</td><td>✅ 已保留</td></tr>` : ''}
                        </table>
                    </div>
                </div>
                ${task.error_message ? `
                    <div class="mt-3">
                        <h6>错误信息</h6>
                        <div class="alert alert-danger">${task.error_message}</div>
                    </div>
                ` : ''}
            `;
        }
        
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }

    /**
     * 显示任务结果
     */
    showTaskResult() {
        const taskCard = document.getElementById('currentTaskCard');
        const resultCard = document.getElementById('taskResultCard');
        
        if (taskCard) {
            taskCard.style.display = 'none';
        }
        
        if (resultCard) {
            resultCard.style.display = 'block';
            resultCard.classList.add('fade-in');
        }

        this.updateResultInfo();
    }

    /**
     * 更新结果信息
     */
    updateResultInfo() {
        if (!this.currentTask) return;

        const resultInfo = document.getElementById('resultInfo');
        if (resultInfo) {
            const elapsed = this.startTime ? Math.floor((Date.now() - this.startTime) / 1000) : 0;
            
            resultInfo.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-2">
                            <strong>任务ID:</strong> ${this.currentTask.task_id}
                        </div>
                        <div class="mb-2">
                            <strong>视频标题:</strong> ${this.currentTask.title || '未知'}
                        </div>
                        <div class="mb-2">
                            <strong>转录时长:</strong> ${window.Bili2Text.Utils.formatDuration(elapsed)}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-2">
                            <strong>音频时长:</strong> ${this.currentTask.duration ? window.Bili2Text.Utils.formatDuration(this.currentTask.duration) : '未知'}
                        </div>
                        <div class="mb-2">
                            <strong>文件大小:</strong> ${this.currentTask.file_size ? window.Bili2Text.Utils.formatFileSize(this.currentTask.file_size) : '未知'}
                        </div>
                        <div class="mb-2">
                            <strong>使用模型:</strong> ${this.currentTask.model_name}
                        </div>
                    </div>
                </div>
            `;
        }

        // 显示/隐藏音频下载按钮
        const downloadAudioBtn = document.getElementById('downloadAudio');
        if (downloadAudioBtn) {
            downloadAudioBtn.style.display = this.currentTask.audio_file_path ? 'inline-block' : 'none';
        }
    }

    /**
     * 下载结果文件
     */
    async downloadResult() {
        if (!this.currentTask) return;

        await this.safeApiCall(async () => {
            const url = `/api/files/${this.currentTask.task_id}/result`;
            const filename = `${this.currentTask.title || this.currentTask.task_id}_transcript.txt`;
            
            // 创建下载链接
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            window.notificationManager.show('开始下载转录结果', 'success');
        }, 'download_result');
    }

    /**
     * 下载音频文件
     */
    async downloadAudio() {
        if (!this.currentTask) return;

        await this.safeApiCall(async () => {
            const url = `/api/files/${this.currentTask.task_id}/audio`;
            const filename = `${this.currentTask.title || this.currentTask.task_id}_audio.m4a`;
            
            // 创建下载链接
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            window.notificationManager.show('开始下载音频文件', 'success');
        }, 'download_audio');
    }

    /**
     * 预览结果
     */
    async previewResult() {
        if (!this.currentTask) return;

        await this.safeApiCall(async () => {
            const response = await fetch(`/api/files/${this.currentTask.task_id}/result`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const content = await response.text();
            this.showPreviewModal(content);
        }, 'preview_result');
    }

    /**
     * 显示预览模态框
     */
    showPreviewModal(content) {
        const modal = document.getElementById('previewModal');
        const previewContent = document.getElementById('previewContent');
        
        if (previewContent) {
            previewContent.innerHTML = `<pre class="bg-light p-3 rounded">${content}</pre>`;
        }
        
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }

    /**
     * 复制结果到剪贴板
     */
    async copyResultToClipboard() {
        try {
            const previewContent = document.getElementById('previewContent');
            if (previewContent) {
                const text = previewContent.textContent;
                await window.Bili2Text.Utils.copyToClipboard(text);
            }
        } catch (error) {
            console.error('复制失败:', error);
            window.notificationManager.show('复制失败', 'danger');
        }
    }

    /**
     * 重置表单
     */
    resetForm() {
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

        // 隐藏任务卡片
        const taskCard = document.getElementById('currentTaskCard');
        const resultCard = document.getElementById('taskResultCard');
        
        if (taskCard) {
            taskCard.style.display = 'none';
        }
        
        if (resultCard) {
            resultCard.style.display = 'none';
        }

        // 停止WebSocket监听
        if (this.taskWebSocket) {
            this.taskWebSocket.unwatchTask();
        }

        // 重置状态
        this.currentTask = null;
        this.startTime = null;
        this.stopProgressTimer();
    }

    /**
     * 开始批量处理
     */
    async startBatchProcessing() {
        const urls = document.getElementById('batchUrls').value.trim();
        const model = document.getElementById('batchModel').value;
        const format = document.getElementById('batchFormat').value;
        const keepAudio = document.getElementById('batchKeepAudio').checked;

        if (!urls) {
            window.notificationManager.show('请输入视频URL列表', 'warning');
            return;
        }

        const urlList = urls.split('\n').filter(url => url.trim());
        if (urlList.length === 0) {
            window.notificationManager.show('请输入有效的视频URL', 'warning');
            return;
        }

        if (urlList.length > 10) {
            window.notificationManager.show('最多支持10个视频同时处理', 'warning');
            return;
        }

        try {
            const tasks = [];
            for (const url of urlList) {
                const formData = {
                    url: url.trim(),
                    model_name: model,
                    options: {
                        keep_audio: keepAudio,
                        output_format: format
                    }
                };

                const response = await window.apiClient.post('/tasks/', formData);
                if (response.success) {
                    tasks.push(response.data);
                }
            }

            window.notificationManager.show(`成功创建 ${tasks.length} 个批量任务`, 'success');
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('batchModal'));
            if (modal) {
                modal.hide();
            }

            // 跳转到历史页面查看批量任务
            window.location.href = '/history';
        } catch (error) {
            console.error('批量处理失败:', error);
            window.notificationManager.show(`批量处理失败: ${error.message}`, 'danger');
        }
    }

    /**
     * 获取状态颜色
     */
    getStatusColor(status) {
        const colorMap = {
            'pending': 'secondary',
            'downloading': 'info',
            'transcribing': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary'
        };
        return colorMap[status] || 'secondary';
    }

    /**
     * 显示URL帮助信息
     */
    showUrlHelp() {
        const helpModal = document.createElement('div');
        helpModal.className = 'modal fade';
        helpModal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-info text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-info-circle me-2"></i>
                            URL格式帮助
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>请确保输入的是有效的哔哩哔哩视频链接，支持以下格式：</p>
                        <ul>
                            <li><code>https://www.bilibili.com/video/BV1234567890</code></li>
                            <li><code>https://b23.tv/abc123</code></li>
                            <li><code>BV1234567890</code> (仅BV号)</li>
                        </ul>
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            <strong>注意：</strong>暂不支持其他视频平台的链接
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" data-bs-dismiss="modal">我知道了</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(helpModal);
        const bsModal = new bootstrap.Modal(helpModal);
        bsModal.show();

        // 模态框关闭后移除DOM元素
        helpModal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(helpModal);
        });
    }

    /**
     * 显示系统过载帮助信息
     */
    showSystemOverloadHelp() {
        const helpModal = document.createElement('div');
        helpModal.className = 'modal fade';
        helpModal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title">
                            <i class="fas fa-server me-2"></i>
                            系统繁忙
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>当前系统负载较高，建议您：</p>
                        <ul>
                            <li>等待几分钟后重试</li>
                            <li>选择较小的模型（如tiny或base）以减少处理时间</li>
                            <li>避免在高峰时段提交任务</li>
                        </ul>
                        <div class="alert alert-info">
                            <i class="fas fa-lightbulb me-2"></i>
                            <strong>提示：</strong>您可以在"系统状态"页面查看当前系统负载情况
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">稍后重试</button>
                        <button type="button" class="btn btn-warning" onclick="this.closest('.modal').querySelector('[data-bs-dismiss=modal]').click(); setTimeout(() => window.taskManager.startTranscription(), 60000);">
                            1分钟后自动重试
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(helpModal);
        const bsModal = new bootstrap.Modal(helpModal);
        bsModal.show();

        // 模态框关闭后移除DOM元素
        helpModal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(helpModal);
        });
    }

    /**
     * 处理网络错误
     */
    handleNetworkError(error) {
        if (window.errorHandler) {
            window.errorHandler.handleError(error, 'task_manager', {
                retryCallback: () => this.startTranscription(),
                modal: true
            });
        }
    }

    /**
     * 安全执行API调用
     */
    async safeApiCall(apiCall, context = 'unknown') {
        try {
            return await apiCall();
        } catch (error) {
            if (window.errorHandler) {
                window.errorHandler.handleError(error, context);
            }
            throw error;
        }
    }
}

// 导出到全局
window.TaskManager = TaskManager; 