# Bili2Text Web API 文档

## 📋 API概述

Bili2Text Web应用提供RESTful API和WebSocket接口，支持视频转录任务的完整生命周期管理。

## 🔐 认证方式

当前版本暂不需要认证，后续版本将支持：
- API Key认证
- JWT Token认证
- OAuth 2.0认证

## 📡 基础信息

- **Base URL**: `http://localhost:8000/api`
- **Content-Type**: `application/json`
- **响应格式**: JSON
- **字符编码**: UTF-8

## 🔄 任务管理API

### 创建转录任务

**POST** `/api/tasks/`

创建新的视频转录任务。

#### 请求参数
```json
{
  "url": "https://www.bilibili.com/video/BV15N4y1J7CA",
  "model_name": "medium",
  "options": {
    "use_proxy": false,
    "keep_audio": true,
    "output_format": "txt"
  }
}
```

#### 响应示例
```json
{
  "task_id": "task_20240115_143022_abc123",
  "status": "pending",
  "message": "任务创建成功",
  "created_at": "2024-01-15T14:30:22Z"
}
```

### 获取任务列表

**GET** `/api/tasks/`

获取所有任务的列表，支持分页和筛选。

#### 查询参数
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 20, 最大: 100)
- `status`: 任务状态筛选
- `date_from`: 开始日期 (YYYY-MM-DD)
- `date_to`: 结束日期 (YYYY-MM-DD)

#### 响应示例
```json
{
  "tasks": [
    {
      "task_id": "task_20240115_143022_abc123",
      "url": "https://www.bilibili.com/video/BV15N4y1J7CA",
      "status": "completed",
      "progress": 100,
      "created_at": "2024-01-15T14:30:22Z",
      "completed_at": "2024-01-15T14:35:45Z",
      "model_name": "medium",
      "file_size": 3145728,
      "duration": 180.5
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

### 获取任务详情

**GET** `/api/tasks/{task_id}`

获取指定任务的详细信息。

#### 响应示例
```json
{
  "task_id": "task_20240115_143022_abc123",
  "url": "https://www.bilibili.com/video/BV15N4y1J7CA",
  "status": "completed",
  "progress": 100,
  "created_at": "2024-01-15T14:30:22Z",
  "started_at": "2024-01-15T14:30:25Z",
  "completed_at": "2024-01-15T14:35:45Z",
  "model_name": "medium",
  "file_size": 3145728,
  "duration": 180.5,
  "result_file_path": "/storage/results/task_20240115_143022_abc123/result.txt",
  "audio_file_path": "/storage/audio/task_20240115_143022_abc123/audio.m4a",
  "video_info": {
    "title": "【参考信息第123期】某某视频标题",
    "author": "UP主名称",
    "duration": 180.5,
    "view_count": 12345
  }
}
```

### 取消任务

**POST** `/api/tasks/{task_id}/cancel`

取消正在执行或等待中的任务。

#### 响应示例
```json
{
  "task_id": "task_20240115_143022_abc123",
  "status": "cancelled",
  "message": "任务已取消"
}
```

### 删除任务

**DELETE** `/api/tasks/{task_id}`

删除任务及其相关文件。

#### 响应示例
```json
{
  "message": "任务删除成功",
  "deleted_files": [
    "/storage/results/task_20240115_143022_abc123/result.txt",
    "/storage/audio/task_20240115_143022_abc123/audio.m4a"
  ]
}
```

## 📁 文件操作API

### 下载转录结果

**GET** `/api/files/{task_id}/result`

下载任务的转录结果文件。

#### 响应
- **Content-Type**: `text/plain; charset=utf-8`
- **Content-Disposition**: `attachment; filename="result.txt"`

### 下载音频文件

**GET** `/api/files/{task_id}/audio`

下载任务的音频文件。

#### 响应
- **Content-Type**: `audio/mp4`
- **Content-Disposition**: `attachment; filename="audio.m4a"`

### 删除任务文件

**DELETE** `/api/files/{task_id}`

删除任务的所有相关文件。

#### 响应示例
```json
{
  "message": "文件删除成功",
  "deleted_files": [
    "/storage/results/task_20240115_143022_abc123/result.txt",
    "/storage/audio/task_20240115_143022_abc123/audio.m4a"
  ]
}
```

## 📊 系统状态API

### 获取系统状态

**GET** `/api/system/status`

获取系统当前状态信息。

#### 响应示例
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime": 86400,
  "tasks": {
    "total": 150,
    "pending": 2,
    "running": 1,
    "completed": 145,
    "failed": 2
  },
  "system": {
    "cpu_usage": 45.2,
    "memory_usage": 68.5,
    "disk_usage": 23.1,
    "gpu_available": true,
    "gpu_memory_usage": 34.7
  },
  "workers": {
    "active": 3,
    "total": 3
  }
}
```

### 获取可用模型

**GET** `/api/system/models`

获取系统支持的Whisper模型列表。

#### 响应示例
```json
{
  "models": [
    {
      "name": "tiny",
      "size": "39MB",
      "speed": "very_fast",
      "accuracy": "low",
      "memory_required": "1GB",
      "recommended_for": "快速测试、实时转录"
    },
    {
      "name": "medium",
      "size": "769MB",
      "speed": "medium",
      "accuracy": "high",
      "memory_required": "5GB",
      "recommended_for": "推荐使用，质量优先",
      "default": true
    }
  ]
}
```

### 获取统计信息

**GET** `/api/system/stats`

获取系统使用统计信息。

#### 查询参数
- `period`: 统计周期 (day/week/month, 默认: day)

#### 响应示例
```json
{
  "period": "day",
  "date": "2024-01-15",
  "stats": {
    "tasks_created": 25,
    "tasks_completed": 23,
    "tasks_failed": 1,
    "total_processing_time": 3600,
    "total_audio_duration": 7200,
    "total_file_size": 1073741824,
    "average_processing_speed": 2.0,
    "model_usage": {
      "tiny": 5,
      "base": 8,
      "medium": 10,
      "large-v3": 2
    }
  }
}
```

## 🔌 WebSocket API

### 任务状态更新

**WebSocket** `/ws/tasks/{task_id}`

实时接收指定任务的状态更新。

#### 连接示例
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/tasks/task_20240115_143022_abc123');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('任务更新:', data);
};
```

#### 消息格式
```json
{
  "type": "task_update",
  "task_id": "task_20240115_143022_abc123",
  "status": "transcribing",
  "progress": 45.5,
  "message": "正在转录音频...",
  "timestamp": "2024-01-15T14:32:15Z"
}
```

### 系统状态更新

**WebSocket** `/ws/system`

实时接收系统状态更新。

#### 消息格式
```json
{
  "type": "system_update",
  "data": {
    "active_tasks": 3,
    "cpu_usage": 67.2,
    "memory_usage": 71.8,
    "timestamp": "2024-01-15T14:32:15Z"
  }
}
```

## ❌ 错误处理

### 错误响应格式

所有API错误都遵循统一的响应格式：

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "指定的任务不存在",
    "details": {
      "task_id": "invalid_task_id"
    }
  },
  "timestamp": "2024-01-15T14:30:22Z"
}
```

### 常见错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| `INVALID_URL` | 400 | 无效的视频URL |
| `UNSUPPORTED_SITE` | 400 | 不支持的视频网站 |
| `INVALID_MODEL` | 400 | 无效的模型名称 |
| `TASK_NOT_FOUND` | 404 | 任务不存在 |
| `FILE_NOT_FOUND` | 404 | 文件不存在 |
| `TASK_ALREADY_RUNNING` | 409 | 任务已在运行中 |
| `SYSTEM_OVERLOAD` | 503 | 系统负载过高 |
| `DOWNLOAD_FAILED` | 500 | 视频下载失败 |
| `TRANSCRIPTION_FAILED` | 500 | 转录处理失败 |

## 📝 使用示例

### Python客户端示例

```python
import requests
import websocket
import json

# 创建任务
def create_task(url, model="medium"):
    response = requests.post(
        "http://localhost:8000/api/tasks/",
        json={
            "url": url,
            "model_name": model,
            "options": {
                "keep_audio": True
            }
        }
    )
    return response.json()

# 监听任务状态
def on_message(ws, message):
    data = json.loads(message)
    print(f"任务状态: {data['status']}, 进度: {data['progress']}%")

def monitor_task(task_id):
    ws = websocket.WebSocketApp(
        f"ws://localhost:8000/ws/tasks/{task_id}",
        on_message=on_message
    )
    ws.run_forever()

# 使用示例
task = create_task("https://www.bilibili.com/video/BV15N4y1J7CA")
print(f"任务创建成功: {task['task_id']}")
monitor_task(task['task_id'])
```

### JavaScript客户端示例

```javascript
// 创建任务
async function createTask(url, model = 'medium') {
    const response = await fetch('/api/tasks/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url: url,
            model_name: model,
            options: {
                keep_audio: true
            }
        })
    });
    return await response.json();
}

// 监听任务状态
function monitorTask(taskId) {
    const ws = new WebSocket(`ws://localhost:8000/ws/tasks/${taskId}`);
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateTaskProgress(data.progress);
        updateTaskStatus(data.status);
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket错误:', error);
    };
}

// 下载结果文件
function downloadResult(taskId) {
    window.open(`/api/files/${taskId}/result`, '_blank');
}
```

## 🔄 版本控制

API版本通过URL路径进行管理：
- `v1`: `/api/v1/tasks/` (当前版本)
- `v2`: `/api/v2/tasks/` (未来版本)

当前文档对应API版本：**v1.0.0**

## 📞 技术支持

如有API使用问题，请通过以下方式联系：
- GitHub Issues: [项目Issues页面]
- 邮件支持: [技术支持邮箱]
- 文档反馈: [文档仓库]