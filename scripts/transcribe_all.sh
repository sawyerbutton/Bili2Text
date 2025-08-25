#!/bin/bash
# 便捷的批量转写脚本 - 自动使用GPU转写所有视频

echo "======================================"
echo "   Bili2Text GPU批量转写工具"
echo "======================================"
echo ""

# 检查conda环境
if ! conda info --envs | grep -q "bili2text-gpu"; then
    echo "❌ 错误: 未找到 bili2text-gpu conda环境"
    echo "请先运行: conda create -n bili2text-gpu python=3.11"
    echo "然后安装依赖: conda activate bili2text-gpu && pip install torch whisper"
    exit 1
fi

# 统计视频文件
video_count=$(find storage/video -name "*.mp4" -o -name "*.mkv" | wc -l)
completed_count=$(find storage/results/gpu_transcripts -name "*.txt" 2>/dev/null | wc -l)

echo "📊 视频统计:"
echo "   总数: $video_count 个视频"
echo "   已完成: $completed_count 个"
echo "   待处理: $((video_count - completed_count)) 个"
echo ""

if [ $video_count -eq $completed_count ]; then
    echo "✅ 所有视频都已转写完成！"
    echo "   结果位置: storage/results/gpu_transcripts/"
    exit 0
fi

echo "🚀 开始批量转写..."
echo "   使用GPU加速"
echo "   支持断点续传"
echo ""

# 执行转写脚本
./transcribe/stable_transcribe.sh

echo ""
echo "✅ 批量转写完成！"
echo "   结果保存在: storage/results/gpu_transcripts/"