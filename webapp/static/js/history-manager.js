/**
 * 历史管理器
 * 处理任务历史列表、筛选、批量操作等功能
 */

class HistoryManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 20;
        this.totalPages = 1;
        this.selectedTasks = new Set();
        this.filters = {
            status: '',
            timeRange: '',
            search: ''
        };
        
        this.bindEvents();
        this.loadTasks();
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 刷新按钮
        const refreshBtn = document.getElementById('refreshTasks');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadTasks();
            });
        }

        // 清空历史按钮
        const clearBtn = document.getElementById('clearHistory');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearHistory();
            });
        }

        // 应用筛选按钮
        const applyBtn = document.getElementById('applyFilters');
        if (applyBtn) {
            applyBtn.addEventListener('click', () => {
                this.applyFilters();
            });
        }

        // 搜索框回车事件
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.applyFilters();
                }
            });
        }

        // 批量操作按钮
        const batchDownloadBtn = document.getElementById('batchDownload');
        if (batchDownloadBtn) {
            batchDownloadBtn.addEventListener('click', () => {
                this.batchDownload();
            });
        }

        const batchDeleteBtn = document.getElementById('batchDelete');
        if (batchDeleteBtn) {
            batchDeleteBtn.addEventListener('click', () => {
                this.batchDelete();
            });
        }

        const clearSelectionBtn = document.getElementById('clearSelection');
        if (clearSelectionBtn) {
            clearSelectionBtn.addEventListener('click', () => {
                this.clearSelection();
            });
        }
    }

    /**
     * 加载任务列表
     */
    async loadTasks() {
        try {
            const params = {
                page: this.currentPage,
                limit: this.pageSize,
                ...this.filters
            };

            // 移除空值
            Object.keys(params).forEach(key => {
                if (!params[key]) {
                    delete params[key];
                }
            });

            const response = await window.apiClient.get('/tasks/', params);
            
            if (response.success) {
                this.renderTasks(response.data.tasks);
                this.updatePagination(response.data);
            } else {
                throw new Error(response.message || '加载任务列表失败');
            }
        } catch (error) {
            console.error('加载任务列表失败:', error);
            window.notificationManager.show(`加载失败: ${error.message}`, 'danger');
        }
    }

    /**
     * 渲染任务列表
     */
    renderTasks(tasks) {
        const container = document.getElementById('tasksList');
        if (!container) return;

        if (tasks.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">暂无任务记录</h5>
                    <p class="text-muted">开始您的第一个转录任务吧！</p>
                    <a href="/" class="btn btn-primary">
                        <i class="fas fa-plus me-1"></i>创建任务
                    </a>
                </div>
            `;
            return;
        }

        const tasksHtml = tasks.map(task => this.createTaskCard(task)).join('');
        container.innerHTML = tasksHtml;

        // 绑定任务卡片事件
        this.bindTaskCardEvents();
    }

    /**
     * 创建任务卡片
     */
    createTaskCard(task) {
        const statusColor = this.getStatusColor(task.status);
        const statusIcon = this.getStatusIcon(task.status);
        const createdAt = new Date(task.created_at).toLocaleString('zh-CN');
        
        return `
            <div class="card task-card ${task.status} mb-3" data-task-id="${task.id}">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-auto">
                            <div class="form-check">
                                <input class="form-check-input task-checkbox" type="checkbox" 
                                       value="${task.id}" data-task-id="${task.id}">
                            </div>
                        </div>
                        <div class="col">
                            <div class="d-flex justify-content-between align-items-start">
                                <div class="flex-grow-1">
                                    <h6 class="card-title mb-1">
                                        <i class="${statusIcon} me-2 text-${statusColor}"></i>
                                        ${task.title || task.url}
                                    </h6>
                                    <div class="text-muted small mb-2">
                                        <span class="me-3">
                                            <i class="fas fa-calendar me-1"></i>${createdAt}
                                        </span>
                                        <span class="me-3">
                                            <i class="fas fa-microchip me-1"></i>${task.model_name}
                                        </span>
                                        ${task.file_size ? `
                                            <span class="me-3">
                                                <i class="fas fa-file me-1"></i>${window.Bili2Text.Utils.formatFileSize(task.file_size)}
                                            </span>
                                        ` : ''}
                                        ${task.duration ? `
                                            <span class="me-3">
                                                <i class="fas fa-clock me-1"></i>${window.Bili2Text.Utils.formatDuration(task.duration)}
                                            </span>
                                        ` : ''}
                                    </div>
                                    ${task.progress !== undefined && task.status !== 'completed' ? `
                                        <div class="progress mb-2" style="height: 4px;">
                                            <div class="progress-bar bg-${statusColor}" 
                                                 style="width: ${task.progress}%"></div>
                                        </div>
                                    ` : ''}
                                </div>
                                <div class="text-end">
                                    <span class="badge bg-${statusColor} mb-2">${this.getStatusText(task.status)}</span>
                                    <div class="btn-group btn-group-sm">
                                        ${task.status === 'completed' ? `
                                            <button class="btn btn-outline-primary download-btn" 
                                                    data-task-id="${task.id}" data-action="download">
                                                <i class="fas fa-download"></i>
                                            </button>
                                        ` : ''}
                                        <button class="btn btn-outline-info detail-btn" 
                                                data-task-id="${task.id}" data-action="detail">
                                            <i class="fas fa-info-circle"></i>
                                        </button>
                                        ${task.status === 'failed' ? `
                                            <button class="btn btn-outline-warning retry-btn" 
                                                    data-task-id="${task.id}" data-action="retry">
                                                <i class="fas fa-redo"></i>
                                            </button>
                                        ` : ''}
                                        ${['pending', 'downloading', 'transcribing'].includes(task.status) ? `
                                            <button class="btn btn-outline-danger cancel-btn" 
                                                    data-task-id="${task.id}" data-action="cancel">
                                                <i class="fas fa-stop"></i>
                                            </button>
                                        ` : `
                                            <button class="btn btn-outline-danger delete-btn" 
                                                    data-task-id="${task.id}" data-action="delete">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        `}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * 绑定任务卡片事件
     */
    bindTaskCardEvents() {
        // 复选框事件
        document.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const taskId = e.target.dataset.taskId;
                if (e.target.checked) {
                    this.selectedTasks.add(taskId);
                } else {
                    this.selectedTasks.delete(taskId);
                }
                this.updateBatchActions();
            });
        });

        // 操作按钮事件
        document.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const taskId = e.target.closest('[data-task-id]').dataset.taskId;
                const action = e.target.closest('[data-action]').dataset.action;
                this.handleTaskAction(taskId, action);
            });
        });
    }

    /**
     * 处理任务操作
     */
    async handleTaskAction(taskId, action) {
        try {
            switch (action) {
                case 'download':
                    await this.downloadTask(taskId);
                    break;
                case 'detail':
                    await this.showTaskDetail(taskId);
                    break;
                case 'retry':
                    await this.retryTask(taskId);
                    break;
                case 'cancel':
                    await this.cancelTask(taskId);
                    break;
                case 'delete':
                    await this.deleteTask(taskId);
                    break;
            }
        } catch (error) {
            console.error(`任务操作失败 (${action}):`, error);
            window.notificationManager.show(`操作失败: ${error.message}`, 'danger');
        }
    }

    /**
     * 下载任务结果
     */
    async downloadTask(taskId) {
        const url = `/api/files/${taskId}/result`;
        window.Bili2Text.Utils.downloadFile(url, `task_${taskId}_result.txt`);
        window.notificationManager.show('开始下载文件', 'success');
    }

    /**
     * 显示任务详情
     */
    async showTaskDetail(taskId) {
        const response = await window.apiClient.get(`/tasks/${taskId}`);
        if (response.success) {
            this.showTaskDetailModal(response.data);
        }
    }

    /**
     * 重试任务
     */
    async retryTask(taskId) {
        // 获取原任务信息
        const response = await window.apiClient.get(`/tasks/${taskId}`);
        if (response.success) {
            const originalTask = response.data;
            
            // 创建新任务
            const newTaskData = {
                url: originalTask.url,
                model_name: originalTask.model_name,
                options: originalTask.options || {}
            };
            
            const createResponse = await window.apiClient.post('/tasks/', newTaskData);
            if (createResponse.success) {
                window.notificationManager.show('任务重试成功', 'success');
                this.loadTasks();
            }
        }
    }

    /**
     * 取消任务
     */
    async cancelTask(taskId) {
        const response = await window.apiClient.post(`/tasks/${taskId}/cancel`);
        if (response.success) {
            window.notificationManager.show('任务已取消', 'warning');
            this.loadTasks();
        }
    }

    /**
     * 删除任务
     */
    async deleteTask(taskId) {
        if (!confirm('确定要删除这个任务吗？此操作不可恢复。')) {
            return;
        }

        const response = await window.apiClient.delete(`/tasks/${taskId}`);
        if (response.success) {
            window.notificationManager.show('任务已删除', 'success');
            this.loadTasks();
        }
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
                            <tr><td>任务ID</td><td>${task.id}</td></tr>
                            <tr><td>状态</td><td><span class="badge bg-${this.getStatusColor(task.status)}">${this.getStatusText(task.status)}</span></td></tr>
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
     * 应用筛选
     */
    applyFilters() {
        this.filters.status = document.getElementById('statusFilter').value;
        this.filters.timeRange = document.getElementById('timeFilter').value;
        this.filters.search = document.getElementById('searchInput').value.trim();
        
        this.currentPage = 1;
        this.loadTasks();
    }

    /**
     * 更新批量操作显示
     */
    updateBatchActions() {
        const batchActions = document.getElementById('batchActions');
        const selectedCount = document.getElementById('selectedCount');
        
        if (batchActions && selectedCount) {
            if (this.selectedTasks.size > 0) {
                batchActions.style.display = 'block';
                selectedCount.textContent = this.selectedTasks.size;
            } else {
                batchActions.style.display = 'none';
            }
        }
    }

    /**
     * 批量下载
     */
    async batchDownload() {
        if (this.selectedTasks.size === 0) return;

        for (const taskId of this.selectedTasks) {
            try {
                await this.downloadTask(taskId);
            } catch (error) {
                console.error(`下载任务 ${taskId} 失败:`, error);
            }
        }
        
        window.notificationManager.show(`开始下载 ${this.selectedTasks.size} 个文件`, 'success');
    }

    /**
     * 批量删除
     */
    async batchDelete() {
        if (this.selectedTasks.size === 0) return;

        if (!confirm(`确定要删除选中的 ${this.selectedTasks.size} 个任务吗？此操作不可恢复。`)) {
            return;
        }

        let successCount = 0;
        for (const taskId of this.selectedTasks) {
            try {
                const response = await window.apiClient.delete(`/tasks/${taskId}`);
                if (response.success) {
                    successCount++;
                }
            } catch (error) {
                console.error(`删除任务 ${taskId} 失败:`, error);
            }
        }

        window.notificationManager.show(`成功删除 ${successCount} 个任务`, 'success');
        this.clearSelection();
        this.loadTasks();
    }

    /**
     * 清空选择
     */
    clearSelection() {
        this.selectedTasks.clear();
        document.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });
        this.updateBatchActions();
    }

    /**
     * 清空历史
     */
    async clearHistory() {
        if (!confirm('确定要清空所有历史记录吗？此操作不可恢复。')) {
            return;
        }

        try {
            // 这里需要后端提供清空历史的API
            window.notificationManager.show('历史记录清空功能开发中...', 'info');
        } catch (error) {
            console.error('清空历史失败:', error);
            window.notificationManager.show(`清空失败: ${error.message}`, 'danger');
        }
    }

    /**
     * 更新分页
     */
    updatePagination(data) {
        const pagination = document.getElementById('pagination');
        if (!pagination) return;

        this.totalPages = Math.ceil(data.total / this.pageSize);
        
        if (this.totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let paginationHtml = '';
        
        // 上一页
        paginationHtml += `
            <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${this.currentPage - 1}">上一页</a>
            </li>
        `;

        // 页码
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(this.totalPages, this.currentPage + 2);

        if (startPage > 1) {
            paginationHtml += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
            if (startPage > 2) {
                paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            paginationHtml += `
                <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }

        if (endPage < this.totalPages) {
            if (endPage < this.totalPages - 1) {
                paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            paginationHtml += `<li class="page-item"><a class="page-link" href="#" data-page="${this.totalPages}">${this.totalPages}</a></li>`;
        }

        // 下一页
        paginationHtml += `
            <li class="page-item ${this.currentPage === this.totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${this.currentPage + 1}">下一页</a>
            </li>
        `;

        pagination.innerHTML = paginationHtml;

        // 绑定分页事件
        pagination.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(e.target.dataset.page);
                if (page && page !== this.currentPage && page >= 1 && page <= this.totalPages) {
                    this.currentPage = page;
                    this.loadTasks();
                }
            });
        });
    }

    /**
     * 获取状态颜色
     */
    getStatusColor(status) {
        const colors = {
            'pending': 'secondary',
            'downloading': 'info',
            'transcribing': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'dark'
        };
        return colors[status] || 'secondary';
    }

    /**
     * 获取状态图标
     */
    getStatusIcon(status) {
        const icons = {
            'pending': 'fas fa-clock',
            'downloading': 'fas fa-download',
            'transcribing': 'fas fa-microphone',
            'completed': 'fas fa-check',
            'failed': 'fas fa-times',
            'cancelled': 'fas fa-ban'
        };
        return icons[status] || 'fas fa-question';
    }

    /**
     * 获取状态文本
     */
    getStatusText(status) {
        const texts = {
            'pending': '等待中',
            'downloading': '下载中',
            'transcribing': '转录中',
            'completed': '已完成',
            'failed': '失败',
            'cancelled': '已取消'
        };
        return texts[status] || status;
    }
}

// 导出到全局
window.HistoryManager = HistoryManager; 