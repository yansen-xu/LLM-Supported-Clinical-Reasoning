<template>
  <div class="root-container">
    <!-- 登录页面 -->
    <LoginPage 
      v-if="!isLoggedIn" 
      @start-analysis="handleStartAnalysis" 
    />
    
    <!-- 分析界面 -->
    <div v-else class="grid-container analysis-version">
      <div class="user-info">
        <span class="username">Welcom, {{ username }}</span>
        <button class="evaluation-btn" @click="goToEvaluation">Go to Evaluation</button>
        <button class="logout-btn" @click="logout">Log out</button>
      </div>
      
      <C ref="sectionCRef" class="c-container" />
      <D class="d-container"
         :messages="cData.messages"
         @clearAll="clearAllContent"
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from "vue";
import C from "./SectionC.vue";
import D from "./SectionD.vue";
import LoginPage from "./LoginPage.vue";

export default {
  components: { C, D, LoginPage },
  setup() {
    const sectionCRef = ref(null);
    const cData = ref({ messages: [] });
    const isLoggedIn = ref(false);
    const username = ref('');

    // 检查是否已登录
    const checkLoginStatus = () => {
      // 混合模式下，直接检查analysis_username即可
      const savedUsername = localStorage.getItem('analysis_username');
      if (savedUsername) {
        // 如果有保存的用户名，直接认为已登录
        username.value = savedUsername;
        isLoggedIn.value = true;
        // 确保session标记也被设置
        sessionStorage.setItem('analysis_session', 'true');
      } else {
        // 没有保存的用户名则需要重新登录
        isLoggedIn.value = false;
        username.value = '';
      }
    };

    // 处理开始分析
    const handleStartAnalysis = async (user) => {
      username.value = user;
      isLoggedIn.value = true;
      // 生成唯一的用户ID
      const userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('analysis_user_id', userId);
      // 设置会话存储，标记当前会话已登录
      sessionStorage.setItem('analysis_session', 'true');
      localStorage.setItem('analysis_username', user);
    };

    // 退出登录
    const logout = () => {
      localStorage.removeItem('analysis_username');
      localStorage.removeItem('analysis_user_id');
      sessionStorage.removeItem('analysis_session');
      isLoggedIn.value = false;
      username.value = '';
    };

    // 检查5001端口是否开放
    const checkPort5001 = async () => {
      try {
        // 尝试连接到5001端口的一个简单端点来检查服务是否运行
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 3000); // 3秒超时
        
        const response = await fetch('http://localhost:5001/api/evaluation/health', {
          signal: controller.signal
        });
        
        clearTimeout(timeout);
        return response.ok;
      } catch (error) {
        return false;
      }
    };

    // 跳转到evaluation页面
    const goToEvaluation = async () => {
      // 检查5001端口是否开放
      const isPort5001Open = await checkPort5001();
      
      if (!isPort5001Open) {
        alert('Evaluation backend service is not running. Please ensure backend is started with "python run_all.py".');
        return;
      }
      
      if (window.__SWITCH_VERSION__) {
        window.__SWITCH_VERSION__('evaluation');
      } else {
        console.error('Version switch function not found');
      }
    };

    // 收集子组件数据
    const collectData = () => {
      if (sectionCRef.value) {
        // 使用新的方法来获取最新的对话数据
        if (sectionCRef.value.getLatestMessages) {
          cData.value.messages = sectionCRef.value.getLatestMessages();
        } else {
          const currentMessages = sectionCRef.value.messages.value || sectionCRef.value.messages;
          cData.value.messages = currentMessages;
        }
        console.log('收集到的对话数据:', cData.value.messages);
      }
    };

    // 每次挂载时收集一次
    onMounted(async () => {
      // 检查登录状态
      checkLoginStatus();
      
      // 只有在已登录状态下才清空评估相关的状态
      if (isLoggedIn.value) {
        localStorage.removeItem('evaluation_current_case_id');
        sessionStorage.removeItem('evaluation_session');
        
        // 重置组件数据
        cData.value = { messages: [] };
        
        nextTick(collectData);
      }
      
      // 将cData暴露到全局，供其他组件访问
      window.cData = cData;
    });

    // 清空所有内容（供D区调用）
    const clearAllContent = async () => {
      console.log('清空内容');
    };

    // 强制重新收集数据（供D区调用）
    const forceCollectData = () => {
      collectData();
      return cData.value.messages;
    };

    // 将collectData暴露到全局
    window.collectData = collectData;

    return {
      sectionCRef,
      cData,
      isLoggedIn,
      username,
      handleStartAnalysis,
      logout,
      goToEvaluation,
      clearAllContent,
      forceCollectData
    };
  }
};
</script>

<style lang="less">
.root-container {
  width: 100vw;
  height: 100vh;
  padding: 0;
  box-sizing: border-box;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
}

.user-info {
  position: absolute;
  top: 1vh;
  right: 1vw;
  display: flex;
  align-items: center;
  gap: 1vw;
  z-index: 1000;
  
  .username {
    color: #333;
    font-weight: 500;
    font-size: clamp(14px, 1.5vw, 18px);
  }
  
  .evaluation-btn {
    padding: clamp(6px, 0.8vh, 10px) clamp(12px, 1.2vw, 16px);
    background: #2196F3;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: clamp(12px, 1.2vw, 16px);
    transition: all 0.3s ease;
    
    &:hover {
      background: #1976D2;
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
    }
    
    &:active {
      transform: translateY(0);
    }
  }
  
  .logout-btn {
    padding: clamp(6px, 0.8vh, 10px) clamp(12px, 1.2vw, 16px);
    background: #ff4757;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: clamp(12px, 1.2vw, 16px);
    transition: all 0.3s ease;
    
    &:hover {
      background: #ff3742;
      transform: translateY(-1px);
    }
  }
}

.grid-container.analysis-version {
  display: grid;
  grid-template-columns: 1.2fr 1.8fr;
  grid-template-rows: 1fr;
  gap: 0.3vw;
  width: 100%;
  height: 100vh;
  background-color: #ffffff;
  position: relative;
  padding: 0.5vh 0.5vw;
  overflow: hidden;

  > [class$="-container"] {
    border: clamp(2px, 0.3vw, 4px) solid #B6BFC8;
    border-radius: clamp(6px, 0.8vw, 10px);
    box-sizing: border-box;
    overflow: hidden;
    min-width: 0;
    min-height: 0;
    position: relative;

    &::after {
      content: "";
      display: block;
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      pointer-events: none;
      z-index: -1;
    }
  }
}

.analysis-version .c-container {
  grid-column: 1;
  grid-row: 1;
}

.analysis-version .d-container {
  grid-column: 2;
  grid-row: 1;
}

/* 响应式设计 - 小屏幕适配 */
@media (max-width: 768px) {
  .grid-container.analysis-version {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 0.5vh;
  }
  
  .analysis-version .c-container {
    grid-column: 1;
    grid-row: 1;
  }
  
  .analysis-version .d-container {
    grid-column: 1;
    grid-row: 2;
  }
  
  .analysis-version .user-info {
    top: 0.5vh;
    right: 0.5vw;
    
    .username {
      font-size: clamp(12px, 3vw, 16px);
    }
    
    .logout-btn {
      padding: clamp(4px, 1vh, 8px) clamp(8px, 2vw, 12px);
      font-size: clamp(10px, 2.5vw, 14px);
    }
  }
}

/* 超宽屏幕适配 */
@media (min-width: 1920px) {
  .grid-container.analysis-version {
    gap: 0.5vw;
    padding: 1vh 1vw;
  }
  
  .analysis-version .user-info {
    top: 1.5vh;
    right: 1.5vw;
    
    .username {
      font-size: clamp(16px, 1vw, 20px);
    }
    
    .logout-btn {
      padding: clamp(8px, 1vh, 12px) clamp(16px, 1.5vw, 20px);
      font-size: clamp(14px, 1vw, 18px);
    }
  }
}
</style>
