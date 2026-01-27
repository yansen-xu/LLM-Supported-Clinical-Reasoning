<template>
  <!-- 成功提示框 -->
  <div v-if="showSuccessMessage" class="success-message-overlay">
    <div class="success-message">
      <div class="success-icon">✓</div>
      <div class="success-text">Save successfully</div>
    </div>
  </div>
  
  <!-- 原有内容 -->
  <div class="content">
    <!-- 重新设计的诊断结论部分 -->
    <div class="diagnosis-container">
      <h3 class="section-title">Diagnosis</h3>
      <p class="guidance-text">
        Based on the patient's symptoms, signs and examination results, combined with your clinical experience, please provide a clear diagnosis conclusion. The recommendation should include: main diagnosis, secondary diagnosis, complications, etc. Please use standard medical terms to ensure the accuracy and completeness of the diagnosis.
      </p>
      
      <!-- 诊断结论列表 -->
      <div class="diagnosis-list-container">
        <div class="diagnosis-list">
          <div 
            v-for="(diagnosis, index) in diagnosisList" 
            :key="index" 
            class="diagnosis-item"
          >
            <div class="diagnosis-number">{{ index + 1 }}.</div>
            <div class="diagnosis-inputs">
              <div class="input-group">
                <label class="input-label">Conclusion</label>
                <textarea
                  v-model="diagnosisList[index].conclusion"
                  class="diagnosis-conclusion"
                  :placeholder="`Please input your conclusion...`"
                  rows="2"
                ></textarea>
              </div>
              <div class="input-group">
                <label class="input-label">Reasoning Process</label>
                <textarea
                  v-model="diagnosisList[index].reasoning"
                  class="diagnosis-reasoning"
                  :placeholder="`Please input your reasoning process...`"
                  rows="2"
                ></textarea>
              </div>
            </div>
            <button 
              @click="removeDiagnosis(index)" 
              class="remove-btn"
              title="Delete"
            >
              ×
            </button>
          </div>
        </div>
      </div>
      
      <!-- 添加新诊断按钮 -->
      <button @click="addDiagnosis" class="add-diagnosis-btn">
        <span class="add-icon">+</span>
        Add diagnosis conclusion.
      </button>
    </div>
    
    <div class="treatment-container">
      <h3 class="section-title">Treatment Principles</h3>
      <p class="guidance-text">
        Please formulate a comprehensive and standardized treatment plan, including: drug therapy (drug name, dosage, usage, treatment course), non-drug therapy, nursing measures, follow-up plan, etc. Please follow the principles of evidence-based medicine and take into account individual differences of patients to ensure the safety and effectiveness of the treatment.
        Note: The priority of more important treatment principles should be higher.
      </p>
      
      <!-- 治疗方案列表 -->
      <div class="treatment-list-container">
        <div class="treatment-list">
          <div 
            v-for="(treatment, index) in treatmentList" 
            :key="index" 
            class="treatment-item"
          >
            <div class="treatment-number">{{ index + 1 }}.</div>
            <div class="treatment-inputs">
              <div class="input-group">
                <textarea
                  v-model="treatmentList[index].plan"
                  class="treatment-plan"
                  :placeholder="`Please input your treatment plan`"
                  rows="2"
                ></textarea>
              </div>
            </div>
            <button 
              @click="removeTreatment(index)" 
              class="remove-btn"
              title="删除此条治疗方案"
            >
              ×
            </button>
          </div>
        </div>
      </div>
      
      <!-- 添加新治疗方案按钮 -->
      <button @click="addTreatment" class="add-treatment-btn">
        <span class="add-icon">+</span>
        Add your treatment plan
      </button>
    </div>
    <div class="bottom-btn-wrapper">
      <!-- 最后一个案例时只显示提交按钮 -->
      <template v-if="isLastCase">
        <button v-if="showPreviousBtn" class="previous-btn" @click="handlePrevious">Previous</button>
        <button class="submit-btn" @click="handleSubmit">Save</button>
      </template>
      <!-- 非最后一个案例时显示前一个和下一个按钮 -->
      <template v-else>
        <button v-if="showPreviousBtn" class="previous-btn" @click="handlePrevious">Previous</button>
        <button class="next-btn" @click="handleNext">Next</button>
      </template>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { ref, onMounted, onBeforeUnmount, computed } from "vue";

export default {
  name: "SectionD",
  props: {
    messages: { type: Array, default: () => [] }
  },
  emits: ["clearAll"],
  setup(props, { emit }) {

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

    // 将单个diagnosis改为diagnosisList数组，每个元素包含结论和推理过程
    const diagnosisList = ref([{ conclusion: "", reasoning: "" }]);
    // 将单个treatment改为treatmentList数组，每个元素包含治疗方案
    const treatmentList = ref([{ plan: "" }]);
    
    // 病例信息相关状态（从SectionC获取）
    const currentCaseIndex = ref(0);
    const totalCases = ref(0); // 添加总案例数量状态
    const showPreviousBtn = ref(false); // 是否显示previous按钮
    const showSuccessMessage = ref(false); // 是否显示成功提示
    let pollTimer = null;
    
    // 计算是否为最后一个案例（动态计算）
    const isLastCase = computed(() => currentCaseIndex.value === totalCases.value - 1);
    
    // 添加诊断结论
    const addDiagnosis = () => {
      diagnosisList.value.push({ conclusion: "", reasoning: "" });
    };
    
    // 删除诊断结论
    const removeDiagnosis = (index) => {
      if (diagnosisList.value.length > 1) {
        diagnosisList.value.splice(index, 1);
      }
    };
    
    // 添加治疗方案
    const addTreatment = () => {
      treatmentList.value.push({ plan: "" });
    };
    
    // 删除治疗方案
    const removeTreatment = (index) => {
      if (treatmentList.value.length > 1) {
        treatmentList.value.splice(index, 1);
      }
    };
    
    // 获取格式化的诊断结论文本
    const getFormattedDiagnosis = () => {
      return diagnosisList.value
        .filter(diagnosis => diagnosis.conclusion.trim() !== "" || diagnosis.reasoning.trim() !== "")
        .map((diagnosis, index) => {
          let result = `${index + 1}. 结论：${diagnosis.conclusion.trim()}`;
          if (diagnosis.reasoning.trim() !== "") {
            result += `\n   推理过程：${diagnosis.reasoning.trim()}`;
          }
          return result;
        })
        .join("\n\n");
    };
    
    // 获取格式化的治疗原则文本
    const getFormattedTreatment = () => {
      return treatmentList.value
        .filter(treatment => treatment.plan.trim() !== "")
        .map((treatment, index) => {
          return `${index + 1}. ${treatment.plan.trim()}`;
        })
        .join("\n\n");
    };
    
    // 从后端获取当前病例信息（获取索引和总案例数量）
    const fetchCurrentCaseIndex = async () => {
      try {
        const userId = localStorage.getItem('analysis_user_id') || 'default_user';
        const username = localStorage.getItem('analysis_username') || '';
        const response = await axios.get(`${backendBaseURL.value}/current-case?user_id=${userId}&username=${username}`);
        if (response.data.status === 'success') {
          // 更新病例索引
          const newCaseIndex = response.data.case_index;
          if (newCaseIndex !== currentCaseIndex.value) {
            console.log(`用户 ${username} 病例索引从 ${currentCaseIndex.value} 更新为 ${newCaseIndex}`);
            // 当案例改变时，检查是否需要加载已保存的对话
            await checkAndLoadSavedConversation(username, newCaseIndex);
          }
          currentCaseIndex.value = newCaseIndex;
          
          // 更新总案例数量（从调试信息中获取）
          if (response.data.debug_info && response.data.debug_info.total_cases) {
            totalCases.value = response.data.debug_info.total_cases;
            console.log(`用户 ${username} 总案例数量: ${totalCases.value}`);
          }
          
          // 更新是否显示previous按钮
          checkIfShowPreviousBtn(username, newCaseIndex);
        }
      } catch (error) {
        console.error("获取当前病例索引失败:", error);
      }
    };
    
    // 检查是否显示previous按钮（当前案例不是第一个就显示）
    const checkIfShowPreviousBtn = async (username, caseIndex) => {
      try {
        // 只有当不是第一个案例时，才显示previous按钮
        showPreviousBtn.value = caseIndex > 0;
        console.log(`用户 ${username} 当前案例索引: ${caseIndex}, 显示previous按钮: ${showPreviousBtn.value}`);
      } catch (error) {
        console.error("检查previous按钮状态失败:", error);
        showPreviousBtn.value = false;
      }
    };
    
    // 检查并加载已保存的对话
    const checkAndLoadSavedConversation = async (username, caseIndex) => {
      try {
        const response = await axios.get(`${backendBaseURL.value}/api/get-saved-conversation`, {
          params: {
            username: username,
            case_index: caseIndex
          }
        });
        
        if (response.data.status === 'success') {
          // 加载已保存的诊断和治疗
          if (response.data.Diagnosis) {
            // 解析诊断文本，重建diagnosisList
            const diagnosisText = response.data.Diagnosis;
            const diagnosisLines = diagnosisText.split('\n\n').filter(line => line.trim());
            diagnosisList.value = diagnosisLines.map(line => {
              // 简单解析格式："1. 结论：xxx\n   推理过程：yyy"
              const parts = line.split('\n');
              const conclusion = parts[0]?.replace(/^\d+\.\s*结论：/, '').trim() || '';
              const reasoning = parts[1]?.replace(/^\s*推理过程：/, '').trim() || '';
              return { conclusion, reasoning };
            });
            if (diagnosisList.value.length === 0) {
              diagnosisList.value = [{ conclusion: "", reasoning: "" }];
            }
          }
          
          if (response.data.Treatment) {
            // 解析治疗文本，重建treatmentList
            const treatmentText = response.data.Treatment;
            const treatmentLines = treatmentText.split('\n\n').filter(line => line.trim());
            treatmentList.value = treatmentLines.map(line => {
              const plan = line.replace(/^\d+\.\s*/, '').trim();
              return { plan };
            });
            if (treatmentList.value.length === 0) {
              treatmentList.value = [{ plan: "" }];
            }
          }
          
          console.log("已加载之前保存的对话内容");
        }
      } catch (error) {
        // 没有已保存的对话，这是正常的
        console.log("该案例还没有保存过对话内容");
      }
    };
    
    // 启动轮询
    const startPolling = () => {
      // 立即获取一次
      fetchCurrentCaseIndex();
      
      // 然后每1秒轮询一次（减少频率，避免干扰）
      pollTimer = setInterval(fetchCurrentCaseIndex, 1000);
    };
    
    // 停止轮询
    const stopPolling = () => {
      if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
      }
    };
    
    // 组件挂载时启动轮询
    onMounted(startPolling);
    
    // 组件卸载前停止轮询
    onBeforeUnmount(stopPolling);

    const handleNext = async () => {
      
      // 从localStorage获取用户名和用户ID
      const username = localStorage.getItem('analysis_username') || '';
      const userId = localStorage.getItem('analysis_user_id') || 'default_user';
      
      // 在保存前重新收集最新的对话数据
      let conversationData = [];
      
      // 直接从SectionC组件获取最新消息，避免使用缓存的数据
      const messageEvent = new CustomEvent('request-latest-messages', {
        detail: { callback: (messages) => {
          if (messages && messages.length > 0) {
            conversationData = messages;
            console.log("从SectionC获取到的消息:", messages);
          }
        }}
      });
      window.dispatchEvent(messageEvent);
      
      // 等待一小段时间确保消息获取完成
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // 如果还是没有数据，尝试其他方式
      if (conversationData.length === 0) {
        if (window.cData && window.cData.messages && window.cData.messages.length > 0) {
          conversationData = window.cData.messages;
        } else if (props.messages && props.messages.length > 0) {
          conversationData = props.messages;
        }
      }
      
      // 验证对话内容是否与当前案例匹配
      console.log("当前案例索引:", currentCaseIndex.value);
      console.log("对话内容:", conversationData);
      
      // 检查对话内容是否包含当前案例的主诉
      if (conversationData && conversationData.length > 0) {
        const firstMessage = conversationData[0]?.content || '';
        console.log("第一条消息:", firstMessage);
        
        // 获取当前案例的主诉信息
        try {
          const caseResponse = await axios.get(`${backendBaseURL.value}/api/get-main-suit?user_id=${userId}&username=${username}`);
          if (caseResponse.data.status === 'success') {
            const expectedMainSuit = caseResponse.data.main_suit;
            console.log("期望的主诉:", expectedMainSuit);
            
            if (!firstMessage.includes(expectedMainSuit)) {
              console.warn("警告：对话内容与当前案例不匹配！");
              console.warn("期望的主诉:", expectedMainSuit);
              console.warn("实际对话:", firstMessage);
              
              // 如果对话内容不匹配，尝试重新获取正确的对话内容
              // 这里可以添加逻辑来获取正确的对话内容
            }
          }
        } catch (error) {
          console.error("获取主诉信息失败:", error);
        }
      }
      
      // 组装导出数据，使用格式化的诊断结论
      const exportData = {
        username: username,
        user_id: userId,
        conversation: conversationData,
        Diagnosis: getFormattedDiagnosis(),
        Treatment: getFormattedTreatment(),
        case_index: currentCaseIndex.value  // 传递当前案例索引，确保保存到正确的文件
      };
      
      // 强制重新收集数据
      if (window.collectData) {
        window.collectData();
        // 重新获取对话数据
        if (window.cData && window.cData.messages && window.cData.messages.length > 0) {
          conversationData = window.cData.messages;
          exportData.conversation = conversationData;
        }
      }
      
      try {
        console.log("正在保存数据...", exportData);
        console.log("当前案例索引:", currentCaseIndex.value);
        
        // 先保存当前案例的对话内容
        const response = await axios.post(`${backendBaseURL.value}/api/save-conversation`, exportData);
        console.log("保存响应:", response.data);
        
        // 显示保存成功提示
        showSuccessMessage.value = true;
        // 2秒后自动隐藏成功提示
        setTimeout(() => {
          showSuccessMessage.value = false;
        }, 2000);
        
        // 等待保存完成后再跳转
        await new Promise(resolve => setTimeout(resolve, 200)); // 等待200ms确保保存完成
        
        // 然后调用next-step进行跳转
        const nextResponse = await axios.post(`${backendBaseURL.value}/api/next-step`, {
            action: true,
            username: username,
            user_id: userId
          });
        console.log("下一步响应:", nextResponse.data);
        
        // 清空本地内容
        diagnosisList.value = [{ conclusion: "", reasoning: "" }];
        treatmentList.value = [{ plan: "" }];
        emit("clearAll"); // 清空前端内容
        
        // 通知SectionC清空对话内容并重新加载病例信息
        // 通过全局事件通知SectionC执行next方法
        window.dispatchEvent(new CustomEvent('clear-conversation'));
        
        // 重新启动轮询以确保获取到最新的病例信息
        stopPolling();
        await new Promise(resolve => setTimeout(resolve, 500)); // 等待500ms确保后端状态更新
        
        // 立即获取一次最新数据
        await fetchCurrentCaseIndex();
        
        // 重新启动轮询
        startPolling();
        
        console.log("继续下一个案例，当前病例索引:", currentCaseIndex.value);
      } catch (e) {
        console.error("保存失败:", e);
        console.error("错误详情:", e.response?.data || e.message);
        alert(`保存失败，请重试。错误信息: ${e.response?.data?.message || e.message}`);
      }
    };

    const handlePrevious = async () => {
      // 从localStorage获取用户名和用户ID
      const username = localStorage.getItem('analysis_username') || '';
      const userId = localStorage.getItem('analysis_user_id') || 'default_user';
      
      try {
        console.log("切换到上一个案例...");
        
        // 调用后端previous-step接口
        const response = await axios.post(`${backendBaseURL.value}/api/previous-step`, {
          username: username,
          user_id: userId
        });
        console.log("上一步响应:", response.data);
        
        // 清空本地内容（不保存当前内容，直接返回）
        diagnosisList.value = [{ conclusion: "", reasoning: "" }];
        treatmentList.value = [{ plan: "" }];
        emit("clearAll"); // 清空前端内容
        
        // 通知SectionC清空对话内容并重新加载病例信息
        window.dispatchEvent(new CustomEvent('clear-conversation'));
        
        // 重新启动轮询以确保获取到最新的病例信息
        stopPolling();
        await new Promise(resolve => setTimeout(resolve, 500)); // 等待500ms确保后端状态更新
        
        // 立即获取一次最新数据
        await fetchCurrentCaseIndex();
        
        // 检查并加载已保存的对话（传入用户名和当前案例索引）
        await checkAndLoadSavedConversation(username, currentCaseIndex.value);
        
        // 通知SectionC加载已保存的对话
        window.dispatchEvent(new CustomEvent('load-saved-conversation', {
          detail: {
            username: username,
            caseIndex: currentCaseIndex.value
          }
        }));
        
        // 重新启动轮询
        startPolling();
        
        console.log("返回上一个案例，当前病例索引:", currentCaseIndex.value);
      } catch (e) {
        console.error("返回上一个案例失败:", e);
        console.error("错误详情:", e.response?.data || e.message);
        alert(`返回失败，请重试。错误信息: ${e.response?.data?.message || e.message}`);
      }
    };

    const handleSubmit = async () => {
      
      // 从localStorage获取用户名和用户ID
      const username = localStorage.getItem('analysis_username') || '';
      const userId = localStorage.getItem('analysis_user_id') || 'default_user';
      
      // 在保存前重新收集最新的对话数据
      let conversationData = [];
      
      // 直接从SectionC组件获取最新消息，避免使用缓存的数据
      const messageEvent = new CustomEvent('request-latest-messages', {
        detail: { callback: (messages) => {
          if (messages && messages.length > 0) {
            conversationData = messages;
            console.log("从SectionC获取到的消息:", messages);
          }
        }}
      });
      window.dispatchEvent(messageEvent);
      
      // 等待一小段时间确保消息获取完成
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // 如果还是没有数据，尝试其他方式
      if (conversationData.length === 0) {
        if (window.cData && window.cData.messages && window.cData.messages.length > 0) {
          conversationData = window.cData.messages;
        } else if (props.messages && props.messages.length > 0) {
          conversationData = props.messages;
        }
      }
      
      // 组装导出数据，使用格式化的诊断结论
      const exportData = {
        username: username,
        user_id: userId,
        conversation: conversationData,
        Diagnosis: getFormattedDiagnosis(),
        Treatment: getFormattedTreatment(),
        case_index: currentCaseIndex.value
      };
      
      // 强制重新收集数据
      if (window.collectData) {
        window.collectData();
        // 重新获取对话数据
        if (window.cData && window.cData.messages && window.cData.messages.length > 0) {
          conversationData = window.cData.messages;
          exportData.conversation = conversationData;
        }
      }
      
      try {
        console.log("正在保存数据...", exportData);
        
        // 保存数据
        await axios.post(`${backendBaseURL.value}/api/save-conversation`, exportData);
        
        // 显示保存成功提示
        showSuccessMessage.value = true;
        // 2秒后自动隐藏成功提示
        setTimeout(() => {
          showSuccessMessage.value = false;
        }, 2000);
        
      } catch (e) {
        console.error("保存失败:", e);
        console.error("错误详情:", e.response?.data || e.message);
        alert(`保存失败，请重试。错误信息: ${e.response?.data?.message || e.message}`);
      }
    };
    return { 
      diagnosisList,
      treatmentList, 
      handleNext,
      handlePrevious,
      handleSubmit,
      addDiagnosis,
      removeDiagnosis,
      addTreatment,
      removeTreatment,
      currentCaseIndex,
      isLastCase,
      showPreviousBtn,
      showSuccessMessage
    };
  }
};
</script>

<style scoped>
/* 成功提示框样式 */
.success-message-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
  background: rgba(0, 0, 0, 0.3);
}

.success-message {
  background: #4CAF50;
  color: white;
  padding: 30px 50px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 18px;
  animation: slideIn 0.3s ease-out;
}

.success-icon {
  font-size: 32px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}

.success-text {
  font-weight: 500;
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.content {
  padding: clamp(8px, 1vh, 16px);
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: clamp(12px, 1.5vh, 20px);
  overflow: auto;
  width: 100%;
  box-sizing: border-box;
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.content::-webkit-scrollbar {
  width: 6px;
}

.content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.section-title {
  font-size: clamp(14px, 1.5vw, 18px);
  font-weight: 600;
  margin-bottom: clamp(6px, 0.8vh, 12px);
  color: #333;
}

.guidance-text {
  font-size: clamp(12px, 1.3vw, 16px);
  color: #666;
  line-height: 1.6;
  margin-bottom: clamp(8px, 1vh, 16px);
  padding: clamp(8px, 1vh, 16px);
  background-color: #f8f9fa;
  border-left: clamp(2px, 0.3vw, 6px) solid #409eff;
  border-radius: clamp(3px, 0.4vw, 6px);
  font-style: italic;
}

.diagnosis-container,
.treatment-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  box-sizing: border-box;
  min-height: 0;
}

/* 诊断结论列表容器样式 */
.diagnosis-list-container {
  max-height: clamp(250px, 35vh, 400px);
  overflow-y: auto;
  overflow-x: hidden;
  border: clamp(1px, 0.1vh, 2px) solid #e9ecef;
  border-radius: clamp(6px, 0.8vw, 12px);
  padding: clamp(8px, 1vh, 16px);
  background-color: #f8f9fa;
  margin-bottom: clamp(12px, 1.5vh, 20px);
  width: 100%;
  box-sizing: border-box;
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.diagnosis-list-container::-webkit-scrollbar {
  width: 6px;
}

.diagnosis-list-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.diagnosis-list-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.diagnosis-list-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 治疗方案列表容器样式 */
.treatment-list-container {
  max-height: clamp(200px, 25vh, 300px);
  overflow-y: auto;
  overflow-x: hidden;
  border: clamp(1px, 0.1vh, 2px) solid #e9ecef;
  border-radius: clamp(6px, 0.8vw, 12px);
  padding: clamp(8px, 1vh, 16px);
  background-color: #f8f9fa;
  margin-bottom: clamp(12px, 1.5vh, 20px);
  width: 100%;
  box-sizing: border-box;
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.treatment-list-container::-webkit-scrollbar {
  width: 6px;
}

.treatment-list-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.treatment-list-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.treatment-list-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 诊断结论列表样式 */
.diagnosis-list {
  display: flex;
  flex-direction: column;
  gap: clamp(8px, 1vh, 16px);
  width: 100%;
  box-sizing: border-box;
}

/* 治疗方案列表样式 */
.treatment-list {
  display: flex;
  flex-direction: column;
  gap: clamp(8px, 1vh, 16px);
  width: 100%;
  box-sizing: border-box;
}

.diagnosis-item {
  display: flex;
  align-items: flex-start;
  gap: clamp(6px, 0.8vw, 12px);
  background-color: white;
  padding: clamp(8px, 1vh, 16px);
  border-radius: clamp(6px, 0.8vw, 12px);
  border: clamp(1px, 0.1vh, 2px) solid #e9ecef;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  width: 100%;
  box-sizing: border-box;
}

.treatment-item {
  display: flex;
  align-items: flex-start;
  gap: clamp(6px, 0.8vw, 12px);
  background-color: white;
  padding: clamp(8px, 1vh, 16px);
  border-radius: clamp(6px, 0.8vw, 12px);
  border: clamp(1px, 0.1vh, 2px) solid #e9ecef;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  width: 100%;
  box-sizing: border-box;
}

.diagnosis-inputs {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: clamp(8px, 1vw, 16px);
  align-items: flex-start;
  width: 100%;
  min-width: 0;
  overflow: hidden;
  box-sizing: border-box;
}

.treatment-inputs {
  flex: 1;
  display: flex;
  align-items: flex-start;
  width: 100%;
  min-width: 0;
  overflow: hidden;
  box-sizing: border-box;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: clamp(3px, 0.4vh, 6px);
  min-width: 0;
  overflow: hidden;
  box-sizing: border-box;
  flex: 1;
}

.input-label {
  font-size: clamp(10px, 1.1vw, 14px);
  font-weight: 600;
  color: #409eff;
  margin-bottom: clamp(1px, 0.2vh, 3px);
}

.diagnosis-number {
  font-weight: 600;
  color: #409eff;
  margin-top: clamp(1px, 0.2vh, 3px);
  flex-shrink: 0;
  min-width: clamp(16px, 2vw, 24px);
  font-size: clamp(12px, 1.3vw, 16px);
}

.treatment-number {
  font-weight: 600;
  color: #409eff;
  margin-top: clamp(1px, 0.2vh, 3px);
  flex-shrink: 0;
  min-width: clamp(16px, 2vw, 24px);
  font-size: clamp(12px, 1.3vw, 16px);
}

.diagnosis-conclusion {
  padding: clamp(6px, 0.8vh, 12px);
  border: clamp(1px, 0.1vh, 2px) solid #dcdfe6;
  border-radius: clamp(4px, 0.5vw, 8px);
  font-size: clamp(12px, 1.3vw, 16px);
  line-height: 1.4;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
  background-color: white;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  min-height: clamp(60px, 8vh, 80px);
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.diagnosis-conclusion::-webkit-scrollbar {
  width: 6px;
}

.diagnosis-conclusion::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.diagnosis-conclusion::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.diagnosis-conclusion::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.diagnosis-conclusion:focus {
  border-color: #409eff;
}

.diagnosis-conclusion::placeholder {
  color: #c0c4cc;
}

.diagnosis-reasoning {
  padding: clamp(6px, 0.8vh, 12px);
  border: clamp(1px, 0.1vh, 2px) solid #dcdfe6;
  border-radius: clamp(4px, 0.5vw, 8px);
  font-size: clamp(12px, 1.3vw, 16px);
  line-height: 1.4;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
  background-color: white;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  min-height: clamp(60px, 8vh, 80px);
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.diagnosis-reasoning::-webkit-scrollbar {
  width: 6px;
}

.diagnosis-reasoning::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.diagnosis-reasoning::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.diagnosis-reasoning::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.diagnosis-reasoning:focus {
  border-color: #409eff;
}

.diagnosis-reasoning::placeholder {
  color: #c0c4cc;
}

.treatment-plan {
  padding: clamp(6px, 0.8vh, 12px);
  border: clamp(1px, 0.1vh, 2px) solid #dcdfe6;
  border-radius: clamp(4px, 0.5vw, 8px);
  font-size: clamp(12px, 1.3vw, 16px);
  line-height: 1.4;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
  background-color: white;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  min-height: clamp(60px, 8vh, 80px);
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.treatment-plan::-webkit-scrollbar {
  width: 6px;
}

.treatment-plan::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.treatment-plan::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.treatment-plan::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.treatment-plan:focus {
  border-color: #409eff;
}

.treatment-plan::placeholder {
  color: #c0c4cc;
}

.remove-btn {
  width: clamp(24px, 3vw, 32px);
  height: clamp(24px, 3vw, 32px);
  border: none;
  background-color: #f56c6c;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: clamp(12px, 1.5vw, 18px);
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
  margin-top: clamp(1px, 0.2vh, 3px);
  flex-shrink: 0;
}

.remove-btn:hover {
  background-color: #e74c3c;
}

.add-diagnosis-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(6px, 0.8vw, 12px);
  padding: clamp(8px, 1vh, 16px) clamp(12px, 1.5vw, 24px);
  background-color: #f0f9ff;
  border: clamp(1px, 0.1vh, 3px) dashed #409eff;
  border-radius: clamp(6px, 0.8vw, 12px);
  color: #409eff;
  font-size: clamp(12px, 1.3vw, 16px);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: clamp(12px, 1.5vh, 20px);
}

.add-diagnosis-btn:hover {
  background-color: #e6f7ff;
  border-color: #337ecc;
  color: #337ecc;
}

.add-treatment-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(6px, 0.8vw, 12px);
  padding: clamp(8px, 1vh, 16px) clamp(12px, 1.5vw, 24px);
  background-color: #f0f9ff;
  border: clamp(1px, 0.1vh, 3px) dashed #409eff;
  border-radius: clamp(6px, 0.8vw, 12px);
  color: #409eff;
  font-size: clamp(12px, 1.3vw, 16px);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: clamp(12px, 1.5vh, 20px);
}

.add-treatment-btn:hover {
  background-color: #e6f7ff;
  border-color: #337ecc;
  color: #337ecc;
}

.add-icon {
  font-size: clamp(14px, 1.8vw, 22px);
  font-weight: bold;
}

.editable-textarea {
  flex: 1;
  min-height: clamp(60px, 8vh, 100px);
  padding: clamp(8px, 1vh, 16px);
  border: clamp(1px, 0.1vh, 3px) solid #dcdfe6;
  border-radius: clamp(4px, 0.5vw, 8px);
  font-size: clamp(12px, 1.3vw, 16px);
  line-height: 1.5;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.editable-textarea::-webkit-scrollbar {
  width: 6px;
}

.editable-textarea::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.editable-textarea::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.editable-textarea::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.editable-textarea:focus {
  border-color: #409eff;
}

.editable-textarea::placeholder {
  color: #c0c4cc;
}

.bottom-btn-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  margin-top: auto;
  margin-bottom: clamp(8px, 1vh, 16px);
  gap: clamp(8px, 1vw, 16px);
}

.next-btn {
  font-size: clamp(14px, 1.5vw, 20px);
  padding: clamp(8px, 1vh, 16px) clamp(24px, 3vw, 40px);
  background: #409eff;
  color: white;
  border: none;
  border-radius: clamp(6px, 0.8vw, 12px);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: background 0.2s;
  white-space: nowrap;
}

.next-btn:active {
  background: #337ecc;
}

.previous-btn {
  font-size: clamp(14px, 1.5vw, 20px);
  padding: clamp(8px, 1vh, 16px) clamp(24px, 3vw, 40px);
  background: #909399;
  color: white;
  border: none;
  border-radius: clamp(6px, 0.8vw, 12px);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: background 0.2s;
  white-space: nowrap;
}

.previous-btn:active {
  background: #737373;
}

.submit-btn {
  font-size: clamp(14px, 1.5vw, 20px);
  padding: clamp(8px, 1vh, 16px) clamp(24px, 3vw, 40px);
  background: #67c23a;
  color: white;
  border: none;
  border-radius: clamp(6px, 0.8vw, 12px);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: background 0.2s;
  white-space: nowrap;
}

.submit-btn:active {
  background: #5daf34;
}

/* 感谢页面样式 */
.thank-you-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.thank-you-content {
  text-align: center;
  background: white;
  padding: clamp(40px, 5vh, 80px) clamp(24px, 3vw, 48px);
  border-radius: clamp(16px, 2vw, 24px);
  box-shadow: 0 clamp(16px, 2vh, 32px) clamp(32px, 4vh, 48px) rgba(0, 0, 0, 0.1);
  max-width: clamp(400px, 50vw, 600px);
  width: 90%;
}

.thank-you-title {
  font-size: clamp(2rem, 4vw, 3rem);
  color: #333;
  margin-bottom: clamp(16px, 2vh, 24px);
  font-weight: 600;
}

.thank-you-message {
  font-size: clamp(1rem, 2vw, 1.4rem);
  color: #666;
  line-height: 1.6;
  margin-bottom: clamp(20px, 3vh, 32px);
}

.thank-you-icon {
  font-size: clamp(3rem, 6vw, 5rem);
  margin-top: clamp(16px, 2vh, 24px);
}

/* 响应式设计 - 小屏幕适配 */
@media (max-width: 768px) {
  .diagnosis-inputs {
    grid-template-columns: 1fr;
    gap: clamp(6px, 1vh, 12px);
  }
  
  .diagnosis-item, .treatment-item {
    flex-direction: column;
    gap: clamp(4px, 0.8vh, 8px);
  }
  
  .diagnosis-number, .treatment-number {
    align-self: flex-start;
  }
  
  .remove-btn {
    align-self: flex-end;
  }
  
  .bottom-btn-wrapper {
    flex-direction: column;
    gap: clamp(6px, 1vh, 12px);
  }
  
  .next-btn, .submit-btn {
    width: 100%;
    max-width: clamp(200px, 60vw, 300px);
  }
}

/* 超宽屏幕适配 */
@media (min-width: 1920px) {
  .content {
    padding: clamp(16px, 1.5vh, 24px);
    gap: clamp(20px, 2vh, 28px);
  }
  
  .diagnosis-list-container {
    max-height: clamp(300px, 40vh, 500px);
  }
  
  .treatment-list-container {
    max-height: clamp(250px, 30vh, 400px);
  }
  
  .diagnosis-item, .treatment-item {
    padding: clamp(16px, 1.5vh, 24px);
  }
  
  .bottom-btn-wrapper {
    margin-bottom: clamp(16px, 1.5vh, 24px);
  }
}
</style>
