#!/bin/bash
# Bili2Text CLI 启动脚本

# 设置conda路径
export PATH="$HOME/miniconda3/bin:$PATH"

# 使用conda环境运行命令
conda run -n bili2text-cli python -m cli.main "$@"