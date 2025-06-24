# Bili2Text Web Windows部署脚本
# PowerShell版本

param(
    [Parameter(Position=0)]
    [string]$Command = "deploy",
    
    [Parameter(Position=1)]
    [string]$Service = "",
    
    [Parameter(Position=2)]
    [string]$BackupFile = ""
)

# 颜色函数
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# 检查Docker是否安装
function Test-Docker {
    try {
        $null = Get-Command docker -ErrorAction Stop
        $null = Get-Command docker-compose -ErrorAction Stop
        Write-Success "Docker环境检查通过"
        return $true
    }
    catch {
        Write-Error "Docker或Docker Compose未安装，请先安装"
        return $false
    }
}

# 创建必要的目录
function New-Directories {
    Write-Info "创建必要的目录..."
    
    $directories = @(
        "storage\audio",
        "storage\results", 
        "storage\temp",
        "data",
        "webapp\logs",
        "nginx\logs"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "目录创建完成"
}

# 设置环境变量
function Set-Environment {
    if (!(Test-Path ".env")) {
        Write-Info "创建环境变量文件..."
        Copy-Item "env.example" ".env"
        Write-Warning "请编辑 .env 文件配置您的环境变量"
    }
    else {
        Write-Info "环境变量文件已存在"
    }
}

# 构建镜像
function Build-Image {
    Write-Info "构建Docker镜像..."
    docker-compose build --no-cache
    if ($LASTEXITCODE -eq 0) {
        Write-Success "镜像构建完成"
    }
    else {
        Write-Error "镜像构建失败"
        exit 1
    }
}

# 启动服务
function Start-Services {
    Write-Info "启动服务..."
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Success "服务启动完成"
    }
    else {
        Write-Error "服务启动失败"
        exit 1
    }
}

# 检查服务状态
function Test-Services {
    Write-Info "检查服务状态..."
    
    # 等待服务启动
    Start-Sleep -Seconds 10
    
    # 检查容器状态
    $status = docker-compose ps
    if ($status -match "Up") {
        Write-Success "服务运行正常"
        
        # 显示服务信息
        Write-Host ""
        Write-Info "服务访问信息:"
        Write-Host "  Web界面: http://localhost"
        Write-Host "  API文档: http://localhost/api"
        Write-Host "  系统状态: http://localhost/api/system/status"
        Write-Host ""
        
        # 显示容器状态
        docker-compose ps
    }
    else {
        Write-Error "服务启动失败"
        docker-compose logs
        exit 1
    }
}

# 停止服务
function Stop-Services {
    Write-Info "停止服务..."
    docker-compose down
    if ($LASTEXITCODE -eq 0) {
        Write-Success "服务已停止"
    }
}

# 清理数据
function Clear-Data {
    Write-Warning "这将删除所有数据，包括数据库和存储文件"
    $confirm = Read-Host "确认删除? (y/N)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Info "清理数据..."
        docker-compose down -v
        
        if (Test-Path "storage") {
            Remove-Item -Path "storage\*" -Recurse -Force
        }
        if (Test-Path "data") {
            Remove-Item -Path "data\*" -Recurse -Force
        }
        if (Test-Path "webapp\logs") {
            Remove-Item -Path "webapp\logs\*" -Recurse -Force
        }
        
        Write-Success "数据清理完成"
    }
    else {
        Write-Info "取消清理操作"
    }
}

# 查看日志
function Show-Logs {
    param([string]$ServiceName)
    
    if ($ServiceName) {
        Write-Info "显示 $ServiceName 服务日志..."
        docker-compose logs -f $ServiceName
    }
    else {
        Write-Info "显示所有服务日志..."
        docker-compose logs -f
    }
}

# 备份数据
function Backup-Data {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "backup_$timestamp"
    
    Write-Info "创建数据备份到 $backupDir..."
    
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    if (Test-Path "storage") {
        Copy-Item -Path "storage" -Destination "$backupDir\" -Recurse
    }
    if (Test-Path "data") {
        Copy-Item -Path "data" -Destination "$backupDir\" -Recurse
    }
    if (Test-Path ".env") {
        Copy-Item -Path ".env" -Destination "$backupDir\"
    }
    
    # 创建压缩包
    Compress-Archive -Path $backupDir -DestinationPath "$backupDir.zip"
    Remove-Item -Path $backupDir -Recurse -Force
    
    Write-Success "备份完成: $backupDir.zip"
}

# 恢复数据
function Restore-Data {
    param([string]$BackupFile)
    
    if (!$BackupFile) {
        Write-Error "请指定备份文件"
        return
    }
    
    if (!(Test-Path $BackupFile)) {
        Write-Error "备份文件不存在: $BackupFile"
        return
    }
    
    Write-Warning "这将覆盖现有数据"
    $confirm = Read-Host "确认恢复? (y/N)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Info "恢复数据从 $BackupFile..."
        
        # 停止服务
        docker-compose down
        
        # 解压备份
        $backupDir = [System.IO.Path]::GetFileNameWithoutExtension($BackupFile)
        Expand-Archive -Path $BackupFile -DestinationPath "." -Force
        
        # 恢复数据
        if (Test-Path "$backupDir\storage") {
            Copy-Item -Path "$backupDir\storage\*" -Destination "storage\" -Recurse -Force
        }
        if (Test-Path "$backupDir\data") {
            Copy-Item -Path "$backupDir\data\*" -Destination "data\" -Recurse -Force
        }
        if (Test-Path "$backupDir\.env") {
            Copy-Item -Path "$backupDir\.env" -Destination "."
        }
        
        # 清理临时文件
        Remove-Item -Path $backupDir -Recurse -Force
        
        Write-Success "数据恢复完成"
        
        # 重启服务
        Start-Services
    }
    else {
        Write-Info "取消恢复操作"
    }
}

# 更新应用
function Update-App {
    Write-Info "更新应用..."
    
    # 备份数据
    Backup-Data
    
    # 拉取最新代码
    git pull
    
    # 重新构建和启动
    docker-compose down
    Build-Image
    Start-Services
    
    Write-Success "应用更新完成"
}

# 显示帮助信息
function Show-Help {
    Write-Host "Bili2Text Web Windows部署脚本"
    Write-Host ""
    Write-Host "用法: .\deploy.ps1 [命令] [参数]"
    Write-Host ""
    Write-Host "命令:"
    Write-Host "  deploy      完整部署应用（默认）"
    Write-Host "  start       启动服务"
    Write-Host "  stop        停止服务"
    Write-Host "  restart     重启服务"
    Write-Host "  status      查看服务状态"
    Write-Host "  logs        查看日志 [服务名]"
    Write-Host "  build       构建镜像"
    Write-Host "  backup      备份数据"
    Write-Host "  restore     恢复数据 <备份文件>"
    Write-Host "  clean       清理所有数据"
    Write-Host "  update      更新应用"
    Write-Host "  help        显示帮助信息"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\deploy.ps1 deploy           # 完整部署"
    Write-Host "  .\deploy.ps1 logs bili2text-web  # 查看web服务日志"
    Write-Host "  .\deploy.ps1 restore backup.zip  # 恢复备份"
}

# 主函数
function Main {
    switch ($Command.ToLower()) {
        "deploy" {
            if (!(Test-Docker)) { return }
            New-Directories
            Set-Environment
            Build-Image
            Start-Services
            Test-Services
        }
        "start" {
            Start-Services
            Test-Services
        }
        "stop" {
            Stop-Services
        }
        "restart" {
            Stop-Services
            Start-Services
            Test-Services
        }
        "status" {
            docker-compose ps
        }
        "logs" {
            Show-Logs $Service
        }
        "build" {
            Build-Image
        }
        "backup" {
            Backup-Data
        }
        "restore" {
            Restore-Data $BackupFile
        }
        "clean" {
            Clear-Data
        }
        "update" {
            Update-App
        }
        "help" {
            Show-Help
        }
        default {
            Write-Error "未知命令: $Command"
            Show-Help
        }
    }
}

# 执行主函数
Main 