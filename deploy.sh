#!/bin/bash

# Bili2Text Web 部署脚本
# 用于快速部署Docker化的应用

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p storage/audio
    mkdir -p storage/results
    mkdir -p storage/temp
    mkdir -p data
    mkdir -p webapp/logs
    mkdir -p nginx/logs
    
    log_success "目录创建完成"
}

# 复制环境变量文件
setup_env() {
    if [ ! -f .env ]; then
        log_info "创建环境变量文件..."
        cp env.example .env
        log_warning "请编辑 .env 文件配置您的环境变量"
    else
        log_info "环境变量文件已存在"
    fi
}

# 构建镜像
build_image() {
    log_info "构建Docker镜像..."
    docker-compose build --no-cache
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    docker-compose up -d
    log_success "服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 等待服务启动
    sleep 10
    
    # 检查容器状态
    if docker-compose ps | grep -q "Up"; then
        log_success "服务运行正常"
        
        # 显示服务信息
        echo ""
        log_info "服务访问信息:"
        echo "  Web界面: http://localhost"
        echo "  API文档: http://localhost/api"
        echo "  系统状态: http://localhost/api/system/status"
        echo ""
        
        # 显示容器状态
        docker-compose ps
    else
        log_error "服务启动失败"
        docker-compose logs
        exit 1
    fi
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务已停止"
}

# 清理数据
clean_data() {
    log_warning "这将删除所有数据，包括数据库和存储文件"
    read -p "确认删除? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "清理数据..."
        docker-compose down -v
        sudo rm -rf storage/* data/* webapp/logs/*
        log_success "数据清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 查看日志
show_logs() {
    local service=${1:-}
    
    if [ -n "$service" ]; then
        log_info "显示 $service 服务日志..."
        docker-compose logs -f "$service"
    else
        log_info "显示所有服务日志..."
        docker-compose logs -f
    fi
}

# 备份数据
backup_data() {
    local backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
    
    log_info "创建数据备份到 $backup_dir..."
    
    mkdir -p "$backup_dir"
    cp -r storage "$backup_dir/"
    cp -r data "$backup_dir/"
    cp .env "$backup_dir/" 2>/dev/null || true
    
    tar -czf "${backup_dir}.tar.gz" "$backup_dir"
    rm -rf "$backup_dir"
    
    log_success "备份完成: ${backup_dir}.tar.gz"
}

# 恢复数据
restore_data() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "请指定备份文件"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        exit 1
    fi
    
    log_warning "这将覆盖现有数据"
    read -p "确认恢复? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "恢复数据从 $backup_file..."
        
        # 停止服务
        docker-compose down
        
        # 解压备份
        tar -xzf "$backup_file"
        backup_dir=$(basename "$backup_file" .tar.gz)
        
        # 恢复数据
        cp -r "${backup_dir}/storage"/* storage/ 2>/dev/null || true
        cp -r "${backup_dir}/data"/* data/ 2>/dev/null || true
        cp "${backup_dir}/.env" . 2>/dev/null || true
        
        # 清理临时文件
        rm -rf "$backup_dir"
        
        log_success "数据恢复完成"
        
        # 重启服务
        start_services
    else
        log_info "取消恢复操作"
    fi
}

# 更新应用
update_app() {
    log_info "更新应用..."
    
    # 备份数据
    backup_data
    
    # 拉取最新代码
    git pull
    
    # 重新构建和启动
    docker-compose down
    build_image
    start_services
    
    log_success "应用更新完成"
}

# 显示帮助信息
show_help() {
    echo "Bili2Text Web 部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  deploy      完整部署应用（默认）"
    echo "  start       启动服务"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  status      查看服务状态"
    echo "  logs        查看日志 [服务名]"
    echo "  build       构建镜像"
    echo "  backup      备份数据"
    echo "  restore     恢复数据 <备份文件>"
    echo "  clean       清理所有数据"
    echo "  update      更新应用"
    echo "  help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 deploy           # 完整部署"
    echo "  $0 logs web         # 查看web服务日志"
    echo "  $0 restore backup.tar.gz  # 恢复备份"
}

# 主函数
main() {
    local command=${1:-deploy}
    
    case $command in
        deploy)
            check_docker
            create_directories
            setup_env
            build_image
            start_services
            check_services
            ;;
        start)
            start_services
            check_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            start_services
            check_services
            ;;
        status)
            docker-compose ps
            ;;
        logs)
            show_logs $2
            ;;
        build)
            build_image
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data $2
            ;;
        clean)
            clean_data
            ;;
        update)
            update_app
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 