<template>
  <div class="content">


    <div class="section-container">
      <!-- 子页面切换标签 -->
      <div class="tab-container">
        <button 
          class="tab-btn" 
          :class="{ 'active': currentTab === 'diagnostic' }"
          @click="switchTab('diagnostic')"
        >
          <span class="tab-icon">🔍</span>
          Diagnosis Conclusion
        </button>
        <button 
          class="tab-btn" 
          :class="{ 'active': currentTab === 'treatment' }"
          @click="switchTab('treatment')"
        >
          <span class="tab-icon">💊</span>
          Treatment Principles
        </button>
      </div>

      <!-- 答案内容区域 -->
      <div class="answer-section">
        <!-- 诊断结果页面 -->
        <div 
          v-if="currentTab === 'diagnostic'"
          class="comparison-content"
        >
          <!-- 左侧：作答者诊断答案 -->
          <div class="comparison-left">
            <h4 class="comparison-title">Answer from Analyst</h4>
            <div class="evaluator-content">
              <div v-if="evaluatorDiagnosis" v-html="formatAnswer(evaluatorDiagnosis)"></div>
              <div v-else-if="loading" class="loading">Loading...</div>
              <div v-else class="no-data">None</div>
            </div>
          </div>
          
          <!-- 右侧：参考诊断结论 -->
          <div class="comparison-right">
            <h4 class="comparison-title">Reference of Conclusion</h4>
            <div class="reference-content">
              <div v-if="diagnostic" v-html="formatAnswer(diagnostic)"></div>
              <div v-else-if="loading" class="loading">Loading...</div>
              <div v-else-if="error" class="error">{{ error }}</div>
              <div v-else class="no-answer">None</div>
            </div>
          </div>
        </div>

        <!-- 治疗方案页面 -->
        <div 
          v-if="currentTab === 'treatment'"
          class="comparison-content"
        >
          <!-- 左侧：作答者治疗答案 -->
          <div class="comparison-left">
            <h4 class="comparison-title">Answer from Analyst</h4>
            <div class="evaluator-content">
              <div v-if="evaluatorTreatment" v-html="formatAnswer(evaluatorTreatment)"></div>
              <div v-else-if="loading" class="loading">Loading...</div>
              <div v-else class="no-data">None</div>
            </div>
          </div>
          
          <!-- 右侧：参考治疗原则 -->
          <div class="comparison-right">
            <h4 class="comparison-title">Reference of Treatment Principles</h4>
            <div class="reference-content">
              <div v-if="treatment" v-html="formatAnswer(treatment)"></div>
              <div v-else-if="loading" class="loading">Loading...</div>
              <div v-else-if="error" class="error">{{ error }}</div>
              <div v-else class="no-answer">当前案例暂无治疗信息</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 导航按钮区域 -->
      <div class="navigation-buttons">
        <button 
          class="nav-btn prev-btn" 
          @click="handlePrevious"
          :disabled="isFirstAssignedCase"
        >
          Previous
        </button>
        <div class="navigation-counter">
          {{ currentAssignedIndex + 1 }}/{{ totalAssignedCases }}
        </div>
        <button 
          v-if="!isLastAssignedCase"
          class="nav-btn next-btn" 
          :class="{ 'disabled': !canProceedToNext }"
          @click="handleNext"
          :disabled="!canProceedToNext"
          :title="getNextButtonTitle()"
        >
          <span v-if="!allDimensionsScored" class="warning-icon">⚠</span>
          <span v-if="!allEvaluatorsClassified" class="warning-icon">📋</span>
          Next
        </button>
        <button 
          v-else
          class="nav-btn submit-btn" 
          :class="{ 'disabled': !canProceedToNext }"
          @click="handleSubmit"
          :disabled="!canProceedToNext"
          :title="getNextButtonTitle()"
        >
          <span v-if="!allDimensionsScored" class="warning-icon">⚠</span>
          <span v-if="!allEvaluatorsClassified" class="warning-icon">📋</span>
          Submit
        </button>
      </div>
      

    </div>
  </div>
</template>

<script>
export default {
  name: "SectionE",
  props: {
    username: {
      type: String,
      default: ''
    },
    availableEvaluatorsCount: {
      type: Number,
      default: 0
    },
    selectedEvaluator: {
      type: Object,
      default: null
    }
  },
  emits: ['case-changed', 'show-thank-you'],
  data() {
    return {
      debugInfo: null,
      diagnostic: '',
      treatment: '',
      originalCase: '',
      loading: false,
      userType: null,

      error: '',
      currentTab: 'diagnostic', // 默认显示诊断结果

      evaluatorDiagnosis: '',
      evaluatorTreatment: '',
      dimensionsScoredStatus: false
    }
  },
  computed: {
    isFirstAssignedCase() {
      return this.debugInfo && this.debugInfo.case_index <= 0;
    },
    
    isLastAssignedCase() {
      return this.debugInfo && this.debugInfo.case_index >= this.debugInfo.total_cases - 1;
    },
    
    completedCount() {
      return this.debugInfo ? this.debugInfo.total_cases : 0;
    },
    
    currentAssignedIndex() {
      return this.debugInfo ? this.debugInfo.case_index : 0;
    },
    
    totalAssignedCases() {
      return this.debugInfo ? this.debugInfo.total_cases : 0;
    },
    
    // 检查是否所有作答者都已被分类
    allEvaluatorsClassified() {
      return this.availableEvaluatorsCount === 0;
    },
    
    // 检查是否所有维度都已评分
    allDimensionsScored() {
      return this.dimensionsScoredStatus;
    },
    
    // 检查是否可以进入下一个案例
    canProceedToNext() {
      return this.allEvaluatorsClassified && this.allDimensionsScored;
    }
  },
  async mounted() {
    // 首先获取用户类型和分配案例信息
    await this.getUserTypeInfo();
    // 然后获取当前案例信息
    await this.getCurrentCaseInfo();
    // 获取答案信息
    await this.getAnswer();

    // 检查维度评分状态
    await this.checkDimensionsScoredStatus();
  },
  watch: {
    username: {
      handler() {
        if (this.username) {
          this.getAnswer();
        }
      },
      immediate: true
    },
    availableEvaluatorsCount: {
      handler() {
        // availableEvaluatorsCount changed
      },
      immediate: true
    },
    selectedEvaluator: {
      handler(newEvaluator) {
        if (newEvaluator) {
          this.loadEvaluatorData(newEvaluator);
        } else {
          this.evaluatorDiagnosis = '';
          this.evaluatorTreatment = '';
        }
      },
      immediate: true
    },
    // 监听评分状态变化
    dimensionsScoredStatus: {
      handler(newStatus) {
        console.log('维度评分状态变化:', newStatus);
      },
      immediate: true
    },
    // 监听案例变化，重新检查评分状态
    'debugInfo.case_filename': {
      handler(newCaseName) {
        if (newCaseName) {
          // console.log('案例改变，重新检查评分状态:', newCaseName);
          this.checkDimensionsScoredStatus();
        }
      },
      immediate: true
    }
  },
  methods: {
    // 切换子页面
    switchTab(tab) {
      this.currentTab = tab;
    },

    // 加载评估者诊断和治疗信息
    async loadEvaluatorData(evaluator) {
      if (!evaluator) {
        this.evaluatorDiagnosis = '';
        this.evaluatorTreatment = '';
        return;
      }

      try {
        // 获取当前案例信息，以确定正确的案例ID
        const caseResponse = await fetch(`/api/evaluation/current-case?username=${this.username}`);
        const caseData = await caseResponse.json();
        
        if (caseData.status !== 'success') {
          throw new Error('获取当前案例信息失败');
        }
        
        // 从case_filename中提取案例ID
        let actualCaseId = 1;
        if (caseData.case_filename && caseData.case_filename.startsWith('case')) {
          actualCaseId = parseInt(caseData.case_filename.replace('case', ''));
        }
        
        const response = await fetch(`/api/evaluation/case/${actualCaseId}/evaluator/${evaluator.evaluator.id}`);
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'success') {
            // 直接保存原始诊断和治疗信息
            this.evaluatorDiagnosis = data.diagnosis || '';
            this.evaluatorTreatment = data.treatment || '';
            
            console.log(`加载评估者 ${evaluator.evaluator.id} 的诊断和治疗信息:`, {
              diagnosis: data.diagnosis,
              treatment: data.treatment
            });
          }
        }
      } catch (error) {
        console.error(`加载评估者 ${evaluator.evaluator.id} 诊断和治疗信息失败:`, error);
        this.evaluatorDiagnosis = '';
        this.evaluatorTreatment = '';
      }
    },

    // 获取下一个按钮的提示信息
    getNextButtonTitle() {
      const conditions = [];
      
      if (!this.allEvaluatorsClassified) {
        conditions.push('将所有作答者分类到档位中');
      }
      
      if (!this.allDimensionsScored) {
        conditions.push('完成所有作答者的维度评分');
      }
      
      if (conditions.length > 0) {
        return `请先${conditions.join('，并')}，然后才能进入下一个案例`;
      }
      
      return '';
    },

    async getCurrentCaseInfo() {
      try {
        const response = await fetch(`/api/evaluation/current-case?username=${this.username}`);
        const data = await response.json();
        
        if (data.status === 'success') {
          this.debugInfo = {
            case_index: data.case_index,
            total_cases: data.total_cases,
            case_filename: data.case_filename
          };
          
          // 用户类型和分配案例信息已删除
        }
        return data;
      } catch (error) {
        console.error('获取当前案例信息失败:', error);
        return null;
      }
    },
    
    async getUserTypeInfo() {
      // 用户类型信息获取已删除
    },
    


    // 重构后的维度评分状态检查方法 - 使用SectionC.vue的逻辑
    async checkDimensionsScoredStatus() {
      if (!this.username || !this.debugInfo) {
        this.dimensionsScoredStatus = false;
        console.log('checkDimensionsScoredStatus: 缺少必要参数');
        return;
      }

      try {
        // 使用实际的案例文件名，而不是递增的数字ID
        const caseName = this.debugInfo.case_filename;
        console.log(`开始检查案例${caseName}的维度评分状态`);
        
        // 从案例文件名中提取数字ID用于API调用
        const caseIdMatch = caseName.match(/case(\d+)/);
        const caseId = caseIdMatch ? parseInt(caseIdMatch[1]) : 1;
        
        // 获取当前案例的所有评估者列表
        let expectedEvaluators = [];
        try {
          const evaluatorsResponse = await fetch(`/api/evaluation/case/${caseId}/evaluators`);
          if (evaluatorsResponse.ok) {
            const evaluatorsData = await evaluatorsResponse.json();
            if (evaluatorsData.status === 'success' && evaluatorsData.evaluators && evaluatorsData.evaluators.length > 0) {
              expectedEvaluators = evaluatorsData.evaluators.map(evaluator => evaluator.id);
              console.log(`案例${caseName}的评估者列表:`, expectedEvaluators);
            } else {
              console.log(`案例${caseName}没有评估者数据或评估者列表为空`);
            }
          } else {
            console.log(`案例${caseName}的评估者API返回${evaluatorsResponse.status}，可能该案例不存在`);
            // 如果API返回404，说明该案例不存在，我们使用localStorage中的数据
            const storageKey = `evaluation_scores_${this.username}`;
            const scores = JSON.parse(localStorage.getItem(storageKey) || '{}');
            const caseKey = caseName;
            const caseScores = scores[caseKey] || {};
            
            // 从localStorage中提取评估者ID（排除非评估者字段）
            expectedEvaluators = Object.keys(caseScores).filter(key => 
              key !== 'ranking' && key !== 'tiers' && key !== 'saved' && key !== 'saved_at'
            );
            console.log(`从localStorage获取案例${caseName}的评估者列表:`, expectedEvaluators);
          }
        } catch (apiError) {
          console.log(`获取案例${caseName}评估者列表API失败:`, apiError);
          // 使用localStorage中的数据作为备选
          const storageKey = `evaluation_scores_${this.username}`;
          const scores = JSON.parse(localStorage.getItem(storageKey) || '{}');
          const caseKey = caseName;
          const caseScores = scores[caseKey] || {};
          
          expectedEvaluators = Object.keys(caseScores).filter(key => 
            key !== 'ranking' && key !== 'tiers' && key !== 'saved' && key !== 'saved_at'
          );
          console.log(`从localStorage获取案例${caseName}的评估者列表:`, expectedEvaluators);
        }
        
        // 如果没有评估者，直接返回false
        if (expectedEvaluators.length === 0) {
          this.dimensionsScoredStatus = false;
          console.log(`案例${caseName}没有评估者，设置dimensionsScoredStatus为false`);
          return;
        }
        
        // 从localStorage获取评分数据（与SectionC.vue保持一致）
        const storageKey = `evaluation_scores_${this.username}`;
        const scores = JSON.parse(localStorage.getItem(storageKey) || '{}');
        
        const caseKey = caseName;
        const caseScores = scores[caseKey] || {};
        console.log(`案例${caseName}的评分数据:`, caseScores);
        
        // 获取维度数据
        const dimensionsResponse = await fetch('/api/evaluation/dimensions');
        const dimensionsData = await dimensionsResponse.json();
        
        // 检查每个评估者的所有维度是否都已评分
        for (const evaluatorKey of expectedEvaluators) {
          const evaluatorScores = caseScores[evaluatorKey] || {};
          const dimensions = evaluatorScores.dimensions || {};
          console.log(`评估者${evaluatorKey}的维度评分:`, dimensions);
          
          // 检查该评估者的所有维度
          for (const dimension of dimensionsData) {
            const dimensionKey = `${dimension.category}-${dimension.dimension}`;
            const score = dimensions[dimensionKey] || 0;
            console.log(`检查维度 ${dimensionKey}: 分数 = ${score}`);
            
            if (score === 0) {
              this.dimensionsScoredStatus = false;
              console.log(`维度 ${dimensionKey} 未评分（分数为0），设置dimensionsScoredStatus为false`);
              return;
            }
          }
        }
        
        this.dimensionsScoredStatus = true;
        console.log(`案例${caseName}的所有维度评分已完成，设置dimensionsScoredStatus为true`);
      } catch (error) {
        console.error('检查维度评分状态失败:', error);
        this.dimensionsScoredStatus = false;
      }
    },

    // 新增：处理来自SectionC的评分状态变化事件
    handleScoringStatusChanged(statusData) {
      console.log('SectionE收到评分状态变化:', statusData);
      // 立即重新检查评分状态
      this.checkDimensionsScoredStatus();
    },

    // 新增：处理评分更新事件
    handleScoreUpdated() {
      console.log('SectionE收到评分更新事件');
      // 立即重新检查评分状态
      this.checkDimensionsScoredStatus();
    },

    async getAnswer(forceRefresh = false) {
      if (!this.username) return;
      
      this.loading = true;
      this.error = '';
      
      try {
        const url = forceRefresh 
          ? `/api/evaluation/get-answer?username=${this.username}&force_refresh=true`
          : `/api/evaluation/get-answer?username=${this.username}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.status === 'success') {
          // 分别获取诊断和治疗方案
          this.diagnostic = data.diagnostic || '';
          this.treatment = data.treatment || '';
          this.originalCase = data.originalCase || '';
        } else {
          this.error = data.message || '获取答案失败';
          this.diagnostic = '';
          this.treatment = '';
          this.originalCase = '';
        }
      } catch (error) {
        console.error('获取答案失败:', error);
        this.error = '网络请求失败: ' + error.message;
        this.diagnostic = '';
        this.treatment = '';
        this.originalCase = '';
      } finally {
        this.loading = false;
      }
    },

    formatAnswer(answer) {
      if (!answer) return '';
      // 将换行符转换为HTML换行标签
      return answer.replace(/\n/g, '<br>');
    },

    formatOriginalCase(originalCase) {
      if (!originalCase) return '';
      
      try {
        const caseData = JSON.parse(originalCase);
        let formattedContent = '';
        
        // 角色设定
        if (caseData.prompt1) {
          formattedContent += caseData.prompt1 + '<br><br>';
        }
        
        // 患者自述
        if (caseData.prompt2) {
          formattedContent += caseData.prompt2 + '<br><br>';
        }
        
        // 检查（合并prompt3和prompt4）
        if (caseData.prompt3 || caseData.prompt4) {
          let examinationContent = '';
          
          if (caseData.prompt3 && Object.keys(caseData.prompt3).length > 0) {
            // 格式化prompt3对象
            for (const [key, value] of Object.entries(caseData.prompt3)) {
              examinationContent += `${key}: ${value}<br>`;
            }
          }
          
          if (caseData.prompt4 && Object.keys(caseData.prompt4).length > 0) {
            if (examinationContent) examinationContent += '<br>';
            // 格式化prompt4对象
            for (const [key, value] of Object.entries(caseData.prompt4)) {
              examinationContent += `${key}: ${value}<br>`;
            }
          }
          
          if (examinationContent) {
            formattedContent += examinationContent;
          }
        }
        
        return formattedContent;
      } catch (error) {
        console.error('格式化原始案例内容失败:', error);
        // 如果解析失败，直接返回原始内容
        return originalCase.replace(/\n/g, '<br>');
      }
    },

    async handlePrevious() {
      try {
        const response = await fetch('/api/evaluation/navigate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            direction: 'previous',
            username: this.username
          })
        });

        const data = await response.json();
        
        if (data.status === 'success') {
          // 更新调试信息
          this.debugInfo = {
            case_index: data.current_index,
            total_cases: data.total_cases,
            case_filename: data.case_name
          };
          // 重新获取答案，使用强制刷新
          await this.getAnswer(true);
          // 发射事件通知其他组件案例已改变，并传递导航方向
          this.$emit('case-changed', { ...data, navigationDirection: 'previous' });
        } else {
          // 导航失败时显示错误信息
          console.log('导航失败:', data.message);
          alert('导航失败: ' + data.message);
        }
      } catch (error) {
        console.error('导航请求失败:', error);
      }
    },

    async handleNext() {
      // 强制重新检查评分状态
      await this.checkDimensionsScoredStatus();
      
      // 如果作答者未分类完成或维度未评分完成，直接返回
      if (!this.canProceedToNext) {
        return;
      }

      try {
        // 导航到下一个case
        const response = await fetch('/api/evaluation/navigate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            direction: 'next',
            username: this.username
          })
        });

        const data = await response.json();
        
        if (data.status === 'success') {
          // 更新调试信息
          this.debugInfo = {
            case_index: data.current_index,
            total_cases: data.total_cases,
            case_filename: data.case_name
          };
          
          // 初始化新case的字段
          await this.initializeNewCase(data.case_name);
          
          // 重新获取答案，使用强制刷新
          await this.getAnswer(true);
          // 发射事件通知其他组件案例已改变，并传递导航方向
          this.$emit('case-changed', { ...data, navigationDirection: 'next' });
        } else {
          // 导航失败时显示错误信息
          console.log('导航失败:', data.message);
          alert('导航失败: ' + data.message);
        }
      } catch (error) {
        console.error('导航请求失败:', error);
      }
    },

    // 初始化新case的字段
    async initializeNewCase(caseName) {
      if (!this.username || !caseName) return;
      
      try {
        // 构建初始化数据
        const initData = {
          username: this.username,
          case_id: caseName
        };
        
        // 发送初始化请求
        const initResponse = await fetch('/api/evaluation/initialize-case', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(initData)
        });
        
        if (initResponse.ok) {
          console.log(`新case ${caseName} 字段初始化成功`);
        } else {
          console.error('初始化新case字段失败:', initResponse.statusText);
        }
      } catch (error) {
        console.error('初始化新case字段出错:', error);
      }
    },







    async handleSubmit() {
      try {
        // 直接跳转到感谢页面，不保存任何数据
        this.$emit('show-thank-you');
      } catch (error) {
        console.error('跳转失败:', error);
        alert('跳转失败: ' + error.message);
      }
    },
    



  }
};
</script>

<style scoped>
.content {
  padding: 12px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.section-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.tab-container {
  display: flex;
  gap: 0;
  margin-bottom: 0;
  border-bottom: 2px solid #e0e0e0;
  background-color: #e3f2fd;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
}

.tab-btn {
  flex: 1;
  padding: clamp(10px, 0.96vw, 10px) clamp(16px, 1.6vw, 14px); /* 缩小20%: 12px -> 10px, 1.2vw -> 0.96vw, 15px -> 12px; 20px -> 16px, 2vw -> 1.6vw, 25px -> 20px */
  border: none;
  font-size: clamp(12px, 1.28vw, 14px); /* 缩小20%: 16px -> 13px, 1.6vw -> 1.28vw, 20px -> 16px */
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #bbdefb;
  color: #1976d2;
  border-right: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.tab-btn:last-child {
  border-right: none;
}

.tab-btn.active {
  background-color: #fff;
  color: #1565c0;
  font-weight: 600;
  border-bottom: 3px solid #1565c0;
  box-shadow: 0 2px 4px rgba(21, 101, 192, 0.2);
}

.tab-btn:hover:not(.active) {
  background-color: #90caf9;
  color: #0d47a1;
  transform: translateY(-1px);
}

.tab-icon {
  font-size: clamp(14px, 1.44vw, 16px);
  transition: transform 0.2s ease;
}

.tab-btn:hover .tab-icon {
  transform: scale(1.1);
}

.answer-section {
  border: 1px solid #e0e0e0;
  border-radius: 0 0 8px 8px;
  padding: 0;
  background-color: #fafafa;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.answer-content {
  background-color: white;
  padding: clamp(10px, 0.96vw, 12px); /* 缩小20%: 12px -> 10px, 1.2vw -> 0.96vw, 15px -> 12px */
  border-radius: 6px;
  border: 1px solid #ddd;
  color: #333;
  line-height: 1.6;
  white-space: pre-line;
  font-size: clamp(13px, 1.28vw, 12px); /* 缩小20%: 16px -> 13px, 1.6vw -> 1.28vw, 20px -> 16px */
  cursor: text;
  transition: all 0.2s ease;
}

.answer-content:hover {
  background-color: #f8f9fa;
  border-color: #409eff;
}

.comparison-content {
  display: flex;
  gap: 16px;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.comparison-left,
.comparison-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
  height: 100%;
}

.comparison-title {
  font-size: clamp(14px, 1.44vw, 12px);
  font-weight: 600;
  color: #333;
  margin: 0 0 clamp(2px, 0.2vw, 4px) 0;
  padding: clamp(6px, 0.6vw, 8px) clamp(12px, 1.2vw, 16px);
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  color: #1976d2;
  border-radius: 6px 6px 0 0;
  position: relative;
  box-shadow: 0 2px 4px rgba(25, 118, 210, 0.1);
}

.comparison-title::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 12px 12px 0;
  border-color: transparent #bbdefb transparent transparent;
}

.comparison-title::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 8px 8px 0;
  border-color: transparent #e3f2fd transparent transparent;
}

.evaluator-content {
  flex: 1;
  background-color: white;
  padding: clamp(8px, 0.8vw, 10px);
  border-radius: 0 0 6px 6px;
  border: 1px solid #ddd;
  border-top: none;
  color: #333;
  line-height: 1.4;
  white-space: pre-line;
  font-size: clamp(13px, 1.28vw, 12px);
  cursor: text;
  transition: all 0.2s ease;
  overflow-y: auto;
  overflow-x: hidden;
}

.evaluator-content:hover {
  background-color: #f8f9fa;
  border-color: #409eff;
}



.reference-content {
  flex: 1;
  background-color: white;
  padding: clamp(8px, 0.8vw, 10px);
  border-radius: 0 0 6px 6px;
  border: 1px solid #ddd;
  border-top: none;
  color: #333;
  line-height: 1.4;
  white-space: pre-line;
  font-size: clamp(13px, 1.28vw, 12px);
  cursor: text;
  transition: all 0.2s ease;
  overflow-y: auto;
  overflow-x: hidden;
}

.reference-content:hover {
  background-color: #f8f9fa;
  border-color: #409eff;
}

.label {
  font-weight: 600;
  color: #495057;
  margin-right: 6px;
  display: inline-block;
  min-width: fit-content;
}

.content {
  color: #333;
  line-height: 1.1;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: normal;
  margin: 0;
  padding: 0;
}

.no-data {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 12px;
}

.loading {
  color: #666;
  font-style: italic;
  text-align: center;
  padding: clamp(16px, 1.6vw, 16px); /* 缩小20%: 20px -> 16px, 2vw -> 1.6vw, 25px -> 20px */
}

.error {
  color: #dc3545;
  font-weight: 500;
  text-align: center;
  padding: clamp(16px, 1.6vw, 20px); /* 缩小20%: 20px -> 16px, 2vw -> 1.6vw, 25px -> 20px */
}

.no-answer {
  color: #6c757d;
  font-style: italic;
  text-align: center;
  padding: clamp(16px, 1.6vw, 20px); /* 缩小20%: 20px -> 16px, 2vw -> 1.6vw, 25px -> 20px */
}

.navigation-buttons {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: clamp(16px, 1.6vw, 10px) 0; /* 缩小20%: 20px -> 16px, 2vw -> 1.6vw, 25px -> 20px */
  gap: clamp(16px, 1.6vw, 10px); /* 缩小20%: 20px -> 16px, 2vw -> 1.6vw, 25px -> 20px */
}

.navigation-counter {
  font-size: clamp(13px, 1.28vw, 10px); /* 缩小20%: 16px -> 13px, 1.6vw -> 1.28vw, 20px -> 16px */
  color: #6c757d;
  font-weight: 500;
  padding: clamp(6px, 0.64vw, 8px) clamp(10px, 0.96vw, 12px); /* 缩小20%: 8px -> 6px, 0.8vw -> 0.64vw, 10px -> 8px; 12px -> 10px, 1.2vw -> 0.96vw, 15px -> 12px */
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
  min-width: clamp(48px, 4.8vw, 50px); /* 缩小20%: 60px -> 48px, 6vw -> 4.8vw, 75px -> 60px */
  text-align: center;
}

.nav-btn {
  padding: clamp(10px, 0.96vw, 8px) clamp(10px, 1.92vw, 8px); /* 缩小20%: 12px -> 10px, 1.2vw -> 0.96vw, 15px -> 12px; 24px -> 19px, 2.4vw -> 1.92vw, 30px -> 24px */
  border: none;
  border-radius: 6px;
  font-size: clamp(13px, 1.28vw, 10px); /* 缩小20%: 16px -> 13px, 1.6vw -> 1.28vw, 20px -> 16px */
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.prev-btn {
  background-color: #6c757d;
  color: white;
}

.prev-btn:hover:not(:disabled) {
  background-color: #5a6268;
}

.prev-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.next-btn {
  background-color: #007bff;
  color: white;
}

.next-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.next-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.next-btn.disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
  position: relative;
}

/* 自定义tooltip样式 */
.next-btn.disabled:hover::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background-color: #333;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  margin-bottom: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.next-btn.disabled:hover::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: #333;
  margin-bottom: 3px;
  z-index: 1000;
}

.warning-icon {
  color: #ff6b6b;
  font-size: 14px;
  margin-right: 4px;
  animation: pulse 2s infinite;
}

/* 分类警告图标样式 */
.warning-icon:last-child {
  color: #f71505;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

.submit-btn {
  background-color: #28a745;
  color: white;
}

.submit-btn:hover {
  background-color: #218838;
}

.submit-btn.disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.submit-btn.disabled:hover {
  background-color: #ccc;
}






</style>
