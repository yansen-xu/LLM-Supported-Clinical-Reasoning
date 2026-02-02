<template>
  <div class="root-container">
    <!-- 评估界面 -->
    <div v-if="isLoggedIn && !showThankYou" class="grid-container evaluation-version">
      <A 
        ref="sectionA"
        class="a-container" 
        :username="username" 
        :currentCaseId="currentCaseId"
        :navigationDirection="navigationDirection"
        @evaluator-selected="handleEvaluatorSelected"
        @available-evaluators-changed="handleAvailableEvaluatorsChanged"
      />
      <B 
        ref="sectionB"
        class="b-container" 
        :username="username" 
        :currentCaseId="currentCaseId"
        :selectedEvaluator="selectedEvaluator" 
        :key="caseKey"
        @back-to-analysis="handleBackToAnalysis"
      />
      <C 
        class="c-container" 
        :username="username"
        :currentCaseId="currentCaseId"
        :selectedEvaluator="selectedEvaluator"
        @dimension-deleted="handleDimensionDeleted"
        @scoring-status-changed="handleScoringStatusChanged"
        @score-updated="handleScoreUpdated"
      />
      <D 
        class="d-container" 
        :selectedEvaluator="selectedEvaluator"
        :username="username"
        :currentCaseId="currentCaseId"
      />
      <E 
        ref="sectionE"
        class="e-container" 
        :username="username" 
        @case-changed="handleCaseChanged"
        @show-thank-you="showThankYouPage"
        :availableEvaluatorsCount="availableEvaluatorsCount"
        :selectedEvaluator="selectedEvaluator"
      />
    </div>
    
    <!-- 感谢页面 -->
    <ThankYouPage 
      v-else-if="showThankYou"
      @return-to-evaluation="returnToEvaluation"
    />
  </div>
</template>

<script>
import A from "./SectionA.vue";
import B from "./SectionB.vue";
import C from "./SectionC.vue";
import D from "./SectionD.vue";
import E from "./SectionE.vue";
import ThankYouPage from "./ThankYouPage.vue";

export default {
  components: { A, B, C, D, E, ThankYouPage },
  data() {
    return {
      isLoggedIn: false,
      username: '',
      caseKey: 0,
      currentCaseId: 1,
      selectedEvaluator: null,
      // 感谢页面显示状态
      showThankYou: false,
      // 导航方向
      navigationDirection: null,
      // availableEvaluators数量
      availableEvaluatorsCount: 0
    }
  },
  computed: {
    // 移除计算属性，改为使用data属性
  },
  mounted() {
    // Check if username is passed from analysis (mixed mode)
    const savedUsername = localStorage.getItem('analysis_username');
    if (savedUsername) {
      // Mixed mode: use analysis username
      this.username = savedUsername;
      this.initializeEvaluation(savedUsername);
      this.isLoggedIn = true;
      // Get current case info and refresh component state
      this.getCurrentCaseInfo().then(async () => {
        this.$nextTick(async () => {
          if (this.$refs.sectionA) {
            this.$refs.sectionA.checkCaseSortingStatus();
          }
          if (this.$refs.sectionB) {
            this.$refs.sectionB.fetchCaseInfo();
          }
          if (this.$refs.sectionE) {
            this.$refs.sectionE.getAnswer(true);
          }
        });
      });
    } else {
      // Standalone mode: use timestamp as username
      const timestamp = Date.now().toString();
      this.username = timestamp;
      this.initializeEvaluation(timestamp);
      this.isLoggedIn = true;
      // Get current case info and refresh component state
      this.getCurrentCaseInfo().then(async () => {
        this.$nextTick(async () => {
          if (this.$refs.sectionA) {
            this.$refs.sectionA.checkCaseSortingStatus();
          }
          if (this.$refs.sectionB) {
            this.$refs.sectionB.fetchCaseInfo();
          }
          if (this.$refs.sectionE) {
            this.$refs.sectionE.getAnswer(true);
          }
        });
      });
    }
  },
  methods: {
    async initializeEvaluation(username) {
      try {
        // Create user
        const createResponse = await fetch('/api/evaluation/create-user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username })
        });
        
        if (!createResponse.ok) {
          console.error('Failed to create user:', createResponse.statusText);
        }
        
        // Initialize user
        const initResponse = await fetch('/api/evaluation/init-user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username })
        });
        
        if (!initResponse.ok) {
          console.error('Failed to initialize user:', initResponse.statusText);
          return;
        }
        
        const initData = await initResponse.json();
        console.log('User initialization successful:', initData);
      } catch (error) {
        console.error('User initialization failed:', error);
      }
    },

    async handleStartEvaluation(userInfo) {
      try {
        // Reset all state
        this.selectedEvaluator = null;
        this.navigationDirection = null;
        this.caseKey = 0;
        
        // Call backend API to create and initialize user
        const createResponse = await fetch('/api/evaluation/create-user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            username: userInfo.username
          })
        });
        
        if (!createResponse.ok) {
          console.error('Failed to create user:', createResponse.statusText);
        }
        
        const initResponse = await fetch('/api/evaluation/init-user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            username: userInfo.username
          })
        });
        
        if (!initResponse.ok) {
          console.error('Failed to initialize user:', initResponse.statusText);
          return;
        }
        
        const initData = await initResponse.json();
        console.log('User initialization successful:', initData);
        
        this.username = userInfo.username;
        this.isLoggedIn = true;
        
        // Get user's actual current case info
        await this.getCurrentCaseInfo();
        
        // Force refresh component state
        this.$nextTick(async () => {
          if (this.$refs.sectionA) {
            this.$refs.sectionA.checkCaseSortingStatus();
          }
          if (this.$refs.sectionB) {
            this.$refs.sectionB.fetchCaseInfo();
          }
          if (this.$refs.sectionE) {
            this.$refs.sectionE.getAnswer(true);
          }
          // Initialization complete
        });
      } catch (error) {
        console.error('User initialization failed:', error);
        alert('Login failed, please try again');
      }
    },
    
    handleCaseChanged(result) {
      console.log('案例已改变:', result);
      // 更新当前caseId - 从case文件名中提取数字
      const caseName = result.case_name;
      if (caseName && caseName.startsWith('case')) {
        this.currentCaseId = parseInt(caseName.replace('case', ''));
      } else {
        // 如果没有case_name，使用索引+1作为备选
        this.currentCaseId = result.current_index + 1;
      }
      console.log('更新后的currentCaseId:', this.currentCaseId);
      
      // 保存当前案例ID到localStorage
      localStorage.setItem('evaluation_current_case_id', this.currentCaseId.toString());
      
      // 保存导航方向
      this.navigationDirection = result.navigationDirection;
      console.log('导航方向:', this.navigationDirection);
      // 清除选中的评估者，让SectionA重新选择默认的第一个
      this.selectedEvaluator = null;
      // 通过改变key来强制重新渲染SectionB组件
      this.caseKey++;
      // 重置评分状态，因为案例改变了
      // 重置完成
      
      // 通知SectionA检查新case的排序状态
      this.$nextTick(() => {
        if (this.$refs.sectionA) {
          this.$refs.sectionA.checkCaseSortingStatus();
        }
      });
    },

    async getCurrentCaseInfo() {
      try {
        const response = await fetch(`/api/evaluation/current-case?username=${this.username}`);
        const data = await response.json();
        
        if (data.status === 'success') {
          // 从case_filename中提取case编号
          const caseFilename = data.case_filename;
          if (caseFilename && caseFilename.startsWith('case')) {
            this.currentCaseId = parseInt(caseFilename.replace('case', ''));
          } else {
            this.currentCaseId = data.case_index + 1;
          }
          console.log('初始化currentCaseId:', this.currentCaseId);
          
          // 保存当前案例ID到localStorage
          localStorage.setItem('evaluation_current_case_id', this.currentCaseId.toString());
        }
      } catch (error) {
        console.error('获取当前案例信息失败:', error);
        // 默认使用case1
        this.currentCaseId = 1;
      }
    },

    async handleEvaluatorSelected(evaluatorData) {
      console.log('评估者已选择:', evaluatorData);
      this.selectedEvaluator = evaluatorData;
      // 检查当前案例状态
    },
    
    // 处理维度删除
    handleDimensionDeleted(dimensionId) {
      console.log(`维度 ${dimensionId} 被删除`);
    },

    // 处理评分状态变化
    handleScoringStatusChanged(statusData) {
      // 处理来自SectionC的评分状态变化
      console.log('App.vue 收到评分状态变化:', statusData);
      // 将事件传递给SectionE
      if (this.$refs.sectionE) {
        this.$refs.sectionE.handleScoringStatusChanged(statusData);
      }
    },

    async handleScoreUpdated() {
      // 当评分更新时，通知SectionE重新检查评分状态
      console.log('App.vue 收到评分更新事件');
      if (this.$refs.sectionE) {
        this.$refs.sectionE.handleScoreUpdated();
      }
    },

    // 监听SectionA中availableEvaluators的变化
    handleAvailableEvaluatorsChanged(count) {
      this.availableEvaluatorsCount = count;
      // 强制更新SectionE组件
      this.$nextTick(() => {
        if (this.$refs.sectionE) {
          this.$refs.sectionE.$forceUpdate();
        }
      });
    },



    // 同步获取当前维度数据
    getCurrentDimensionsSync() {
      try {
        // 从localStorage获取维度数据
        const savedDimensions = JSON.parse(localStorage.getItem(`evaluation_dimensions_${this.username}`) || '[]');
        if (savedDimensions.length > 0) {
          return savedDimensions;
        }
        
        // 如果没有保存的数据，返回默认维度结构
        return [
          { category: "问诊过程逻辑性", dimension: "对话提问是否清晰连贯,前后有逻辑" },
          { category: "诊断结论正确性", dimension: "最终诊断是否正确" },
          { category: "诊断结论全面性", dimension: "次要诊断是否全面" },
          { category: "推理过程合理性", dimension: "诊断推理过程是否合理" },
          { category: "治疗原则合理性", dimension: "治疗建议是否恰当" },
          { category: "治疗原则全面性", dimension: "治疗是否全面" },
          { category: "临床专业感知", dimension: "从患者角度考量,这位医生的诊疗行为是否可被接受" },
          { category: "AI感知", dimension: "您认为这位'医生'是AI扮演的,还是真实的人类医生?" }
        ];
      } catch (error) {
        console.error('获取维度数据出错:', error);
        return [];
      }
    },
    
    handleBackToAnalysis() {
      // Switch back to analysis mode
      if (window.__SWITCH_VERSION__) {
        window.__SWITCH_VERSION__('analysis');
      } else {
        console.error('Version switch function not found');
      }
    },
    
    handleLogout() {
      // 清除登录状态，但保留分析应用的用户名信息
      // 因为evaluation现在与analysis共享登录
      localStorage.removeItem('evaluation_current_case_id');
      
      this.isLoggedIn = false;
      this.username = '';
      this.caseKey = 0;
      this.currentCaseId = 1;
      this.selectedEvaluator = null;
      this.showThankYou = false;
      this.navigationDirection = null;
      
      // 询问用户是否返回analysis页面
      setTimeout(() => {
        if (window.confirm('是否返回Analysis页面？')) {
          if (window.__SWITCH_VERSION__) {
            window.__SWITCH_VERSION__('analysis');
          } else {
            console.error('版本切换函数未找到');
          }
        }
      }, 100);
    },
    
    // 显示感谢页面
    showThankYouPage() {
      this.showThankYou = true;
    },
    
    // 返回评估界面
    async returnToEvaluation() {
      this.showThankYou = false;
      
      try {
        // 重新初始化用户状态
        const initResponse = await fetch('/api/evaluation/init-user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: this.username,
            user_id: this.username
          })
        });
        
        if (initResponse.ok) {
          console.log('用户状态重新初始化成功');
        }
        
        // 重新获取当前案例信息
        await this.getCurrentCaseInfo();
        
        // 重置导航方向
        this.navigationDirection = null;
        
        // 清除选中的评估者
        this.selectedEvaluator = null;
        
        // 强制重新渲染组件
        this.caseKey++;
        
        // 通知各个组件重新加载数据
        this.$nextTick(() => {
          if (this.$refs.sectionA) {
            this.$refs.sectionA.checkCaseSortingStatus();
          }
          if (this.$refs.sectionB) {
            this.$refs.sectionB.fetchCaseInfo();
          }
          if (this.$refs.sectionE) {
            this.$refs.sectionE.getAnswer(true);
          }
        });
        
        console.log('已返回评估界面，重新加载案例数据');
      } catch (error) {
        console.error('返回评估界面时出错:', error);
      }
    }
  }
};
</script>

<style lang="less">
.root-container {
  width: 100%;
  height: 100vh;
  padding: clamp(6px, 0.8vw, 12px);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.grid-container.evaluation-version {
  display: grid;
  grid-template-columns: 1fr 1.9fr 2fr;
  grid-template-rows: 2fr 1fr 1fr 3.5fr;
  gap: clamp(1px, 0.2vw, 4px);
  width: 100%;
  height: 100%;
  flex: 1;
  min-height: 0;
  background-color: #ffffff;

  > [class$="-container"] {
    border: clamp(1px, 0.2vw, 3px) solid #B6BFC8;
    border-radius: clamp(3px, 0.6vw, 8px);
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

.evaluation-version .a-container {
  grid-column: 1;
  grid-row: 1 / span 4;
}

.evaluation-version .b-container {
  grid-column: 2;
  grid-row: 1 / span 3;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.evaluation-version .c-container {
  grid-column: 2;
  grid-row: 4;
}

.evaluation-version .d-container {
  grid-column: 3;
  grid-row: 1 / span 1;
}

.evaluation-version .e-container {
  grid-column: 3;
  grid-row: 2 / span 3;
}

/* 响应式断点 */
@media (max-width: 1200px) {
  .grid-container.evaluation-version {
    gap: clamp(1px, 0.2vw, 4px);
    
    > [class$="-container"] {
      border-width: clamp(1px, 0.2vw, 3px);
      border-radius: clamp(3px, 0.6vw, 8px);
    }
  }
}

@media (max-width: 768px) {
  .root-container {
    padding: clamp(4px, 0.8vw, 12px);
  }
  
  .grid-container.evaluation-version {
    gap: clamp(1px, 0.15vw, 3px);
    
    > [class$="-container"] {
      border-width: clamp(1px, 0.15vw, 2px);
      border-radius: clamp(2px, 0.5vw, 6px);
    }
  }
}

@media (max-height: 600px) {
  .root-container {
    padding: clamp(4px, 0.6vw, 10px);
  }
  
  .grid-container.evaluation-version {
    gap: clamp(1px, 0.1vw, 2px);
  }
}

/* 超小屏幕适配 */
@media (max-width: 480px) {
  .grid-container.evaluation-version {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto auto auto;
    gap: clamp(1px, 0.1vw, 2px);
  }
  
  .evaluation-version .a-container {
    grid-column: 1;
    grid-row: 1;
  }
  
  .evaluation-version .b-container {
    grid-column: 1;
    grid-row: 2;
  }
  
  .evaluation-version .c-container {
    grid-column: 1;
    grid-row: 3;
  }
  
  .evaluation-version .d-container {
    grid-column: 1;
    grid-row: 4;
  }
  
  .evaluation-version .e-container {
    grid-column: 1;
    grid-row: 5;
  }
}
</style>
