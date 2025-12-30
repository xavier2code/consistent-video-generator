<script setup>
import { ref, computed } from 'vue';
import { generateVideo, getVideoStatus } from '../api/video.js';

// 状态管理
const firstImage = ref(null);
const secondImage = ref(null);
const firstImagePreview = ref('');
const secondImagePreview = ref('');
const prompt = ref('');
const isUploading = ref(false);
const isPolling = ref(false);
const taskId = ref('');
const taskStatus = ref('');
const videoUrl = ref('');
const errorMessage = ref('');
const statusMessage = ref('');

// 计算属性
const canSubmit = computed(() => {
  return firstImage.value && secondImage.value && !isUploading.value && !isPolling.value;
});

const statusText = computed(() => {
  const statusMap = {
    'PENDING': '等待中',
    'RUNNING': '生成中',
    'SUCCEEDED': '成功',
    'FAILED': '失败',
    'UNKNOWN': '未知'
  };
  return statusMap[taskStatus.value] || taskStatus.value;
});

// 文件选择处理
function handleFileSelect(event, imageType) {
  const file = event.target.files[0];
  if (!file) return;
  
  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
  if (!allowedTypes.includes(file.type)) {
    errorMessage.value = '不支持的文件格式，请上传 JPG、PNG、GIF、BMP 或 WEBP 格式的图片';
    return;
  }
  
  // 验证文件大小 (10MB)
  if (file.size > 10 * 1024 * 1024) {
    errorMessage.value = '文件大小不能超过 10MB';
    return;
  }
  
  errorMessage.value = '';
  
  // 预览图片
  const reader = new FileReader();
  reader.onload = (e) => {
    if (imageType === 'first') {
      firstImage.value = file;
      firstImagePreview.value = e.target.result;
    } else {
      secondImage.value = file;
      secondImagePreview.value = e.target.result;
    }
  };
  reader.readAsDataURL(file);
}

// 清除图片
function clearImage(imageType) {
  if (imageType === 'first') {
    firstImage.value = null;
    firstImagePreview.value = '';
  } else {
    secondImage.value = null;
    secondImagePreview.value = '';
  }
}

// 提交生成视频
async function handleSubmit() {
  if (!canSubmit.value) return;
  
  errorMessage.value = '';
  statusMessage.value = '';
  videoUrl.value = '';
  isUploading.value = true;
  
  try {
    // 上传文件并生成视频
    const response = await generateVideo([firstImage.value, secondImage.value], prompt.value);
    
    taskId.value = response.task_id;
    taskStatus.value = 'PENDING';
    statusMessage.value = response.message;
    
    // 开始轮询
    startPolling();
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    isUploading.value = false;
  }
}

// 开始轮询状态
function startPolling() {
  isPolling.value = true;
  pollStatus();
}

// 轮询状态
async function pollStatus() {
  if (!taskId.value || !isPolling.value) return;
  
  try {
    const response = await getVideoStatus(taskId.value);
    
    taskStatus.value = response.task_status;
    statusMessage.value = response.message;
    
    // 如果状态是 RUNNING，继续轮询
    if (response.task_status === 'RUNNING') {
      setTimeout(pollStatus, 2000); // 每2秒查询一次
    } else {
      // 任务完成或失败
      isPolling.value = false;
      
      if (response.task_status === 'SUCCEEDED' && response.video_url) {
        videoUrl.value = response.video_url;
        statusMessage.value = '视频生成成功！';
      } else if (response.task_status === 'FAILED') {
        errorMessage.value = '视频生成失败';
      }
    }
  } catch (error) {
    errorMessage.value = error.message;
    isPolling.value = false;
  }
}

// 重置表单
function resetForm() {
  firstImage.value = null;
  secondImage.value = null;
  firstImagePreview.value = '';
  secondImagePreview.value = '';
  prompt.value = '';
  taskId.value = '';
  taskStatus.value = '';
  videoUrl.value = '';
  errorMessage.value = '';
  statusMessage.value = '';
  isPolling.value = false;
}

// 下载视频
function downloadVideo() {
  if (!videoUrl.value) return;
  window.open(videoUrl.value, '_blank');
}
</script>

<template>
  <div class="video-generator">
    <h1>AI 视频生成器</h1>
    <p class="subtitle">上传首帧和末帧图片，AI 帮你生成流畅的视频</p>
    
    <!-- 错误提示 -->
    <div v-if="errorMessage" class="alert alert-error">
      {{ errorMessage }}
    </div>
    
    <!-- 状态提示 -->
    <div v-if="statusMessage && !errorMessage" class="alert alert-info">
      {{ statusMessage }}
      <span v-if="isPolling" class="loading-dots">...</span>
    </div>
    
    <!-- 上传表单 -->
    <div class="upload-container" v-if="!videoUrl">
      <div class="upload-section">
        <h3>首帧图片</h3>
        <div class="image-upload">
          <div v-if="!firstImagePreview" class="upload-placeholder" @click="$refs.firstFileInput.click()">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <circle cx="8.5" cy="8.5" r="1.5"></circle>
              <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
            <p>点击上传图片</p>
            <span class="file-info">支持 JPG、PNG、GIF 等格式，最大 10MB</span>
          </div>
          <div v-else class="image-preview">
            <img :src="firstImagePreview" alt="首帧预览" />
            <button @click="clearImage('first')" class="btn-remove" type="button">×</button>
          </div>
          <input 
            ref="firstFileInput"
            type="file" 
            accept="image/*" 
            @change="handleFileSelect($event, 'first')"
            style="display: none"
          />
        </div>
      </div>
      
      <div class="upload-section">
        <h3>末帧图片</h3>
        <div class="image-upload">
          <div v-if="!secondImagePreview" class="upload-placeholder" @click="$refs.secondFileInput.click()">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <circle cx="8.5" cy="8.5" r="1.5"></circle>
              <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
            <p>点击上传图片</p>
            <span class="file-info">支持 JPG、PNG、GIF 等格式，最大 10MB</span>
          </div>
          <div v-else class="image-preview">
            <img :src="secondImagePreview" alt="末帧预览" />
            <button @click="clearImage('second')" class="btn-remove" type="button">×</button>
          </div>
          <input 
            ref="secondFileInput"
            type="file" 
            accept="image/*" 
            @change="handleFileSelect($event, 'second')"
            style="display: none"
          />
        </div>
      </div>
      
      <!-- 提示词输入 -->
      <div class="prompt-section">
        <label for="prompt">提示词（可选）</label>
        <textarea 
          id="prompt"
          v-model="prompt" 
          placeholder="例如：写实风格，高质量视频，流畅的镜头运动"
          rows="3"
          :disabled="isUploading || isPolling"
        ></textarea>
      </div>
      
      <!-- 任务状态 -->
      <div v-if="taskStatus" class="status-section">
        <div class="status-item">
          <span class="status-label">任务ID:</span>
          <span class="status-value">{{ taskId }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">状态:</span>
          <span class="status-value" :class="'status-' + taskStatus.toLowerCase()">
            {{ statusText }}
          </span>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="actions">
        <button 
          @click="handleSubmit" 
          :disabled="!canSubmit"
          class="btn btn-primary"
        >
          <span v-if="isUploading">上传中...</span>
          <span v-else-if="isPolling">生成中...</span>
          <span v-else>生成视频</span>
        </button>
        
        <button 
          v-if="taskId && !isPolling" 
          @click="resetForm"
          class="btn btn-secondary"
        >
          重新开始
        </button>
      </div>
    </div>
    
    <!-- 结果展示 -->
    <div v-if="videoUrl" class="result-container">
      <div class="success-icon">✓</div>
      <h2>视频生成成功！</h2>
      
      <div class="video-preview">
        <video :src="videoUrl" controls autoplay loop></video>
      </div>
      
      <div class="result-actions">
        <button @click="downloadVideo" class="btn btn-primary">
          下载视频
        </button>
        <button @click="resetForm" class="btn btn-secondary">
          生成新视频
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.video-generator {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.alert-error {
  background-color: #fee;
  color: #c33;
  border: 1px solid #fcc;
}

.alert-info {
  background-color: #e3f2fd;
  color: #1976d2;
  border: 1px solid #90caf9;
}

.loading-dots {
  display: inline-block;
  animation: blink 1.4s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}

.upload-container {
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.upload-section {
  margin-bottom: 2rem;
}

.upload-section h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
  font-size: 1.1rem;
}

.image-upload {
  position: relative;
}

.upload-placeholder {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}

.upload-placeholder:hover {
  border-color: #42b883;
  background: #f0f9f5;
}

.upload-placeholder svg {
  color: #999;
  margin-bottom: 1rem;
}

.upload-placeholder p {
  color: #666;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.file-info {
  color: #999;
  font-size: 0.875rem;
}

.image-preview {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #42b883;
}

.image-preview img {
  width: 100%;
  height: auto;
  display: block;
}

.btn-remove {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(0,0,0,0.6);
  color: white;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.btn-remove:hover {
  background: rgba(0,0,0,0.8);
}

.prompt-section {
  margin-bottom: 2rem;
}

.prompt-section label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: 500;
}

.prompt-section textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
  transition: border-color 0.3s;
}

.prompt-section textarea:focus {
  outline: none;
  border-color: #42b883;
}

.prompt-section textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.status-section {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.status-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.status-item:last-child {
  margin-bottom: 0;
}

.status-label {
  color: #666;
  font-weight: 500;
}

.status-value {
  color: #2c3e50;
  font-weight: 600;
}

.status-pending {
  color: #ff9800;
}

.status-running {
  color: #2196f3;
  animation: pulse 1.5s infinite;
}

.status-succeeded {
  color: #4caf50;
}

.status-failed {
  color: #f44336;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #42b883;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #35a372;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 184, 131, 0.3);
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.result-container {
  text-align: center;
  background: #fff;
  border-radius: 12px;
  padding: 3rem 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.success-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #4caf50;
  color: white;
  font-size: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

.result-container h2 {
  color: #2c3e50;
  margin-bottom: 2rem;
}

.video-preview {
  margin-bottom: 2rem;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.video-preview video {
  width: 100%;
  max-width: 100%;
  display: block;
}

.result-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

@media (max-width: 768px) {
  .video-generator {
    padding: 1rem;
  }
  
  .upload-container, .result-container {
    padding: 1.5rem;
  }
  
  .actions, .result-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>
