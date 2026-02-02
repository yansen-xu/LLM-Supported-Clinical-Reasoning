<template>
  <div class="section-c-container">
    <!-- 病例信息显示部分 -->
    <div class="case-info-section">
      <div class="case-header">
        <h3>Case {{ currentCaseIndex + 1 }}</h3>
        <div class="header-right">
          <button 
            @click="resetConversation" 
            class="reset-btn"
            title="Clear conversation and start over"
          >
            🔄 Reset
          </button>
          <span class="progress-indicator">Progress: ({{ currentCaseIndex + 1 }}/{{ totalCases }})</span>
        </div>
      </div>
      <div v-if="formattedCaseData">
        <pre>{{ formattedCaseData }}</pre>
      </div>
      <div v-else-if="loading">
        <p>loading</p>
      </div>
      <div v-else>
        <p>No case data</p>
      </div>
    </div>
    
    <!-- 聊天对话部分 -->
    <div class="chat-container">
      <div class="chat-messages" ref="messageContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role, message.category]"
        >
          <div class="avatar">
            <span v-if="message.role === 'user'">👨‍⚕️</span>
            <span v-else>🤒</span>
          </div>
          <div class="message-content">
            <!-- 分类标签 -->
            <div v-if="message.role === 'assistant' && message.category" class="category-tag">
              {{ getCategoryLabel(message.category) }}
            </div>
            <div 
              class="message-text"
              @mouseup="(e) => handleTextSelection(e, index)"
              @mousedown="clearSelection"
            >
              <span v-if="message.isLoading">Thinking...</span>
              {{ message.content }}
            </div>
          </div>
        </div>
      </div>
      <div class="input-area">
        <input
          v-model="inputMessage"
          @keyup.enter="sendMessage"
          placeholder="Input your evidence."
          :disabled="isSending"
          class="input"
        />
        <button
          @click="sendMessage"
          :disabled="!inputMessage || isSending"
          class="send-btn"
        >
          Send
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick, defineExpose, computed, onMounted, onBeforeUnmount } from "vue";
import axios from "axios";

export default {
  name: "SectionC",
  setup() {
    const getBackendBaseURL = () => {
      // 在Docker环境中，前端通过nginx代理访问后端
      // 如果是在开发环境，使用localhost:5000
      // 如果是在生产环境，使用相对路径让nginx代理处理
      if (process.env.NODE_ENV === 'development') {
        return 'http://localhost:5000';
      } else {
        // 在生产环境中，使用相对路径，让nginx代理到后端
        return '';
      }
    };
    
    const backendBaseURL = ref(getBackendBaseURL());

    const messages = ref([]);
    const inputMessage = ref("");
    const isSending = ref(false);
    const messageContainer = ref(null);
    
    // 病例信息相关状态
    const currentCaseIndex = ref(0);
    const totalCases = ref(0); // 总案例数量状态
    const formattedCaseData = ref("");
    const loading = ref(true);
    let casePollTimer = null;

    // 轮询相关状态
    let pollTimer = null;
    // 分类标签映射
    const categoryLabels = {
      'symptom': 'Symptom',
      'sign': 'Sign', 
      'examination': 'Examination',
      'history': 'History',
      'other': 'Other'
    };

    // 获取分类标签显示文本
    const getCategoryLabel = (category) => {
      return categoryLabels[category] || 'Other';
    };

    // 调用后端分类API
    const classifyMessage = async (messageContent) => {
      try {
        const userId = localStorage.getItem('analysis_user_id') || 'default_user';
        const username = localStorage.getItem('analysis_username') || '';
        const response = await axios.post(
          `${backendBaseURL.value}/classify-message`,
          {
            message: messageContent,
            user_id: userId,
            username: username
          }
        );
        console.log(response)
        if (response.data.status === 'success') {
          return response.data.category;
        } else {
          console.warn('分类API返回错误:', response.data.message);
          return 'other';
        }
      } catch (error) {
        console.error('调用分类API失败:', error);
        return 'other';
      }
    };

    // 从后端获取当前病例信息
    const fetchCurrentCase = async () => {
      try {
        const userId = localStorage.getItem('analysis_user_id') || 'default_user';
        const username = localStorage.getItem('analysis_username') || '';
        const response = await axios.get(`${backendBaseURL.value}/current-case?user_id=${userId}&username=${username}`);
        if (response.data.status === 'success') {
          // 更新病例索引和格式化数据
          const newCaseIndex = response.data.case_index;
          console.log(`获取到病例索引: ${newCaseIndex}，当前索引: ${currentCaseIndex.value}`);
          if (newCaseIndex !== currentCaseIndex.value) {
            console.log(`用户 ${username} 病例索引从 ${currentCaseIndex.value} 更新为 ${newCaseIndex}`);
          }
          currentCaseIndex.value = newCaseIndex;
          formattedCaseData.value = response.data.formatted_data || "无病例内容";
          
          // 更新总案例数量（从调试信息中获取）
          if (response.data.debug_info && response.data.debug_info.total_cases) {
            totalCases.value = response.data.debug_info.total_cases;
          }
        }
      } catch (error) {
        console.error("获取当前病例信息失败:", error);
        formattedCaseData.value = "加载病例信息失败";
      } finally {
        loading.value = false;
      }
    };

    // 启动病例信息轮询
    const startCasePolling = () => {
      // 立即获取一次
      fetchCurrentCase();
      
      // 然后每1秒轮询一次
      casePollTimer = setInterval(fetchCurrentCase, 1000);
    };
    
    // 停止病例信息轮询
    const stopCasePolling = () => {
      if (casePollTimer) {
        clearInterval(casePollTimer);
        casePollTimer = null;
      }
    };

    // 初始化函数：获取main_suit并设置初始消息
    const initializeMessages = async () => {
      // 如果对话已经开始（有多条消息），停止轮询
      if (messages.value.length > 1) {
        stopPolling();
        return;
      }

      const userId = localStorage.getItem('analysis_user_id') || 'default_user';
      const username = localStorage.getItem('analysis_username') || '';
      const currentCaseIdx = currentCaseIndex.value; // 获取当前案例索引
      
      // 检查用户是否已登录
      if (!username || username === '') {
        console.log("用户未登录，跳过主诉获取");
        return;
      }
      
      try {
        const response = await axios.get(`${backendBaseURL.value}/api/get-main-suit?user_id=${userId}&username=${username}`);
        if (response.data.status === 'success') {
            const mainSuit = response.data.main_suit;
            // 每次都从后端获取新数据，不使用缓存
            console.log(`用户 ${username} 案例 ${currentCaseIdx} 的主诉: "${mainSuit}"`);
            messages.value = [
              { 
                content: `Hello, doctor. I'm ${mainSuit}。`, 
                role: "assistant", 
                timestamp: new Date(),
                category: 'symptom'  // 初始主诉通常属于症状类别
              }
            ];
        } else {
            // 如果获取失败，使用默认消息
            messages.value = [
              { 
                content: "Hello, doctor. I'm not feeling well.", 
                role: "assistant", 
                timestamp: new Date(),
                category: 'symptom'  // 默认消息也归类为症状
              }
            ];
        }
      } catch (error) {
        console.log("获取主诉失败，使用默认消息:", error.message);
        // 如果获取失败，使用默认消息
        messages.value = [
          { 
            content: "Hello, doctor. I'm not feeling well.", 
            role: "assistant", 
            timestamp: new Date(),
            category: 'symptom'  // 默认消息也归类为症状
          }
        ];
      }
    };

    // 启动轮询
    const startPolling = () => {
      // 立即获取一次
      initializeMessages();
      
      // 然后每1秒轮询一次（减少频率，避免干扰）
      pollTimer = setInterval(initializeMessages, 1000);
    };
    
    // 停止轮询
    const stopPolling = () => {
      if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
      }
    };

    // 监听清空对话的全局事件
    const handleClearConversation = () => {
      console.log("收到清空对话事件");
      // 1. 先清空本地对话内容
      messages.value = [];
      inputMessage.value = '';
      
      // 2. 重新启动轮询（因为现在又只有一条消息了）
      startPolling();
      
      console.log("已清空对话内容并重新启动轮询");
    };

    // 监听请求最新消息的全局事件
    const handleRequestLatestMessages = (event) => {
      console.log("收到请求最新消息事件");
      const callback = event.detail?.callback;
      if (callback && typeof callback === 'function') {
        // 过滤掉系统消息，只返回用户和助手的对话
        const filteredMessages = messages.value
          .filter(msg => msg.role === 'user' || msg.role === 'assistant')
          .map(msg => ({
            content: msg.content,
            role: msg.role,
            timestamp: msg.timestamp,
            category: msg.category || 'other'  // 包含分类信息
          }));
        callback(filteredMessages);
      }
    };

    // 加载已保存的对话
    const handleLoadSavedConversation = async (event) => {
      console.log("收到加载已保存对话事件");
      const username = event.detail?.username;
      const caseIndex = event.detail?.caseIndex;
      
      if (!username || caseIndex === undefined) {
        console.error("缺少username或caseIndex参数");
        return;
      }
      
      try {
        const response = await axios.get(`${backendBaseURL.value}/api/get-saved-conversation`, {
          params: {
            username: username,
            case_index: caseIndex
          }
        });
        
        if (response.data.status === 'success' && response.data.conversation) {
          // 加载已保存的对话
          messages.value = response.data.conversation.map(msg => ({
            content: msg.content,
            role: msg.role,
            timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
            category: msg.category || 'other'
          }));
          
          console.log("已加载保存的对话:", messages.value.length, "条消息");
          
          // 停止轮询，因为已经有对话内容了
          stopPolling();
          
          // 滚动到底部
          nextTick(scrollToBottom);
        } else {
          // 如果没有已保存的对话，加载原始案例数据（初始主诉）
          console.log("没有已保存的对话，加载原始案例数据");
          messages.value = [];
          startPolling(); // 启动轮询以获取初始主诉信息
        }
      } catch (error) {
        // 加载已保存的对话失败，也加载原始案例数据
        console.log("加载已保存的对话失败，加载原始案例数据:", error.message);
        messages.value = [];
        startPolling(); // 启动轮询以获取初始主诉信息
      }
    };

    // 组件挂载时启动轮询
    onMounted(() => {
      startPolling();
      startCasePolling();
      // 添加全局事件监听
      window.addEventListener('clear-conversation', handleClearConversation);
      window.addEventListener('request-latest-messages', handleRequestLatestMessages);
      window.addEventListener('load-saved-conversation', handleLoadSavedConversation);
    });
    
    // 组件卸载前停止轮询
    onBeforeUnmount(() => {
      stopPolling();
      stopCasePolling();
      // 移除全局事件监听
      window.removeEventListener('clear-conversation', handleClearConversation);
      window.removeEventListener('request-latest-messages', handleRequestLatestMessages);
      window.removeEventListener('load-saved-conversation', handleLoadSavedConversation);
    });

    const sendMessage = async () => {

  // 1. 输入验证：检查消息是否为空或是否正在发送中
  if (!inputMessage.value.trim() || isSending.value) return;
  
  // 2. 如果这是第一条用户消息，停止轮询
  if (messages.value.length === 1) {
    stopPolling();
  }
  
  // 3. 添加用户消息到消息列表
  messages.value.push({
    content: inputMessage.value,
    role: "user",
    timestamp: new Date(),
    isLoading: false
  });
  
  // 3. 保存用户消息并清空输入框
  const userMessage = inputMessage.value;
  inputMessage.value = "";
  isSending.value = true;  // 设置发送状态
  
  try {
    // 4. 添加AI的加载状态消息（占位符）
    messages.value.push({
      content: "",
      role: "assistant",
      timestamp: new Date(),
      isLoading: true  // 标记为加载中状态
    });
    
    // 5. 确保DOM更新后滚动到底部（显示新消息）
    nextTick(scrollToBottom);
    
    // 6. 向服务端发送请求
    const userId = localStorage.getItem('analysis_user_id') || 'default_user';
    const username = localStorage.getItem('analysis_username') || '';
    const response = await axios.post(
        `${backendBaseURL.value}/get-ai-response`, 
        { 
          message: userMessage,
          user_id: userId,
          username: username
        }
      );
    
    // 7. 将加载中的占位消息替换为实际回复
    const lastIndex = messages.value.length - 1;
    const aiReply = response.data.reply;
    
    // 8. 调用分类API对AI回复进行分类
    const category = await classifyMessage(aiReply);
    
    messages.value[lastIndex] = {
      content: aiReply,
      role: "assistant",
      timestamp: new Date(),
      isLoading: false,
      category: category  // 添加分类信息
    };
  } catch (error) {
    // 8. 错误处理：替换为错误信息
    const lastIndex = messages.value.length - 1;
    messages.value[lastIndex] = {
      content: "抱歉，我暂时无法回答，请稍后再试",
      role: "assistant",
      timestamp: new Date(),
      isLoading: false,
      category: 'other'
    };
  } finally {
    // 9. 重置发送状态，并确保滚动到底部
    isSending.value = false;
    nextTick(scrollToBottom);
  }
};

    const next = async () => {
      try {
        // 1. 先清空本地对话内容
        messages.value = [];
        inputMessage.value = '';
        
        // 2. 重新启动轮询（因为现在又只有一条消息了）
        startPolling();
        
        console.log("已清空对话内容并重新启动轮询");
      } catch (error) {
        console.error("下一个请求失败", error);
      }
    };

    // 重置对话函数 - 清除所有对话，只保留初始消息
    const resetConversation = async () => {
      try {
        // 1. 清空所有消息
        messages.value = [];
        inputMessage.value = '';
        
        // 2. 重新启动轮询以获取初始主诉
        startPolling();
        
        console.log("对话已重置，等待初始消息");
      } catch (error) {
        console.error("重置对话失败", error);
      }
    };

    const scrollToBottom = () => {
      if (messageContainer.value) {
        messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
      }
    };

    // 处理文本选择
    const handleTextSelection = (event, messageIndex) => {
      const selection = window.getSelection();
      if (selection.toString().trim()) {
        // 这里可以添加文本选择后的处理逻辑
        console.log('选中文本:', selection.toString(), '消息索引:', messageIndex);
      }
      // 使用event参数避免ESLint警告
      if (event && event.target) {
        // 可以在这里添加更多事件处理逻辑
      }
    };

    // 清除选择
    const clearSelection = () => {
      window.getSelection().removeAllRanges();
    };

    defineExpose({
      messages: computed(() => messages.value.map(msg => ({
        content: msg.content,
        role: msg.role,
        timestamp: msg.timestamp
      }))),
      next,
      getLatestMessages: () => messages.value.map(msg => ({
        content: msg.content,
        role: msg.role,
        timestamp: msg.timestamp
      }))
    });

    return {
      messages,
      inputMessage,
      isSending,
      sendMessage,
      messageContainer,
      next,
      resetConversation,
      currentCaseIndex,
      totalCases,
      formattedCaseData,
      loading,
      getCategoryLabel,
      handleTextSelection,
      clearSelection
    };
  }
};
</script>

<style scoped>
.section-c-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
  min-height: 0;
}

/* 病例信息显示部分样式 */
.case-info-section {
  padding: clamp(8px, 1vh, 16px);
  background: #f8f9fa;
  border-bottom: clamp(1px, 0.1vh, 3px) solid #e9ecef;
  flex-shrink: 0;
  min-height: 0;
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: clamp(4px, 0.5vh, 12px);
  flex-wrap: wrap;
  gap: clamp(4px, 0.5vw, 8px);
}

.case-info-section h3 {
  font-size: clamp(14px, 1.5vw, 18px);
  font-weight: 600;
  color: #333;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: clamp(6px, 0.8vw, 12px);
}

.progress-indicator {
  font-size: clamp(12px, 1.2vw, 16px);
  color: #409eff;
  font-weight: 500;
  background-color: #f0f9ff;
  padding: clamp(2px, 0.3vh, 6px) clamp(6px, 0.8vw, 12px);
  border-radius: clamp(8px, 1vw, 16px);
  border: 1px solid #e6f7ff;
  white-space: nowrap;
}

.case-info-section pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  background-color: #ffffff;
  padding: clamp(8px, 1vh, 16px);
  border-radius: clamp(4px, 0.5vw, 8px);
  max-height: clamp(80px, 15vh, 150px);
  overflow: auto;
  overflow-x: hidden;
  line-height: 1.4;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  font-size: clamp(12px, 1.2vw, 16px);
  margin: 0;
  border: 1px solid #e9ecef;
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.case-info-section pre::-webkit-scrollbar {
  width: 6px;
}

.case-info-section pre::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.case-info-section pre::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.case-info-section pre::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  font-size: clamp(14px, 1.5vw, 18px);
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.chat-toolbar {
  padding: clamp(6px, 0.8vh, 12px) clamp(10px, 1.2vh, 18px);
  background: #f5f7fa;
  border-bottom: clamp(1px, 0.1vh, 2px) solid #e1e4e8;
  display: flex;
  gap: clamp(6px, 0.8vw, 12px);
  flex-shrink: 0;
}

.reset-btn {
  font-size: clamp(12px, 1.3vw, 16px);
  padding: clamp(4px, 0.6vh, 8px) clamp(8px, 1vw, 14px);
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: clamp(3px, 0.4vw, 6px);
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: clamp(4px, 0.5vw, 8px);
}

.reset-btn:hover {
  background: #f78989;
  box-shadow: 0 2px 6px rgba(245, 108, 108, 0.3);
  transform: translateY(-1px);
}

.reset-btn:active {
  transform: translateY(0);
}

.reset-btn:disabled {
  background: #b6bfc8;
  cursor: not-allowed;
  opacity: 0.6;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: clamp(12px, 1.5vh, 24px);
  min-height: 0;
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.message {
  display: flex;
  margin-bottom: clamp(16px, 2vh, 32px);
  align-items: flex-start;
}

.message.user {
  flex-direction: row-reverse;
}

.avatar {
  margin: 0 clamp(8px, 1vw, 16px);
  font-size: clamp(20px, 2.5vw, 32px);
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  background: #fff;
  padding: clamp(10px, 1.2vh, 18px);
  border-radius: clamp(8px, 1vw, 16px);
  box-shadow: 0 3px 7px rgba(0, 0, 0, 0.08);
  font-size: 1em;
  position: relative; /* 为选择按钮定位 */
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.message.user .message-content {
  background: #409eff;
  color: white;
}

/* 分类标签样式 */
.category-tag {
  position: absolute;
  top: clamp(-6px, -0.8vh, -12px);
  left: clamp(8px, 1vw, 16px);
  background: #fff;
  color: #333;
  padding: clamp(2px, 0.3vh, 4px) clamp(6px, 0.8vw, 12px);
  border-radius: clamp(8px, 1vw, 16px);
  font-size: clamp(9px, 1vw, 13px);
  font-weight: 600;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  z-index: 10;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  white-space: nowrap;
}

/* 不同分类的消息样式 */
.message.assistant.symptom .message-content {
  background: linear-gradient(135deg, #FFE4E1, #FFF5F5);
  color: #333;
  border-left: 4px solid #FF6B6B;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.1);
}

.message.assistant.sign .message-content {
  background: linear-gradient(135deg, #F0F8FF, #F8FBFF);
  color: #333;
  border-left: 4px solid #4ECDC4;
  box-shadow: 0 2px 8px rgba(78, 205, 196, 0.1);
}

.message.assistant.examination .message-content {
  background: linear-gradient(135deg, #F0F8FF, #F5F9FF);
  color: #333;
  border-left: 4px solid #91BFDB;
  box-shadow: 0 2px 8px rgba(145, 191, 219, 0.1);
}

.message.assistant.history .message-content {
  background: linear-gradient(135deg, #F8F4FF, #FDFAFF);
  color: #333;
  border-left: 4px solid #A29BFE;
  box-shadow: 0 2px 8px rgba(162, 155, 254, 0.1);
}

.message.assistant.other .message-content {
  background: linear-gradient(135deg, #FFF8E1, #FFFDF5);
  color: #333;
  border-left: 4px solid #FDCB6E;
  box-shadow: 0 2px 8px rgba(253, 203, 110, 0.1);
}

/* 分类标签在不同背景下的颜色调整 */
.message.assistant.symptom .category-tag {
  background: #FF6B6B;
  color: white;
  border-color: #FF6B6B;
  font-weight: 600;
}

.message.assistant.sign .category-tag {
  background: #4ECDC4;
  color: white;
  border-color: #4ECDC4;
  font-weight: 600;
}

.message.assistant.examination .category-tag {
  background: #91BFDB;
  color: white;
  border-color: #91BFDB;
  font-weight: 600;
}

.message.assistant.history .category-tag {
  background: #A29BFE;
  color: white;
  border-color: #A29BFE;
  font-weight: 600;
}

.message.assistant.other .category-tag {
  background: #FDCB6E;
  color: #333;
  border-color: #FDCB6E;
  font-weight: 600;
}

.message-text {
  user-select: text;
  cursor: text;
}

.message-time {
  font-size: clamp(11px, 1.2vw, 15px);
  color: #909399;
  margin-top: clamp(4px, 0.5vh, 8px);
}

.message.user .message-time {
  color: #e6f1ff;
}

.input-area {
  padding: clamp(10px, 1.2vh, 18px);
  background: white;
  border-top: clamp(1px, 0.1vh, 3px) solid #dcdfe6;
  display: flex;
  align-items: center;
  gap: clamp(6px, 0.8vw, 12px);
  width: 100%;
  box-sizing: border-box;
  flex-shrink: 0;
}

.input {
  flex: 1;
  font-size: clamp(14px, 1.5vw, 18px);
  padding: clamp(6px, 0.8vh, 10px) clamp(8px, 1vw, 14px);
  border: clamp(1px, 0.1vh, 2px) solid #dcdfe6;
  border-radius: clamp(4px, 0.5vw, 8px);
  outline: none;
  min-height: clamp(32px, 4vh, 40px);
}

.send-btn {
  font-size: clamp(13px, 1.4vw, 17px);
  padding: clamp(6px, 0.8vh, 10px) clamp(12px, 1.5vw, 20px);
  background: #409eff;
  color: white;
  border: none;
  border-radius: clamp(4px, 0.5vw, 8px);
  cursor: pointer;
  transition: background 0.2s;
  min-height: clamp(32px, 4vh, 40px);
  white-space: nowrap;
}

.send-btn:disabled {
  background: #b6bfc8;
  cursor: not-allowed;
}

/* 选择按钮样式 */
.selection-button {
  width: clamp(20px, 2.5vw, 28px);
  height: clamp(20px, 2.5vw, 28px);
  background: #4CAF50;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: clamp(12px, 1.5vw, 18px);
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  transition: all 0.2s ease;
}

.selection-button:hover {
  background: #45a049;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* 响应式设计 - 小屏幕适配 */
@media (max-width: 768px) {
  .case-header {
    flex-direction: column;
    align-items: flex-start;
    gap: clamp(4px, 1vh, 8px);
  }
  
  .progress-indicator {
    align-self: flex-end;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .avatar {
    font-size: clamp(18px, 4vw, 24px);
  }
  
  .input-area {
    padding: clamp(8px, 1vh, 12px);
    gap: clamp(4px, 1vw, 8px);
  }
  
  .input, .send-btn {
    font-size: clamp(12px, 3vw, 16px);
    min-height: clamp(28px, 6vh, 36px);
  }
}

/* 超宽屏幕适配 */
@media (min-width: 1920px) {
  .case-info-section {
    padding: clamp(16px, 1.5vh, 24px);
  }
  
  .chat-messages {
    padding: clamp(20px, 2vh, 32px);
  }
  
  .message {
    margin-bottom: clamp(24px, 2.5vh, 40px);
  }
  
  .input-area {
    padding: clamp(16px, 1.5vh, 24px);
  }
}
</style>