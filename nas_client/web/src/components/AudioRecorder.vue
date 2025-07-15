<template>
  <div class="audio-recorder-container">
    <div class="controls">
      <!-- 单个录音/停止按钮 -->
      <button
          @click="toggleRecording"
          :disabled="isProcessing"
          :class="{
          'recording-active': isRecording, 
          'processing-active': isProcessing,
          'default-button-style': !isRecording && !isProcessing // 默认样式，非录音非处理中
        }"
      >
        <!-- 根据状态显示不同的图标和文本 -->
        <i :class="isRecording ? 'fas fa-stop-circle' : 'fas fa-microphone'"
           style="margin-right: 15px; width: 20px; height: 20px;"></i>
        <span>{{ isProcessing ? '处理中...' : (isRecording ? '停止讲话' : '开始讲话') }}</span>
      </button>
    </div>
    <!-- 状态消息显示区域 -->
    <p class="status-message" :class="statusType">{{ statusMessage }}</p>
    <!-- Dify 工作流输出显示区域 -->
    <p v-if="workflowOutput" class="workflow-output">Dify 输出: {{ workflowOutput }}</p>
  </div>
</template>

<script setup>
import {ref} from 'vue';
import axios from 'axios'; // 导入 axios 库，用于发送 HTTP 请求

// 【队友修改点】：后端 Flask API 的基础 URL
// 在本地测试时，保持为 localhost:5001。
// 当部署到树莓派时，需要将 'localhost' 替换为树莓派的实际 IP 地址。
// 例如: 'http://192.168.1.100:5001/api/audio'
const BACKEND_API_URL = 'http://localhost:5001/api/audio';

// 响应式状态变量
const isRecording = ref(false); // 标记是否正在录音
const isProcessing = ref(false); // 标记后端是否正在处理工作流（录音停止后到Dify返回结果期间）
const statusMessage = ref('点击“开始录音”'); // 显示给用户的状态消息
const statusType = ref('info'); // 状态消息的类型，用于控制样式 (info, success, error)
const workflowOutput = ref(''); // 存储 Dify 工作流返回的文本输出

// --- 统一控制录音开始/停止的函数 ---
// const toggleRecording = async () => {
//   if (isProcessing.value) {
//     // 如果正在处理中，按钮被禁用，不执行任何操作
//     return;
//   }
//
//   if (!isRecording.value) {
//     // 当前不在录音，所以点击是“开始录音”
//     isRecording.value = true;
//     statusMessage.value = '正在请求后端开始录音...';
//     statusType.value = 'info';
//     workflowOutput.value = ''; // 清空之前的输出
//
//     try {
//       const response = await axios.post(`${BACKEND_API_URL}/start_recording`);
//       if (response.data.status === 'success') {
//         statusMessage.value = '录音已开始。请对着麦克风说话。';
//         statusType.value = 'success';
//       } else {
//         statusMessage.value = `错误: ${response.data.message}`;
//         statusType.value = 'error';
//         isRecording.value = false; // 失败则重置录音状态
//       }
//     } catch (error) {
//       console.error("Error starting recording:", error);
//       statusMessage.value = `网络错误或后端无响应`;
//       statusType.value = 'error';
//       isRecording.value = false;
//     }
//   } else {
//     // 当前正在录音，所以点击是“停止录音”
//     isRecording.value = false; // 立即停止录音状态
//     isProcessing.value = true; // 进入处理中状态
//     statusMessage.value = '正在停止录音并处理...';
//     statusType.value = 'info';
//
//     try {
//       const response = await axios.post(`${BACKEND_API_URL}/stop_recording`);
//       if (response.data.status === 'success') {
//         statusMessage.value = '录音已停止，后端正在处理工作流。';
//         statusType.value = 'success';
//         // 【注意】：这里后端是异步处理，前端不会立即收到工作流结果。
//         // 如果需要实时结果，后端需要通过 WebSocket 或长轮询通知前端。
//         // 目前，我们假设后端处理完毕后，会通过某种方式（例如，再次调用一个获取结果的API）让前端获取到结果。
//         // 这里的 workflowOutput.value 暂时不会被后端直接更新，需要您手动或通过其他API获取。
//         // workflowOutput.value = response.data.workflow_result; // 假设后端直接返回了
//       } else {
//         statusMessage.value = `错误: ${response.data.message}`;
//         statusType.value = 'error';
//       }
//     } catch (error) {
//       console.error("Error stopping recording:", error);
//       statusMessage.value = `网络错误或后端无响应: ${error.message}`;
//       statusType.value = 'error';
//     } finally {
//       isProcessing.value = false; // 无论成功或失败，处理流程结束后都重置处理状态
//       statusMessage.value = '点击“开始录音”'
//     }
//   }
// };

const toggleRecording = async () => {
  if (isProcessing.value) {
    return;
  }

  if (!isRecording.value) {
    // --- 开始录音 ---
    isRecording.value = true;
    statusMessage.value = '正在录音，请对着麦克风说话...';
    statusType.value = 'info';

    try {
      const response = await axios.post(`${BACKEND_API_URL}/start_recording`);
      if (response.data.status === 'success') {
        statusMessage.value = '正在录音，请对着麦克风说话...';
        statusType.value = 'success';
      } else {
        statusMessage.value = `错误: ${response.data.message}`;
        statusType.value = 'error';
        isRecording.value = false;
      }
    } catch (error) {
      console.error("Error starting recording:", error);
      statusMessage.value = `网络错误或后端无响应`;
      statusType.value = 'error';
      isRecording.value = false;

      setTimeout(() => {
        statusMessage.value = '点击“开始录音”'
        statusType.value = 'info';
      }, 3000);
    }
  } else {
    // --- 停止录音并进入处理流程 ---
    isRecording.value = false;
    isProcessing.value = true;
    statusMessage.value = '录音已停止，正在调用工作流...';
    statusType.value = 'info';

    try {
      const response = await axios.post(`${BACKEND_API_URL}/stop_recording`);
      if (response.data.status === 'success') {
        statusMessage.value = '等待Dify工作流返回结果...';
        statusType.value = 'info';

        // 模拟轮询获取 workflowOutput（前端需配合定时器或 WebSocket）
        // 这里假设几秒后 workflowOutput 被填充
        setTimeout(() => {
          if (workflowOutput.value) {
            statusMessage.value = `工作流已完成，识别结果为：${workflowOutput.value}`;
            statusType.value = 'success';

            // 模拟朗读过程
            setTimeout(() => {
              statusMessage.value = `正在朗读识别结果：${workflowOutput.value}`;
              setTimeout(() => {
                statusMessage.value = '识别与朗读已完成。';
              }, 2000); // 朗读持续时间
            }, 500); // 显示识别结果
          }
        }, 3000); // 模拟后台处理延迟
      } else {
        statusMessage.value = `错误: ${response.data.message}`;
        statusType.value = 'error';
      }
    } catch (error) {
      console.error("Error stopping recording:", error);
      statusMessage.value = `网络错误或后端无响应: ${error.message}`;
      statusType.value = 'error';
    } finally {
      isProcessing.value = false;

    }
  }
};

</script>

<style scoped>
@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css");

/* 组件容器样式 */
.audio-recorder-container {
  display: flex;
  flex-direction: column; /* 垂直排列子元素 */
  align-items: center; /* 水平居中 */
  justify-content: center; /* 垂直居中 */
  padding: 10px 20px;

  border-radius: 10px; /* 圆角 */

}


/* 按钮容器样式 (现在只有一个按钮，但为了保持结构，可以保留) */
.controls {
  display: flex; /* 确保按钮在容器中居中 */
  justify-content: center;
  margin-bottom: 20px;
}

/* 按钮通用样式 */
button {
  padding: 15px 30px;
  font-size: 1.5em;
  font-weight: bold;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.1s ease; /* 过渡动画 */
  display: flex;
  align-items: center;
  gap: 0px; /* 文本和图标之间间距 */
  color: white; /* 文字颜色 */
}

/* 按钮悬停效果 */
button:hover:not(:disabled) {
  transform: translateY(-2px); /* 向上轻微移动 */
}

/* 禁用按钮样式 (当 isProcessing 为 true 时生效) */
button:disabled {
  background-color: #cccccc; /* 灰色背景 */
  cursor: not-allowed; /* 禁用鼠标样式 */
  opacity: 0.7; /* 透明度 */
}

/* 默认按钮样式 (当不录音也不处理时) */
.default-button-style {
  background-color: #28a745; /* 绿色 */
}

.default-button-style:hover:not(:disabled) {
  background-color: #218838;
}

/* 录音中状态的按钮样式 */
.recording-active {
  background-color: #dc3545 !important; /* 红色，表示点击停止 */
}

/* 处理中状态的按钮样式 */
.processing-active {
  background-color: #007bff !important; /* 蓝色，表示正在处理 */
}

/* 状态消息通用样式 */
.status-message {
  font-size: 0.9em;
  margin-top: 0px;
  padding: 4px 18px;
  border-radius: 5px;
  background-color: #e9ecef;
  color: #343a40;
  text-align: left;
}

/* 不同状态消息的特定颜色 */
.status-message.info {
  background-color: #e0f7fa;
  color: #007bff;
}

.status-message.success {
  background-color: #d4edda;
  color: #28a745;
}

.status-message.error {
  background-color: #f8d7da;
  color: #dc3545;
}

/* Dify 工作流输出样式 */
.workflow-output {
  margin-top: 15px;
  padding: 10px 15px;
  background-color: #e2e6ea;
  border-left: 5px solid #0056b3; /* 左侧蓝色边框 */
  font-family: 'Courier New', Courier, monospace; /* 等宽字体 */
  font-size: 0.9em;
  color: #333;
  white-space: pre-wrap; /* 保留空白符并自动换行 */
  word-break: break-word; /* 强制长单词换行 */

  text-align: left; /* 居中 */
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2; /* 显示最大行数 */
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 导入 FontAwesome 图标库 */
@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css");
</style>
