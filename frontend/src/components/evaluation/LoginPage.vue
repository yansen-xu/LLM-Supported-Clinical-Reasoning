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
        <h3>我们是上海科技大学ViSeerLAB组，目前在探究诊断场景下感知到的医生和AI的能力。现诚邀您参与我们的评估实验！</h3>
      </div>
      
      <!-- 注意事项容器 -->
      <div class="notice-container">
        <div class="notice-header">
          <i class="notice-icon">📋</i>
          <h4>注意事项</h4>
        </div>
        <div class="notice-content">
          <p>为减少实验非目标性差异，我们对所有医生角色的回答进行了技术性处理，主要包括：</p>
          <ul>
            <li>对错别字进行检查与纠正</li>
            <li>对措辞进行礼貌化调整</li>
            <li>对医学检查相关提问的表述进行统一</li>
          </ul>
        </div>
      </div>
      
      <div class="login-form">
        <div class="input-group">
          <label for="username">姓名：</label>
          <input 
            id="username"
            v-model="username" 
            type="text" 
            placeholder="请输入您的姓名"
            @keyup.enter="startEvaluation"
            :class="{ 'error': showError && !username.trim() }"
          />
          <span v-if="showError && !username.trim()" class="error-message">请输入姓名</span>
        </div>
        
        <div class="input-group">
          <label for="caseGroup">作答题目：</label>
          <select 
            id="caseGroup"
            v-model="selectedCaseGroup" 
            :class="{ 'error': showError && !selectedCaseGroup }"
          >
            <option value="">请选择作答题目</option>
            <option value="all">所有</option>
            <option value="neurology">神经组</option>
            <option value="rare">罕见病组</option>
            <option value="common">常见病组</option>
            <option value="neurology_rare">神经+罕见病</option>
            <option value="neurology_common">神经+常见病</option>
            <option value="rare_common">罕见病+常见病</option>
          </select>
          <span v-if="showError && !selectedCaseGroup" class="error-message">请选择作答题目</span>
        </div>
        
        <button 
          class="start-btn" 
          @click="startEvaluation"
          :disabled="!isFormValid"
        >
          开始作答
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
      showError: false,
      selectedCaseGroup: ''
    }
  },
  computed: {
    isFormValid() {
      return this.username.trim() !== '' && this.selectedCaseGroup !== '';
    }
  },
  methods: {
    startEvaluation() {
      if (!this.isFormValid) {
        this.showError = true;
        return;
      }
      
      this.showError = false;
      
      // 构建用户信息对象
      const userInfo = {
        username: this.username.trim(),
        caseGroup: this.selectedCaseGroup
      };
      
      // 将用户信息存储到localStorage
      localStorage.setItem('evaluation_username', userInfo.username);
      localStorage.setItem('evaluation_user_info', JSON.stringify(userInfo));
      
      // 触发开始评估事件，传递完整的用户信息
      this.$emit('start-evaluation', userInfo);
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
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 50%, #fdcb6e 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 15px; /* 20px * 0.737 = 15px */
  box-shadow: 0 18px 37px rgba(0, 0, 0, 0.15); /* 25px * 0.737 = 18px, 50px * 0.737 = 37px */
  padding: 74px; /* 100px * 0.737 = 74px */
  width: 100%;
  max-width: 590px; /* 800px * 0.737 = 590px */
  text-align: center;
}

.logo-section {
  margin-bottom: 24px; /* 32px * 0.737 = 24px */
}

.logo-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px; /* 20px * 0.737 = 15px */
  flex-wrap: wrap;
}

.lab-logo {
  height: 74px; /* 100px * 0.737 = 74px */
  width: auto;
  object-fit: contain;
}

.red-logo {
  height: 59px; /* 80px * 0.737 = 59px */
  width: auto;
  object-fit: contain;
}

.login-header {
  margin-bottom: 37px; /* 50px * 0.737 = 37px */
  
  h3 {
    color: #333;
    font-size: 21px; /* 28px * 0.737 = 21px */
    font-weight: 600;
    margin-bottom: 12px; /* 16px * 0.737 = 12px */
    line-height: 1.4;
  }
  
  p {
    color: #666;
    font-size: 13px; /* 18px * 0.737 = 13px */
    margin: 0;
    line-height: 1.5;
  }
}

.notice-container {
  background-color: #f9f9f9;
  border-radius: 8px; /* 10px * 0.737 = 8px */
  padding: 15px; /* 20px * 0.737 = 15px */
  margin-bottom: 22px; /* 30px * 0.737 = 22px */
  text-align: left;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05); /* 2px * 0.737 = 1px, 8px * 0.737 = 6px */

  .notice-header {
    display: flex;
    align-items: center;
    margin-bottom: 11px; /* 15px * 0.737 = 11px */
    color: #333;
    font-size: 15px; /* 20px * 0.737 = 15px */
    font-weight: 600;

    .notice-icon {
      font-size: 18px; /* 24px * 0.737 = 18px */
      margin-right: 8px; /* 10px * 0.737 = 8px */
    }
  }

  .notice-content {
    color: #555;
    font-size: 12px; /* 16px * 0.737 = 12px */
    line-height: 1.6;

    p {
      margin-bottom: 8px; /* 10px * 0.737 = 8px */
    }

    ul {
      padding-left: 15px; /* 20px * 0.737 = 15px */
      list-style-type: disc;
    }

    li {
      margin-bottom: 4px; /* 5px * 0.737 = 4px */
    }
  }
}

.login-form {
  .input-group {
    margin-bottom: 22px; /* 30px * 0.737 = 22px */
    text-align: left;
    
    label {
      display: block;
      margin-bottom: 9px; /* 12px * 0.737 = 9px */
      color: #333;
      font-weight: 500;
      font-size: 13px; /* 18px * 0.737 = 13px */
    }
    
    input, select {
      width: 100%;
      padding: 15px; /* 20px * 0.737 = 15px */
      border: 1px solid #e1e5e9; /* 2px * 0.737 = 1px */
      border-radius: 8px; /* 10px * 0.737 = 8px */
      font-size: 13px; /* 18px * 0.737 = 13px */
      transition: all 0.3s ease;
      box-sizing: border-box;
      background-color: white;
      
      &:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1); /* 3px * 0.737 = 2px */
      }
      
      &.error {
        border-color: #ff4757;
      }
      
      &::placeholder {
        color: #999;
      }
    }
    
    select {
      cursor: pointer;
      
      option {
        padding: 8px; /* 10px * 0.737 = 8px */
      }
    }
    
    .error-message {
      color: #ff4757;
      font-size: 12px; /* 16px * 0.737 = 12px */
      margin-top: 8px; /* 10px * 0.737 = 8px */
      display: block;
    }
  }
  
  .start-btn {
    width: 100%;
    padding: 15px; /* 20px * 0.737 = 15px */
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px; /* 10px * 0.737 = 8px */
    font-size: 15px; /* 20px * 0.737 = 15px */
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: 15px; /* 20px * 0.737 = 15px */
    
    &:hover:not(:disabled) {
      transform: translateY(-1px); /* -2px * 0.737 = -1px */
      box-shadow: 0 6px 19px rgba(102, 126, 234, 0.3); /* 8px * 0.737 = 6px, 25px * 0.737 = 19px */
    }
    
    &:disabled {
      background: #ccc;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 37px 22px; /* 50px * 0.737 = 37px, 30px * 0.737 = 22px */
    max-width: 95%;
  }
  
  .login-header h3 {
    font-size: 21px; /* 28px * 0.737 = 21px */
  }
  
  .login-header p {
    font-size: 12px; /* 16px * 0.737 = 12px */
  }
  
  .logo-container {
    gap: 15px; /* 20px * 0.737 = 15px */
  }
  
  .lab-logo {
    height: 52px; /* 70px * 0.737 = 52px */
  }
  
  .red-logo {
    height: 44px; /* 60px * 0.737 = 44px */
  }
}
</style>
