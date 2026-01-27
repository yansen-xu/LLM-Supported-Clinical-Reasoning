<template>
  <div class="content">
    <div class="section-container">
      <!-- 上半部分：患者基本信息和用户信息 -->
      <div class="upper-section">
        <!-- 左侧：患者基本信息 -->
        <div class="patient-info-section">
          <h4>Patient Basic Information</h4>
          <div class="info-content" v-if="patientInfo">
            <div v-html="formatPatientInfo(patientInfo)"></div>
          </div>
          <div class="loading" v-else-if="loading">
            Loading...
          </div>
          <div class="error" v-else-if="error">
            {{ error }}
          </div>
        </div>
        
                 <!-- 右侧：用户信息 -->
                  <div class="user-info-section">
           <div class="user-header">
             <h4>User Information</h4>
             <div class="user-details">
               <span><strong>Welcome: </strong> {{ username }}</span>
               <span class="divider">|</span>
               <span><strong>Current Case: </strong> {{ currentCaseName }}</span>
             </div>
           </div>
             <button 
               class="back-to-analysis-btn"
               :class="{ disabled: !isPort5000Open }"
               @click="handleBackToAnalysis"
               :disabled="!isPort5000Open"
               :title="isPort5000Open ? 'Switch to Analysis mode' : 'Analysis service is not running. Please start the backend with python run_all.py'"
             >
               Back to Analysis
             </button>
         </div>
      </div>
      
      <!-- 下半部分：对话内容 -->
      <div class="lower-section">
        <h3>Inquiry Record</h3>
        <div class="chat-messages" ref="messageContainer">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message', message.role]"
          >
            <div class="avatar">
              <span v-if="message.role === 'user'">👨‍⚕️</span>
              <span v-else>🤒</span>
            </div>
            <div class="message-content">
              <div class="message-text">
                {{ message.content }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue';
import axios from "axios";

// 配置axios baseURL
const baseURL = process.env.NODE_ENV === 'development' 
  ? '' // 在开发环境中使用相对路径，通过Vue代理
  : window.location.origin;

// 创建axios实例
const api = axios.create({
  baseURL: baseURL,
  timeout: 10000
});

export default {
  name: "SectionB",
  props: {
    username: {
      type: String,
      required: true
    },
    currentCaseId: {
      type: Number,
      default: 1
    },
    selectedEvaluator: {
      type: Object,
      default: null
    }
  },
  emits: ['back-to-analysis'],
  setup(props, { emit }) {
    const patientInfo = ref('');
    const mainSuit = ref('');
    const loading = ref(false);
    const error = ref('');
    const messages = ref([]);
    const messageContainer = ref(null);
    const currentCaseName = ref(`case${props.currentCaseId}`);
    
    const fetchCaseInfo = async () => {
      loading.value = true;
      error.value = '';
      
      try {
        // 获取患者基本信息
        const caseResponse = await api.get(`/api/evaluation/current-case?username=${props.username}`);
        const caseData = caseResponse.data;
        
        if (caseData.status === 'success') {
          patientInfo.value = caseData.formatted_data;
          // 获取当前案例名称
          if (caseData.case_filename) {
            currentCaseName.value = caseData.case_filename;
          }
        } else {
          error.value = caseData.message || '获取病例信息失败';
        }
        
        // 获取主诉
        const suitResponse = await api.get(`/api/evaluation/get-main-suit?username=${props.username}`);
        const suitData = suitResponse.data;
        
        if (suitData.status === 'success') {
          mainSuit.value = suitData.main_suit;
        } else {
          error.value = suitData.message || '获取主诉失败';
        }
        
      } catch (err) {
        error.value = '网络请求失败: ' + err.message;
      } finally {
        loading.value = false;
      }
    };
    
    onMounted(async () => {
      if (props.username) {
        await fetchCaseInfo();
      }
      // Check port 5000 when component mounts
      await checkPort5000();
      // Periodically check port status (every 5 seconds)
      setInterval(checkPort5000, 5000);
    });
    
    // 监听username变化，重新加载数据
    watch(() => props.username, () => {
      if (props.username) {
        fetchCaseInfo();
      }
    });

    // 加载评估者对话内容
    const loadEvaluatorConversation = async (evaluator) => {
      if (!evaluator) {
        messages.value = [];
        return;
      }

      try {
        // 获取当前案例信息，以确定正确的案例ID
        const caseResponse = await fetch(`/api/evaluation/current-case?username=${props.username}`);
        const caseData = await caseResponse.json();
        
        if (caseData.status !== 'success') {
          throw new Error('获取当前案例信息失败');
        }
        
        // 从case_filename中提取案例ID
        let actualCaseId = props.currentCaseId;
        if (caseData.case_filename && caseData.case_filename.startsWith('case')) {
          actualCaseId = parseInt(caseData.case_filename.replace('case', ''));
        }
        
        const response = await fetch(`/api/evaluation/case/${actualCaseId}/evaluator/${evaluator.evaluator.id}`);
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'success' && data.conversation) {
            messages.value = data.conversation;
            console.log(`加载评估者 ${evaluator.evaluator.id} 的对话内容:`, data.conversation);
            // 滚动到底部
            nextTick(() => {
              scrollToBottom();
            });
          }
        }
      } catch (error) {
        console.error(`加载评估者 ${evaluator.evaluator.id} 对话失败:`, error);
        messages.value = [];
      }
    };

    // 滚动到底部
    const scrollToBottom = () => {
      if (messageContainer.value) {
        messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
      }
    };

    // 监听选中的评估者变化
    watch(() => props.selectedEvaluator, (newEvaluator) => {
      if (newEvaluator) {
        loadEvaluatorConversation(newEvaluator);
      } else {
        messages.value = [];
      }
    }, { immediate: true });
    
    const formatPatientInfo = (info) => {
      if (!info) return '';
      // 将换行符转换为HTML换行标签
      return info.replace(/\n/g, '<br>');
    };

    const handleBackToAnalysis = () => {
      // Emit event to switch back to analysis mode
      emit('back-to-analysis');
    };
    
    // Check if port 5000 (Analysis service) is open
    const isPort5000Open = ref(false);
    
    const checkPort5000 = async () => {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 3000); // 3 second timeout
        
        const response = await fetch('http://localhost:5000/health', {
          signal: controller.signal,
          mode: 'no-cors'  // Allow CORS requests
        });
        
        clearTimeout(timeout);
        // In no-cors mode, response.ok might not work correctly, so check if response is not null
        isPort5000Open.value = response !== null;
      } catch (error) {
        console.log('Port 5000 check failed:', error);
        isPort5000Open.value = false;
      }
    };
    
    return {
      patientInfo,
      mainSuit,
      loading,
      error,
      messages,
      messageContainer,
      currentCaseName,
      formatPatientInfo,
      fetchCaseInfo,
      handleBackToAnalysis,
      isPort5000Open,
      checkPort5000
    };
  },
};
</script>

<style scoped>
.content {
  padding: clamp(8px, 1vw, 16px);
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-container {
  display: flex;
  flex-direction: column;
  gap: clamp(6px, 1vw, 12px);
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.upper-section {
  display: flex;
  gap: clamp(8px, 1.2vw, 16px);
  flex-shrink: 0;
  max-height: 30%;
}

.patient-info-section {
  flex: 1;
  border: clamp(1px, 0.2vw, 2px) solid #e0e0e0;
  border-radius: clamp(4px, 0.8vw, 12px);
  padding: clamp(6px, 1vw, 12px);
  background-color: #fafafa;
  display: flex;
  flex-direction: column;
}

.user-info-section {
  flex: 1;
  border: clamp(1px, 0.2vw, 2px) solid #e0e0e0;
  border-radius: clamp(4px, 0.8vw, 12px);
  padding: clamp(6px, 1vw, 12px);
  background-color: #fafafa;
  display: flex;
  flex-direction: column;
}

.user-header {
  display: flex;
  align-items: center;
  gap: clamp(8px, 1.2vw, 16px);
  margin-bottom: clamp(4px, 0.8vw, 10px);
}

.user-info-section h4 {
  margin: 0;
  font-size: clamp(8px, 0.8vw, 11px); /* 缩小20%: 10px -> 8px, 1vw -> 0.8vw, 14px -> 11px */
  font-weight: 600;
  white-space: nowrap;
}

.user-details {
  display: flex;
  align-items: center;
  gap: clamp(4px, 0.8vw, 10px);
  color: #333;
  font-size: clamp(7px, 0.72vw, 10px); /* 缩小20%: 9px -> 7px, 0.9vw -> 0.72vw, 13px -> 10px */
  line-height: 1.4;
}

.divider {
  color: #ccc;
  font-weight: normal;
}

.back-to-analysis-btn {
  width: 100%;
  padding: clamp(2px, 0.5vw, 5px);
  border: none;
  border-radius: clamp(2px, 0.4vw, 5px);
  background: #2196F3;
  color: white;
  cursor: pointer;
  font-size: clamp(7px, 0.72vw, 10px);
  font-weight: 500;
  transition: all 0.3s ease;
  margin-top: clamp(4px, 0.8vw, 10px);
}

.back-to-analysis-btn:hover:not(:disabled) {
  background: #1976D2;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.back-to-analysis-btn:active:not(:disabled) {
  transform: translateY(0);
}

.back-to-analysis-btn:disabled {
  background: #ccc;
  color: #666;
  cursor: not-allowed;
  opacity: 0.6;
}

.lower-section {
  border: clamp(1px, 0.2vw, 2px) solid #e0e0e0;
  border-radius: clamp(4px, 0.8vw, 12px);
  padding: clamp(8px, 1.2vw, 16px);
  background-color: #fafafa;
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.upper-section h3, .lower-section h3 {
  margin-top: 0;
  margin-bottom: clamp(8px, 1.2vw, 16px);
  color: #333;
  border-bottom: clamp(1px, 0.2vw, 3px) solid #007bff;
  padding-bottom: clamp(3px, 0.6vw, 8px);
  font-size: clamp(10px, 0.96vw, 13px); /* 缩小20%: 12px -> 10px, 1.2vw -> 0.96vw, 16px -> 13px */
}

.case-info {
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 1.5vw, 20px);
  flex: 1;
  min-height: 0;
}

.patient-info, .main-suit {
  background-color: white;
  padding: clamp(8px, 1.2vw, 16px);
  border-radius: clamp(3px, 0.6vw, 8px);
  border: clamp(1px, 0.15vw, 2px) solid #ddd;
  flex-shrink: 0;
}

.patient-info h4, .main-suit h4 {
  margin-top: 0;
  margin-bottom: clamp(4px, 0.8vw, 10px);
  color: #007bff;
  font-size: clamp(8px, 0.8vw, 11px); /* 缩小20%: 10px -> 8px, 1vw -> 0.8vw, 14px -> 11px */
  font-weight: 600;
}

.info-content, .suit-content {
  color: #333;
  line-height: 1.4;
  white-space: pre-line;
  font-size: clamp(7px, 0.72vw, 10px); /* 缩小20%: 9px -> 7px, 0.9vw -> 0.72vw, 13px -> 10px */
}

.loading {
  color: #666;
  font-style: italic;
}

.error {
  color: #dc3545;
  font-weight: 500;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: clamp(10px, 1.5vw, 20px);
  min-height: 0;
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.chat-messages::-webkit-scrollbar {
  width: clamp(4px, 0.5vw, 8px);
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: clamp(2px, 0.3vw, 4px);
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: clamp(2px, 0.3vw, 4px);
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.message {
  display: flex;
  margin-bottom: clamp(8px, 1.5vw, 16px);
  align-items: flex-start;
}

.message.user {
  flex-direction: row-reverse;
}

.avatar {
  margin: 0 clamp(6px, 1vw, 12px);
  font-size: clamp(11px, 1.6vw, 19px); /* 缩小20%: 14px -> 11px, 2vw -> 1.6vw, 24px -> 19px */
  flex-shrink: 0;
}

.message-content {
  max-width: 75%;
  background: #fff;
  padding: clamp(6px, 1vw, 12px);
  border-radius: clamp(4px, 0.8vw, 12px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  font-size: clamp(8px, 0.88vw, 11px); /* 缩小20%: 10px -> 8px, 1.1vw -> 0.88vw, 14px -> 11px */
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.message.user .message-content {
  background: #409eff;
  color: white;
}

/* 确保病人角色的消息内容显示为黑色文字 */
.message:not(.user) .message-content {
  background: #fff;
  color: #333;
}

.message-text {
  user-select: text;
  cursor: text;
  line-height: 1.6;
}

/* 响应式断点 */
@media (max-width: 1200px) {
  .message-content {
    max-width: 80%;
    font-size: clamp(9px, 0.96vw, 13px); /* 缩小20%: 11px -> 9px, 1.2vw -> 0.96vw, 16px -> 13px */
  }
  
  /* 确保在响应式布局中病人角色的消息仍然显示黑色文字 */
  .message:not(.user) .message-content {
    background: #fff;
    color: #333;
  }
  
  .avatar {
    font-size: clamp(13px, 1.76vw, 22px); /* 缩小20%: 16px -> 13px, 2.2vw -> 1.76vw, 28px -> 22px */
  }
}

@media (max-width: 768px) {
  .content {
    padding: clamp(6px, 0.8vw, 12px);
  }
  
  .section-container {
    gap: clamp(4px, 0.8vw, 8px);
  }
  
  .upper-section, .lower-section {
    padding: clamp(6px, 1vw, 12px);
  }
  
  .upper-section {
    flex-direction: column;
    gap: clamp(6px, 1vw, 12px);
  }
  
  .patient-info-section, .user-info-section {
    flex: none;
  }
  
  .message-content {
    max-width: 85%;
    font-size: clamp(8px, 0.88vw, 11px); /* 缩小20%: 10px -> 8px, 1.1vw -> 0.88vw, 14px -> 11px */
  }
  
  /* 确保在移动端病人角色的消息仍然显示黑色文字 */
  .message:not(.user) .message-content {
    background: #fff;
    color: #333;
  }
  
  .avatar {
    font-size: clamp(11px, 1.6vw, 19px); /* 缩小20%: 14px -> 11px, 2vw -> 1.6vw, 24px -> 19px */
    margin: 0 clamp(6px, 1vw, 12px);
  }
  
  .message {
    margin-bottom: clamp(8px, 1.5vw, 16px);
  }
}



@media (max-height: 600px) {
  .section-container {
    gap: clamp(3px, 0.6vw, 6px);
  }
  
  .upper-section, .lower-section {
    padding: clamp(4px, 0.8vw, 8px);
  }
  
  .message {
    margin-bottom: clamp(6px, 1.2vw, 12px);
  }
  
  .avatar {
    font-size: clamp(10px, 1.44vw, 16px); /* 缩小20%: 12px -> 10px, 1.8vw -> 1.44vw, 20px -> 16px */
  }
  
  .message-content {
    font-size: clamp(7px, 0.8vw, 10px); /* 缩小20%: 9px -> 7px, 1vw -> 0.8vw, 13px -> 10px */
  }
  
  /* 确保在小屏幕下病人角色的消息仍然显示黑色文字 */
  .message:not(.user) .message-content {
    background: #fff;
    color: #333;
  }
}
</style>
