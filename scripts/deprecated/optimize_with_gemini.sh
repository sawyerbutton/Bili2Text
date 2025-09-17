#!/bin/bash
# Gemini 文档优化脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 默认值
INPUT_DIR="storage/results/expert_optimized"
OUTPUT_DIR="storage/results/gemini_optimized"
CONFIG_FILE="config/gemini_config.json"

# 显示帮助
show_help() {
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -i, --input DIR     输入目录或文件 (默认: $INPUT_DIR)"
    echo "  -o, --output DIR    输出目录 (默认: $OUTPUT_DIR)"
    echo "  -k, --key KEY       Gemini API密钥"
    echo "  -c, --config FILE   配置文件路径 (默认: $CONFIG_FILE)"
    echo "  -t, --test          运行测试"
    echo "  -h, --help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -i input.md -o output.md -k YOUR_API_KEY"
    echo "  $0 -i storage/results -o storage/optimized"
    echo "  $0 --test"
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--input)
            INPUT_DIR="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -k|--key)
            export GEMINI_API_KEY="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -t|--test)
            RUN_TEST=1
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}错误: 未知选项 $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 运行测试
if [ "$RUN_TEST" = "1" ]; then
    echo -e "${GREEN}运行测试...${NC}"
    python scripts/optimize/test_gemini_optimizer.py
    exit $?
fi

# 检查API密钥
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${YELLOW}警告: 未设置 GEMINI_API_KEY${NC}"
    echo "请使用以下方式之一设置API密钥:"
    echo "  1. export GEMINI_API_KEY='your-key'"
    echo "  2. $0 -k YOUR_API_KEY"
    echo "  3. 编辑 $CONFIG_FILE"
    exit 1
fi

# 检查输入
if [ ! -e "$INPUT_DIR" ]; then
    echo -e "${RED}错误: 输入路径不存在: $INPUT_DIR${NC}"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 判断是单文件还是批量处理
if [ -f "$INPUT_DIR" ]; then
    # 单文件处理
    echo -e "${GREEN}优化单个文件...${NC}"
    echo "输入: $INPUT_DIR"
    echo "输出: $OUTPUT_DIR"

    python scripts/optimize/gemini_document_optimizer.py \
        "$INPUT_DIR" \
        -o "$OUTPUT_DIR" \
        --api-key "$GEMINI_API_KEY"
else
    # 批量处理
    echo -e "${GREEN}批量优化文档...${NC}"
    echo "输入目录: $INPUT_DIR"
    echo "输出目录: $OUTPUT_DIR"
    echo "配置文件: $CONFIG_FILE"

    # 统计文件数量
    FILE_COUNT=$(find "$INPUT_DIR" -name "*.md" -not -path "*optimized*" | wc -l)
    echo "找到 $FILE_COUNT 个待优化文件"

    if [ "$FILE_COUNT" -eq 0 ]; then
        echo -e "${YELLOW}没有找到待优化的文件${NC}"
        exit 0
    fi

    # 执行批量优化
    python scripts/optimize/gemini_batch_optimizer.py \
        "$INPUT_DIR" \
        -o "$OUTPUT_DIR" \
        -c "$CONFIG_FILE"
fi

# 检查结果
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 优化完成!${NC}"
    echo "结果保存在: $OUTPUT_DIR"

    # 显示统计信息
    if [ -d "$OUTPUT_DIR" ]; then
        OPTIMIZED_COUNT=$(find "$OUTPUT_DIR" -name "*optimized*.md" | wc -l)
        echo "已优化 $OPTIMIZED_COUNT 个文件"
    fi
else
    echo -e "${RED}❌ 优化失败!${NC}"
    exit 1
fi