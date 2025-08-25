#!/bin/bash
# 稳定的逐个文件转写脚本

echo "🔍 扫描待处理的视频文件..."

# 统计总数
total_count=$(find storage/video -name "*.mp4" | wc -l)
echo "📁 总共 $total_count 个视频文件"

# 统计已完成
completed_count=$(find storage/results/gpu_transcripts -name "*.txt" | wc -l)
echo "✅ 已完成 $completed_count 个"

# 计数器
processed=0
success=0
failed=0

# 遍历所有视频文件
find storage/video -name "*.mp4" | while read video_file; do
    # 获取相对路径
    rel_path=$(echo "$video_file" | sed 's|storage/video/||')
    
    # 生成输出文件名（移除特殊字符）
    output_name=$(basename "$video_file" .mp4 | sed 's/["\[\]【】（）：]//g')
    output_dir="storage/results/gpu_transcripts/$(dirname "$rel_path")"
    output_file="$output_dir/${output_name}.txt"
    
    # 创建输出目录
    mkdir -p "$output_dir"
    
    # 检查是否已存在
    if [ -f "$output_file" ]; then
        echo "⏭️  跳过已存在: $rel_path"
        continue
    fi
    
    processed=$((processed + 1))
    echo ""
    echo "[$processed] 🔄 处理: $rel_path"
    
    # 创建临时文件名（避免特殊字符）
    temp_video="/tmp/temp_video_$$.mp4"
    cp "$video_file" "$temp_video"
    
    # 使用conda环境执行转写
    timeout 300 conda run -n bili2text-gpu python -c "
import whisper
import torch

print('Loading model...')
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = whisper.load_model('base', device=device)

print('Transcribing...')
result = model.transcribe('$temp_video', language='zh')

print('Saving...')
with open('$output_file', 'w', encoding='utf-8') as f:
    f.write('源文件: $(basename "$video_file")\n')
    f.write('='*50 + '\n\n')
    f.write(result['text'])
print('Done!')
"
    
    if [ $? -eq 0 ] && [ -f "$output_file" ]; then
        echo "✅ 成功"
        success=$((success + 1))
    else
        echo "❌ 失败"
        failed=$((failed + 1))
    fi
    
    # 清理临时文件
    rm -f "$temp_video"
    
    # 显示进度
    total_processed=$((completed_count + processed))
    progress=$((total_processed * 100 / total_count))
    echo "📊 总进度: $total_processed/$total_count ($progress%)"
    
    # 每5个文件休息一下
    if [ $((processed % 5)) -eq 0 ]; then
        echo "💤 休息5秒..."
        sleep 5
    fi
done

echo ""
echo "=" 
echo "📊 转写完成统计:"
echo "   成功: $success"
echo "   失败: $failed"
echo "   总进度: $(find storage/results/gpu_transcripts -name "*.txt" | wc -l)/$total_count"