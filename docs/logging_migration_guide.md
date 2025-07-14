# 日志和错误处理系统迁移指南

本指南说明如何将现有代码迁移到新的统一日志和错误处理系统。

## 目录

1. [概述](#概述)
2. [日志系统迁移](#日志系统迁移)
3. [错误处理迁移](#错误处理迁移)
4. [装饰器使用](#装饰器使用)
5. [最佳实践](#最佳实践)
6. [迁移示例](#迁移示例)

## 概述

新的日志和错误处理系统提供了：
- 统一的日志格式和颜色输出
- 分级日志管理（DEBUG/INFO/WARNING/ERROR/CRITICAL）
- 自定义异常层次结构
- 错误重试机制
- 错误收集和批量处理
- 执行时间记录

## 日志系统迁移

### 1. 替换print语句

**旧代码：**
```python
print(f"开始下载: {url}")
print(f"下载失败 {url}: {e}")
```

**新代码：**
```python
from .logger import get_logger

class MyClass:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def download(self, url):
        self.logger.info(f"开始下载: {url}")
        self.logger.error(f"下载失败 {url}: {e}", exc_info=True)
```

### 2. 日志级别选择

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息，确认程序按预期运行
- **WARNING**: 警告信息，程序仍可运行但可能有问题
- **ERROR**: 错误信息，某些功能无法执行
- **CRITICAL**: 严重错误，程序可能无法继续运行

### 3. 结构化日志

使用`extra`参数添加结构化数据：

```python
self.logger.info(
    "批量下载完成",
    extra={
        "success": success_count,
        "failed": failed_count,
        "total": total_count,
        "duration": elapsed_time
    }
)
```

### 4. 日志上下文

使用`LogContext`添加临时上下文信息：

```python
from .logger import LogContext

with LogContext(self.logger, request_id="12345", user_id="user001"):
    # 这个块内的所有日志都会包含request_id和user_id
    self.logger.info("处理用户请求")
```

## 错误处理迁移

### 1. 使用自定义异常

**旧代码：**
```python
if not url:
    raise ValueError("URL不能为空")

if response.status_code == 404:
    raise Exception(f"视频未找到: {video_id}")
```

**新代码：**
```python
from .exceptions import URLValidationError, VideoNotFoundError

if not url:
    raise URLValidationError(url)

if response.status_code == 404:
    raise VideoNotFoundError(video_id)
```

### 2. 异常转换

将第三方库的异常转换为自定义异常：

```python
try:
    await downloader.get_video(url)
except Exception as e:
    if "404" in str(e):
        raise VideoNotFoundError(url) from e
    elif "timeout" in str(e).lower():
        raise NetworkError(f"网络超时: {e}") from e
    else:
        raise DownloadError(f"下载失败: {e}") from e
```

### 3. 错误收集

批量操作时使用`ErrorCollector`：

```python
from .error_handler import ErrorCollector

error_collector = ErrorCollector(logger_name=__name__)

for item in items:
    with error_collector:  # 自动捕获并收集错误
        process_item(item)

# 检查是否有错误
if error_collector.has_errors():
    self.logger.warning(f"处理过程中有 {len(error_collector.get_errors())} 个错误")
```

## 装饰器使用

### 1. 错误处理装饰器

```python
from .error_handler import error_handler

@error_handler(
    exceptions=(NetworkError, DownloadError),  # 要捕获的异常
    default_return=False,                      # 出错时的返回值
    raise_on_error=False,                      # 是否重新抛出
    error_message="下载操作失败"                # 自定义错误消息
)
def download_file(self, url: str) -> bool:
    # 函数实现
    pass
```

### 2. 重试装饰器

```python
from .exceptions import retry_on_error

@retry_on_error(
    exceptions=(NetworkError,),
    max_retries=3,
    delay=2.0,
    backoff=2.0
)
async def fetch_data(self, url: str):
    # 网络请求实现
    pass
```

### 3. 执行时间记录

```python
from .logger import log_execution_time

@log_execution_time()
async def process_batch(self, items: List[Any]):
    # 批处理实现
    pass
```

### 4. 优雅关闭

```python
from .error_handler import graceful_shutdown

def cleanup():
    # 清理资源
    pass

@graceful_shutdown(cleanup_func=cleanup)
def main():
    # 主程序
    pass
```

## 最佳实践

### 1. 日志记录原则

- 在类初始化时创建logger实例
- 使用适当的日志级别
- 包含足够的上下文信息
- 避免在循环中记录过多日志
- 敏感信息不要记录到日志

### 2. 错误处理原则

- 使用具体的异常类型而不是通用Exception
- 在异常中包含有用的调试信息
- 使用异常链（from e）保留原始错误信息
- 在适当的层级处理异常
- 记录错误时使用`exc_info=True`

### 3. 性能考虑

- 使用`logger.isEnabledFor(logging.DEBUG)`检查日志级别
- 避免在日志消息中进行昂贵的字符串格式化
- 批量操作使用ErrorCollector而不是单独try-except

## 迁移示例

### 完整的类迁移示例

**原始代码：**
```python
class VideoProcessor:
    def __init__(self):
        pass
    
    def process(self, video_id):
        print(f"Processing video: {video_id}")
        try:
            # 处理逻辑
            result = self._download(video_id)
            print(f"Download complete: {result}")
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
```

**迁移后的代码：**
```python
from .logger import get_logger, log_execution_time
from .exceptions import VideoNotFoundError, ProcessingError
from .error_handler import error_handler

class VideoProcessor:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.info("VideoProcessor初始化")
    
    @log_execution_time()
    @error_handler(
        exceptions=(ProcessingError,),
        default_return=None,
        raise_on_error=False
    )
    def process(self, video_id: str):
        self.logger.info(
            "开始处理视频",
            extra={"video_id": video_id}
        )
        
        try:
            result = self._download(video_id)
            self.logger.info(
                "视频处理完成",
                extra={
                    "video_id": video_id,
                    "result": result
                }
            )
            return result
        except VideoNotFoundError:
            self.logger.warning(f"视频未找到: {video_id}")
            raise
        except Exception as e:
            raise ProcessingError(
                f"处理视频失败: {video_id}",
                details={"video_id": video_id, "error": str(e)}
            ) from e
```

### 批处理迁移示例

```python
from .error_handler import ErrorCollector

async def batch_process(self, items: List[str]):
    """批量处理示例"""
    error_collector = ErrorCollector(logger_name=__name__)
    results = []
    
    self.logger.info(f"开始批量处理 {len(items)} 个项目")
    
    for item in items:
        with error_collector:
            result = await self.process_item(item)
            results.append(result)
    
    # 汇总结果
    if error_collector.has_errors():
        self.logger.warning(
            f"批处理完成，但有错误",
            extra={
                "total": len(items),
                "success": len(results),
                "errors": len(error_collector.get_errors())
            }
        )
    else:
        self.logger.info(f"批处理成功完成，处理了 {len(results)} 个项目")
    
    return results
```

## 配置日志系统

在应用启动时配置日志系统：

```python
from bili2text_v2.core import init_logger, set_log_level
from bili2text_v2.config import get_config

# 初始化日志系统
init_logger()

# 动态调整日志级别
if debug_mode:
    set_log_level("DEBUG")
else:
    set_log_level("INFO")
```

## 总结

迁移到新的日志和错误处理系统能够：
1. 提供一致的日志格式和错误处理方式
2. 更容易调试和追踪问题
3. 自动记录执行时间和性能指标
4. 优雅地处理批量操作中的错误
5. 支持结构化日志便于后续分析

按照本指南逐步迁移代码，可以显著提升代码的可维护性和可靠性。