"""
后端错误处理中间件
统一处理异常和错误响应
"""

import logging
import traceback
import uuid
from datetime import datetime
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

class ErrorCode:
    """错误代码常量"""
    # 通用错误
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    
    # 认证错误
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    
    # 业务错误
    INVALID_URL = "INVALID_URL"
    INVALID_MODEL = "INVALID_MODEL"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    SYSTEM_OVERLOAD = "SYSTEM_OVERLOAD"
    
    # 文件错误
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    
    # 数据库错误
    DATABASE_ERROR = "DATABASE_ERROR"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"
    
    # 网络错误
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

class BusinessException(Exception):
    """业务异常基类"""
    
    def __init__(self, code, message, details=None, status_code=400):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code
        super().__init__(message)

class ValidationException(BusinessException):
    """验证异常"""
    
    def __init__(self, message, field=None, details=None):
        super().__init__(
            ErrorCode.VALIDATION_ERROR,
            message,
            details or {'field': field} if field else None,
            400
        )

class NotFoundException(BusinessException):
    """资源不存在异常"""
    
    def __init__(self, resource_type, resource_id=None):
        message = f"{resource_type}不存在"
        if resource_id:
            message += f": {resource_id}"
        
        super().__init__(
            f"{resource_type.upper()}_NOT_FOUND",
            message,
            {'resource_type': resource_type, 'resource_id': resource_id},
            404
        )

class SystemOverloadException(BusinessException):
    """系统过载异常"""
    
    def __init__(self, message="系统负载过高，请稍后重试"):
        super().__init__(
            ErrorCode.SYSTEM_OVERLOAD,
            message,
            None,
            503
        )

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化应用"""
        app.errorhandler(Exception)(self.handle_exception)
        app.errorhandler(HTTPException)(self.handle_http_exception)
        app.errorhandler(BusinessException)(self.handle_business_exception)
        
        # 注册错误日志记录
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """请求前处理"""
        # 记录请求信息
        request.start_time = datetime.utcnow()
        request.error_id = str(uuid.uuid4())
        
        # 记录请求日志
        logger.info(f"Request started: {request.method} {request.url}", extra={
            'request_id': request.error_id,
            'method': request.method,
            'url': request.url,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        })
    
    def after_request(self, response):
        """请求后处理"""
        if hasattr(request, 'start_time'):
            duration = (datetime.utcnow() - request.start_time).total_seconds()
            
            # 记录响应日志
            logger.info(f"Request completed: {response.status_code}", extra={
                'request_id': getattr(request, 'error_id', 'unknown'),
                'status_code': response.status_code,
                'duration': duration
            })
        
        return response
    
    def handle_exception(self, error):
        """处理通用异常"""
        error_id = getattr(request, 'error_id', str(uuid.uuid4()))
        
        # 记录错误日志
        logger.error(f"Unhandled exception: {str(error)}", extra={
            'request_id': error_id,
            'error_type': type(error).__name__,
            'traceback': traceback.format_exc()
        })
        
        # 返回通用错误响应
        return self.create_error_response(
            ErrorCode.INTERNAL_ERROR,
            "服务器内部错误",
            error_id=error_id,
            status_code=500
        )
    
    def handle_http_exception(self, error):
        """处理HTTP异常"""
        error_id = getattr(request, 'error_id', str(uuid.uuid4()))
        
        # 记录HTTP错误
        logger.warning(f"HTTP exception: {error.code} {error.name}", extra={
            'request_id': error_id,
            'status_code': error.code,
            'description': error.description
        })
        
        # 映射HTTP状态码到错误代码
        error_code_map = {
            400: ErrorCode.VALIDATION_ERROR,
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.TASK_NOT_FOUND,
            429: ErrorCode.SYSTEM_OVERLOAD,
            500: ErrorCode.INTERNAL_ERROR,
            503: ErrorCode.SERVICE_UNAVAILABLE
        }
        
        error_code = error_code_map.get(error.code, ErrorCode.UNKNOWN_ERROR)
        
        return self.create_error_response(
            error_code,
            error.description or error.name,
            error_id=error_id,
            status_code=error.code
        )
    
    def handle_business_exception(self, error):
        """处理业务异常"""
        error_id = getattr(request, 'error_id', str(uuid.uuid4()))
        
        # 记录业务错误
        logger.warning(f"Business exception: {error.code} {error.message}", extra={
            'request_id': error_id,
            'error_code': error.code,
            'details': error.details
        })
        
        return self.create_error_response(
            error.code,
            error.message,
            details=error.details,
            error_id=error_id,
            status_code=error.status_code
        )
    
    def create_error_response(self, code, message, details=None, error_id=None, status_code=400):
        """创建错误响应"""
        response_data = {
            'success': False,
            'error': {
                'code': code,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        if details:
            response_data['error']['details'] = details
        
        if error_id:
            response_data['error']['error_id'] = error_id
        
        # 在开发模式下添加调试信息
        if current_app.debug and hasattr(request, 'error_id'):
            response_data['debug'] = {
                'request_id': request.error_id,
                'endpoint': request.endpoint,
                'method': request.method,
                'url': request.url
            }
        
        return jsonify(response_data), status_code

def handle_database_error(func):
    """数据库错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 检查是否为数据库相关错误
            error_message = str(e).lower()
            if any(keyword in error_message for keyword in ['database', 'sql', 'constraint', 'integrity']):
                logger.error(f"Database error in {func.__name__}: {str(e)}")
                raise BusinessException(
                    ErrorCode.DATABASE_ERROR,
                    "数据库操作失败",
                    {'original_error': str(e)},
                    500
                )
            else:
                raise
    return wrapper

def handle_file_operation_error(func):
    """文件操作错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            raise NotFoundException("文件")
        except PermissionError:
            raise BusinessException(
                ErrorCode.FORBIDDEN,
                "文件访问权限不足",
                status_code=403
            )
        except OSError as e:
            logger.error(f"File operation error in {func.__name__}: {str(e)}")
            raise BusinessException(
                ErrorCode.INTERNAL_ERROR,
                "文件操作失败",
                {'original_error': str(e)},
                500
            )
    return wrapper

def validate_request_data(required_fields=None, optional_fields=None):
    """请求数据验证装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                raise ValidationException("请求必须包含JSON数据")
            
            data = request.get_json()
            if not data:
                raise ValidationException("请求数据不能为空")
            
            # 验证必需字段
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    raise ValidationException(
                        f"缺少必需字段: {', '.join(missing_fields)}",
                        details={'missing_fields': missing_fields}
                    )
            
            # 验证字段类型（如果提供了可选字段定义）
            if optional_fields:
                for field, field_type in optional_fields.items():
                    if field in data and data[field] is not None:
                        if not isinstance(data[field], field_type):
                            raise ValidationException(
                                f"字段 {field} 类型错误，期望 {field_type.__name__}",
                                field=field
                            )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limit_error_handler(func):
    """速率限制错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if 'rate limit' in str(e).lower():
                raise SystemOverloadException("请求过于频繁，请稍后重试")
            else:
                raise
    return wrapper

# 创建全局错误处理器实例
error_handler = ErrorHandler() 