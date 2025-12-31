/**
 * 视频生成API服务
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

/**
 * 生成序列视频 - 上传2-6张图片文件
 * @param {File[]} files - 2-6个图片文件数组
 * @param {string} prompt - 可选的提示词
 * @returns {Promise<{task_id: string, status: string, message: string, merged_video_url?: string}>}
 */
export async function generateVideo(files, prompt = '') {
  const formData = new FormData();
  
  // 添加文件
  files.forEach(file => {
    formData.append('files', file);
  });
  
  // 添加prompt参数（如果有）
  if (prompt) {
    formData.append('prompt', prompt);
  }
  
  const response = await fetch(`${API_BASE_URL}/v1/generate-sequence`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '视频生成失败');
  }
  
  return response.json();
}

/**
 * 查询视频生成状态
 * @param {string} taskId - 任务ID
 * @returns {Promise<{task_id: string, task_status: string, message: string, video_url?: string}>}
 */
export async function getVideoStatus(taskId) {
  const response = await fetch(`${API_BASE_URL}/v1/status/${taskId}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '查询状态失败');
  }
  
  return response.json();
}

/**
 * 等待视频生成完成
 * @param {string} taskId - 任务ID
 * @returns {Promise<{task_id: string, task_status: string, video_url?: string, message: string}>}
 */
export async function waitVideoCompletion(taskId) {
  const response = await fetch(`${API_BASE_URL}/v1/wait/${taskId}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '等待任务完成失败');
  }
  
  return response.json();
}
