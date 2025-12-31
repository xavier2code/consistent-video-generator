# 序列视频生成功能说明

## 功能概述

新增的序列视频生成功能允许上传6张图片，自动生成5个视频片段并合并成一个完整的视频。

## API接口

### 1. 生成序列视频

**端点:** `POST /api/v1/generate-sequence`

**参数:**
- `files`: 6张图片文件（必需，按顺序上传）
- `prompt`: 视频生成提示词（可选）

**工作流程:**

1. **上传6张图片** - 按时间顺序排列的6张人物照片
2. **生成5个视频片段:**
   - 视频1: 图片1 → 图片2
   - 视频2: 图片2 → 图片3
   - 视频3: 图片3 → 图片4
   - 视频4: 图片4 → 图片5
   - 视频5: 图片5 → 图片6
3. **自动下载** - 等待所有视频生成完成并下载到本地
4. **视频合并** - 使用ffmpeg将5个片段拼接成完整视频
5. **返回结果** - 返回合并后的视频URL

**响应示例:**
```json
{
  "task_id": "seq_a1b2c3d4e5f6g7h8",
  "status": "completed",
  "message": "序列视频生成并合并完成",
  "total_videos": 5,
  "processed_videos": 5,
  "merged_video_url": "http://localhost:8000/videos/seq_a1b2c3d4e5f6g7h8_merged.mp4"
}
```

## 使用示例

### cURL命令

```bash
curl -X POST "http://localhost:8000/api/v1/generate-sequence" \
  -F "files=@photo1.jpg" \
  -F "files=@photo2.jpg" \
  -F "files=@photo3.jpg" \
  -F "files=@photo4.jpg" \
  -F "files=@photo5.jpg" \
  -F "files=@photo6.jpg" \
  -F "prompt=同一人物在不同时期的平滑过渡"
```

### Python示例

```python
import requests

url = "http://localhost:8000/api/v1/generate-sequence"

files = [
    ('files', open('photo1.jpg', 'rb')),
    ('files', open('photo2.jpg', 'rb')),
    ('files', open('photo3.jpg', 'rb')),
    ('files', open('photo4.jpg', 'rb')),
    ('files', open('photo5.jpg', 'rb')),
    ('files', open('photo6.jpg', 'rb'))
]

data = {
    'prompt': '同一人物在不同时期的平滑过渡'
}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"视频URL: {result['merged_video_url']}")
```

## 技术细节

### 依赖项

- **httpx**: 用于异步下载视频文件
- **ffmpeg-python**: 用于视频合并操作
- **ffmpeg**: 系统需要安装ffmpeg命令行工具

### 视频合并

使用ffmpeg的concat协议进行无损合并：
```bash
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

### 超时设置

- 每个视频任务最多等待6分钟（180次 × 2秒）
- HTTP下载超时为5分钟（300秒）

### 文件清理

自动清理临时文件：
- ✅ 上传的6张图片
- ✅ 下载的5个视频片段
- ⚠️ 保留合并后的完整视频

## 注意事项

### 1. 系统要求

需要在系统中安装ffmpeg：

**Windows:**
```powershell
# 使用Chocolatey
choco install ffmpeg

# 或下载并添加到PATH
# https://ffmpeg.org/download.html
```

**Linux:**
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg      # CentOS/RHEL
```

**macOS:**
```bash
brew install ffmpeg
```

### 2. 处理时间

- 单个视频生成: 约30-120秒
- 5个视频总计: 约2.5-10分钟
- 视频下载: 取决于网络速度
- 视频合并: 通常<10秒

**预计总时间:** 约5-15分钟

### 3. 图片顺序

⚠️ **重要:** 必须按时间顺序上传6张图片！
- 图片应该展示同一人物的时间变化
- 顺序错误会导致视频过渡不自然

### 4. 存储空间

每个合并视频约占用:
- 720P分辨率: 约10-30MB
- 取决于视频长度和复杂度

建议定期清理 `videos/` 目录。

## 与原接口对比

| 特性 | generate | generate-sequence |
|------|----------|-------------------|
| 图片数量 | 2张 | 6张 |
| 生成视频数 | 1个 | 5个（自动合并） |
| 处理方式 | 单次调用 | 批量调用+合并 |
| 返回结果 | 任务ID | 合并视频URL |
| 处理时间 | 30-120秒 | 5-15分钟 |
| 适用场景 | 简单过渡 | 长时间跨度变化 |

## 故障排查

### FFmpeg未安装
```
错误: 合并视频失败
解决: 安装ffmpeg并确保在PATH中
```

### 视频生成超时
```
错误: 第X个视频生成失败或超时
解决: 检查DashScope服务状态，稍后重试
```

### 内存不足
```
错误: 下载或合并失败
解决: 确保有足够磁盘空间和内存
```

## 最佳实践

1. **图片质量**: 使用清晰、高质量的图片
2. **一致性**: 确保6张图片中的人物面部清晰可见
3. **光照**: 尽量保持相似的光照条件
4. **角度**: 使用相似的拍摄角度
5. **间隔**: 时间跨度均匀分布效果更好

## 后续优化

可能的改进方向：
- [ ] 支持自定义视频数量（不限于6张图片）
- [ ] 添加进度查询接口
- [ ] 支持异步处理（后台任务）
- [ ] 添加视频质量选项
- [ ] 支持自定义分辨率
- [ ] 添加视频预览功能
