<template>
  <div class="section-d-container">
    <!-- 原始案例内容 -->
    <div class="original-case-section">
      <h3>Original Case Content</h3>
      <div class="original-case-content">
        <div v-if="originalCase" v-html="formatOriginalCase(originalCase)"></div>
        <div v-else-if="loading" class="loading">Loading...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <div v-else class="no-data">No original case content is available.</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from "vue";

export default {
  name: "SectionD",
  props: {
    selectedEvaluator: {
      type: Object,
      default: null
    },
    username: {
      type: String,
      default: ''
    },
    // 添加案例ID属性，用于监听案例变化
    currentCaseId: {
      type: Number,
      default: 1
    }
  },
  setup(props) {
    const originalCase = ref('');
    const loading = ref(false);
    const error = ref('');

    // 格式化原始案例内容
    const formatOriginalCase = (originalCaseData) => {
      if (!originalCaseData) return '';
      
      try {
        const caseData = JSON.parse(originalCaseData);
        let formattedContent = '';
        
        // 患者自述
        if (caseData.prompt2) {
          formattedContent += caseData.prompt2 + '<br><br>';
        }
        
        // 检查内容 - 直接显示原始内容
        if (caseData.prompt3) {
          formattedContent += JSON.stringify(caseData.prompt3, null, 2) + '<br>';
        }
        
        return formattedContent;
      } catch (error) {
        console.error('格式化原始案例内容失败:', error);
        // 如果解析失败，直接返回原始内容
        return originalCaseData.replace(/\n/g, '<br>');
      }
    };

    // 获取原始案例内容
    const getOriginalCase = async (forceRefresh = false) => {
      if (!props.username) return;
      
      loading.value = true;
      error.value = '';
      
      try {
        const url = forceRefresh 
          ? `/api/evaluation/get-answer?username=${props.username}&force_refresh=true`
          : `/api/evaluation/get-answer?username=${props.username}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.status === 'success') {
          originalCase.value = data.originalCase || '';
          console.log('SectionD 获取到原始案例内容:', data.originalCase ? '有内容' : '无内容');
        } else {
          error.value = data.message || '获取原始案例失败';
          originalCase.value = '';
        }
      } catch (error) {
        console.error('获取原始案例失败:', error);
        error.value = '网络请求失败: ' + error.message;
        originalCase.value = '';
      } finally {
        loading.value = false;
      }
    };

    // 监听username变化
    watch(() => props.username, (newUsername) => {
      if (newUsername) {
        getOriginalCase();
      }
    }, { immediate: true });

    // 监听案例ID变化，当案例切换时重新获取内容
    watch(() => props.currentCaseId, (newCaseId, oldCaseId) => {
      if (newCaseId !== oldCaseId && props.username) {
        console.log(`SectionD 检测到案例变化: ${oldCaseId} -> ${newCaseId}`);
        // 使用强制刷新确保获取到最新的案例数据
        getOriginalCase(true);
      }
    }, { immediate: true });

    return {
      originalCase,
      loading,
      error,
      formatOriginalCase
    };
  }
};
</script>

<style scoped>
.section-d-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
  min-height: 0;
  padding: 16px;
  gap: 16px;
}

.original-case-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.original-case-section h3 {
  font-size: clamp(14px, 1.44vw, 12px); /* 缩小20%: 18px -> 14px, 1.8vw -> 1.44vw, 22px -> 18px */
  font-weight: 600;
  color: #333;
  margin: 0; /* 移除所有边距 */
  padding-bottom: clamp(6px, 0.64vw, 8px); /* 缩小20%: 8px -> 6px, 0.8vw -> 0.64vw, 10px -> 8px */
  border-bottom: 2px solid #e9ecef;
}

.original-case-content {
  flex: 1;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: clamp(16px, 1.6vw, 20px); /* 增大: 13px -> 16px, 1.28vw -> 1.6vw, 16px -> 20px */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
  overflow-x: hidden;
  cursor: text;
  transition: background-color 0.2s ease;
  color: #333;
  line-height: 1.6;
  white-space: pre-line;
  font-size: clamp(13px, 1.28vw, 12px); /* 缩小20%: 16px -> 13px, 1.6vw -> 1.28vw, 20px -> 16px */
}

.original-case-content:hover {
  background-color: #e9ecef;
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

.no-data {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .section-d-container {
    padding: 12px;
    gap: 16px;
  }
  
  .original-case-section h3 {
    font-size: 16px;
    margin-bottom: 12px;
  }
  
  .original-case-content {
    padding: 12px;
  }
}

/* 超宽屏幕适配 */
@media (min-width: 1920px) {
  .section-d-container {
    padding: 20px;
    gap: 24px;
  }
  
  .original-case-section h3 {
    font-size: 20px;
    margin-bottom: 20px;
  }
  
  .original-case-content {
    padding: 20px;
  }
}
</style>
