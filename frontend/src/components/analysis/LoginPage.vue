 <template>
  <div class="login-container">
    <div class="login-card">
      <!-- Logo区域 -->
      <div class="logo-section">
        <div class="logo-container">
          <img src="@/assets/logo_red.svg" alt="Logo" class="red-logo" />
          <img src="@/assets/实验室logo.png" alt="实验室Logo" class="lab-logo" />
        </div>
      </div>
      
      <div class="login-header">
        <h3>我们是上海科技大学ViSeerLAB组，目前在探究诊断场景下感知到的医生和AI的能力。现诚邀您作为被试参与我们的实验！</h3>
        <p>请输入您的姓名开始作答，系统将自动加载您未完成的案例，默认显示第一个案例。我们将全程保护您的隐私！</p>
      </div>
      
      <div class="login-form">
        <div class="input-group">
          <label for="username">Name: </label>
          <input 
            id="username"
            v-model="username" 
            type="text" 
            placeholder="请输入您的姓名"
            @keyup.enter="startAnalysis"
            :class="{ 'error': showError }"
          />
          <span v-if="showError" class="error-message">Please input your name</span>
        </div>
        
        <button 
          class="start-btn" 
          @click="startAnalysis"
          :disabled="!username.trim()"
        >
          Begin
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginPage',
  data() {
    return {
      username: '',
      showError: false
    }
  },
  methods: {
    startAnalysis() {
      if (!this.username.trim()) {
        this.showError = true;
        return;
      }
      
      this.showError = false;
      // 将用户名存储到localStorage
      localStorage.setItem('analysis_username', this.username.trim());
      // 触发开始分析事件
      this.$emit('start-analysis', this.username.trim());
    }
  }
}
</script>

<style lang="less" scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: clamp(12px, 2vh, 24px);
}

.login-card {
  background: white;
  border-radius: clamp(16px, 2vw, 24px);
  box-shadow: 0 clamp(20px, 3vh, 32px) clamp(40px, 5vh, 64px) rgba(0, 0, 0, 0.15);
  padding: clamp(60px, 8vh, 120px);
  width: 100%;
  max-width: clamp(600px, 80vw, 900px);
  text-align: center;
}

.logo-section {
  margin-bottom: clamp(24px, 3vh, 40px);
}

.logo-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: clamp(12px, 2vw, 24px);
  flex-wrap: wrap;
}

.lab-logo {
  height: clamp(60px, 8vh, 120px);
  width: auto;
  object-fit: contain;
}

.red-logo {
  height: clamp(50px, 6vh, 100px);
  width: auto;
  object-fit: contain;
}

.login-header {
  margin-bottom: clamp(32px, 5vh, 64px);
  
  h3 {
    color: #333;
    font-size: clamp(20px, 3vw, 32px);
    font-weight: 600;
    margin-bottom: clamp(12px, 2vh, 20px);
    line-height: 1.4;
  }
  
  p {
    color: #666;
    font-size: clamp(14px, 2vw, 20px);
    margin: 0;
    line-height: 1.5;
  }
}

.login-form {
  .input-group {
    margin-bottom: clamp(24px, 4vh, 48px);
    text-align: left;
    
    label {
      display: block;
      margin-bottom: clamp(8px, 1.5vh, 16px);
      color: #333;
      font-weight: 500;
      font-size: clamp(14px, 2vw, 20px);
    }
    
    input {
      width: 100%;
      padding: clamp(12px, 2vh, 24px);
      border: clamp(1px, 0.2vh, 3px) solid #e1e5e9;
      border-radius: clamp(8px, 1vw, 12px);
      font-size: clamp(14px, 2vw, 20px);
      transition: all 0.3s ease;
      box-sizing: border-box;
      
      &:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 clamp(2px, 0.3vw, 4px) rgba(102, 126, 234, 0.1);
      }
      
      &.error {
        border-color: #ff4757;
      }
      
      &::placeholder {
        color: #999;
      }
    }
    
    .error-message {
      color: #ff4757;
      font-size: clamp(12px, 1.5vw, 18px);
      margin-top: clamp(6px, 1vh, 12px);
      display: block;
    }
  }
  
  .start-btn {
    width: 100%;
    padding: clamp(12px, 2vh, 24px);
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: clamp(8px, 1vw, 12px);
    font-size: clamp(14px, 2vw, 22px);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 clamp(6px, 1vh, 12px) clamp(20px, 3vh, 32px) rgba(102, 126, 234, 0.3);
    }
    
    &:disabled {
      background: #ccc;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }
  }
}

@media (max-width: 768px) {
  .login-card {
    padding: clamp(40px, 6vh, 60px) clamp(24px, 4vw, 32px);
    max-width: 95%;
  }
  
  .login-header h3 {
    font-size: clamp(18px, 4vw, 24px);
  }
  
  .login-header p {
    font-size: clamp(12px, 2.5vw, 16px);
  }
  
  .logo-container {
    gap: clamp(8px, 2vw, 16px);
  }
  
  .lab-logo {
    height: clamp(40px, 6vh, 60px);
  }
  
  .red-logo {
    height: clamp(35px, 5vh, 50px);
  }
  
  .login-form .input-group {
    margin-bottom: clamp(16px, 3vh, 32px);
  }
  
  .login-form .start-btn {
    padding: clamp(10px, 2.5vh, 18px);
    font-size: clamp(12px, 3vw, 18px);
  }
}

@media (min-width: 1920px) {
  .login-card {
    padding: clamp(80px, 10vh, 140px);
    max-width: clamp(700px, 70vw, 1000px);
  }
  
  .login-header h3 {
    font-size: clamp(24px, 2.5vw, 36px);
  }
  
  .login-header p {
    font-size: clamp(16px, 1.8vw, 24px);
  }
  
  .lab-logo {
    height: clamp(80px, 10vh, 140px);
  }
  
  .red-logo {
    height: clamp(70px, 8vh, 120px);
  }
}
</style>