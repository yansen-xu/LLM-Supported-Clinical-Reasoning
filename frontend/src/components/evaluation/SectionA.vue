<template>
  <div class="content">
    <!-- 保存成功提示弹窗 -->
    <transition name="notification">
      <div v-if="showSaveNotification" class="save-notification">
        <div class="notification-content">
          <span class="notification-icon">✓</span>
          <span class="notification-text">顺序已保存</span>
        </div>
      </div>
    </transition>



    <!-- 醒目的提示框 -->
    <div class="instruction-box">
      <div class="instruction-icon">📋</div>
      <div class="instruction-content">
        <div class="instruction-text">1. Click avatar to view answer.</div>
        <div class="instruction-text">2. Drag to tier.</div>
        <div class="instruction-text">3. Reorder within tier.</div>
      </div>
    </div>

    <!-- 左右分栏布局 -->
    <div v-if="loading" class="loading">
      加载中...
    </div>
    <div v-else class="split-layout" ref="splitLayout">
      <!-- 左侧：所有作答者 -->
      <div class="left-panel"
           :class="{ 'drag-over': dragOverTier === 'available' }"
           @dragover="handleTierDragOver($event)"
           @drop="handleTierDrop($event, 'available')"
           @dragenter="handleTierDragEnter($event, 'available')"
           @dragleave="handleTierDragLeave($event)"
           @dragend="handleDragEnd">
        <div class="panel-header">
          <div class="panel-title">Rest</div>
          <div class="panel-count">({{ availableEvaluators.length }})</div>
        </div>
        <div class="evaluators-list">
          <div 
            v-for="(evaluator, index) in availableEvaluators" 
            :key="evaluator.id" 
            class="evaluator-item"
            :class="{ 
              'selected': selectedEvaluator && selectedEvaluator.id === evaluator.id,
              'dragging': draggedIndex === index && draggedTier === 'available',
              'drag-over': dragOverIndex === index && draggedTier === 'available' && draggedIndex !== index
            }"
            :draggable="true"
            @dragstart="handleDragStart(index, $event, 'available')"
            @dragover="handleDragOver($event)"
            @drop="handleDrop(index, $event, 'available')"
            @dragenter="handleDragEnter(index, $event)"
            @dragleave="handleDragLeave($event)"
            @dragend="handleDragEnd"
            @click="selectEvaluator(evaluator)"
          >
            <div class="evaluator-header">
              <div class="evaluator-image-container">
                <img 
                  :src="require('@/assets/user.png')" 
                  alt="评估者头像" 
                  class="evaluator-image"
                />
              </div>
              <div class="player-name">{{ evaluator.name }}</div>
              <div class="rank-indicator">{{ index + 1 }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：档位容器 -->
      <div class="right-panel">
        <!-- 好档位 -->
        <div class="tier-section" 
             :class="{ 'drag-over': dragOverTier === 'good' }"
             @dragover="handleTierDragOver($event)"
             @drop="handleTierDrop($event, 'good')"
             @dragenter="handleTierDragEnter($event, 'good')"
             @dragleave="handleTierDragLeave($event)"
             @dragend="handleDragEnd">
          <div class="tier-header good-tier">
            <div class="tier-title">Good</div>
            <div class="tier-count">({{ goodTier.length }})</div>
          </div>
          <div class="tier-content">
            <div 
              v-for="(evaluator, index) in goodTier" 
              :key="evaluator.id" 
              class="evaluator-item"
              :class="{ 
                'selected': selectedEvaluator && selectedEvaluator.id === evaluator.id,
                'dragging': draggedIndex === index && draggedTier === 'good',
                'drag-over': dragOverIndex === index && draggedTier === 'good' && draggedIndex !== index
              }"
              :draggable="true"
              @dragstart="handleDragStart(index, $event, 'good')"
              @dragover="handleDragOver($event)"
              @drop="handleDrop(index, $event, 'good')"
              @dragenter="handleDragEnter(index, $event)"
              @dragleave="handleDragLeave($event)"
              @dragend="handleDragEnd"
              @click="selectEvaluator(evaluator)"
            >
              <div class="evaluator-header">
                <div class="evaluator-image-container">
                  <img 
                    :src="require('@/assets/user.png')" 
                    alt="评估者头像" 
                    class="evaluator-image"
                  />
                </div>
                <div class="player-name">{{ evaluator.name }}</div>
                <div class="rank-indicator">{{ getGlobalRank(evaluator) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 中档位 -->
        <div class="tier-section" 
             :class="{ 'drag-over': dragOverTier === 'medium' }"
             @dragover="handleTierDragOver($event)"
             @drop="handleTierDrop($event, 'medium')"
             @dragenter="handleTierDragEnter($event, 'medium')"
             @dragleave="handleTierDragLeave($event)"
             @dragend="handleDragEnd">
          <div class="tier-header medium-tier">
            <div class="tier-title">Medium</div>
            <div class="tier-count">({{ mediumTier.length }})</div>
          </div>
          <div class="tier-content">
            <div 
              v-for="(evaluator, index) in mediumTier" 
              :key="evaluator.id" 
              class="evaluator-item"
              :class="{ 
                'selected': selectedEvaluator && selectedEvaluator.id === evaluator.id,
                'dragging': draggedIndex === index && draggedTier === 'medium',
                'drag-over': dragOverIndex === index && draggedTier === 'medium' && draggedIndex !== index
              }"
              :draggable="true"
              @dragstart="handleDragStart(index, $event, 'medium')"
              @dragover="handleDragOver($event)"
              @drop="handleDrop(index, $event, 'medium')"
              @dragenter="handleDragEnter(index, $event)"
              @dragleave="handleDragLeave($event)"
              @dragend="handleDragEnd"
              @click="selectEvaluator(evaluator)"
            >
              <div class="evaluator-header">
                <div class="evaluator-image-container">
                  <img 
                    :src="require('@/assets/user.png')" 
                    alt="评估者头像" 
                    class="evaluator-image"
                  />
                </div>
                <div class="player-name">{{ evaluator.name }}</div>
                <div class="rank-indicator">{{ getGlobalRank(evaluator) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 差档位 -->
        <div class="tier-section" 
             :class="{ 'drag-over': dragOverTier === 'poor' }"
             @dragover="handleTierDragOver($event)"
             @drop="handleTierDrop($event, 'poor')"
             @dragenter="handleTierDragEnter($event, 'poor')"
             @dragleave="handleTierDragLeave($event)"
             @dragend="handleDragEnd">
          <div class="tier-header poor-tier">
            <div class="tier-title">Poor</div>
            <div class="tier-count">({{ poorTier.length }})</div>
          </div>
          <div class="tier-content">
            <div 
              v-for="(evaluator, index) in poorTier" 
              :key="evaluator.id" 
              class="evaluator-item"
              :class="{ 
                'selected': selectedEvaluator && selectedEvaluator.id === evaluator.id,
                'dragging': draggedIndex === index && draggedTier === 'poor',
                'drag-over': dragOverIndex === index && draggedTier === 'poor' && draggedIndex !== index
              }"
              :draggable="true"
              @dragstart="handleDragStart(index, $event, 'poor')"
              @dragover="handleDragOver($event)"
              @drop="handleDrop(index, $event, 'poor')"
              @dragenter="handleDragEnter(index, $event)"
              @dragleave="handleDragLeave($event)"
              @dragend="handleDragEnd"
              @click="selectEvaluator(evaluator)"
            >
              <div class="evaluator-header">
                <div class="evaluator-image-container">
                  <img 
                    :src="require('@/assets/user.png')" 
                    alt="评估者头像" 
                    class="evaluator-image"
                  />
                </div>
                <div class="player-name">Analyst {{ evaluator.initialOrder }}</div>
                <div class="rank-indicator">{{ getGlobalRank(evaluator) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：排序说明容器 -->
      <div class="sorting-instruction-panel">
        <div class="instruction-text-vertical">
          Please rank all Analysts according to your overall assessment of their performance.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

// 配置axios baseURL
axios.defaults.baseURL = process.env.NODE_ENV === 'development' 
  ? '' // 在开发环境中使用相对路径，通过Vue代理
  : window.location.origin;

export default {
  name: "SectionA",
  props: {
    username: {
      type: String,
      required: true
    },
    currentCaseId: {
      type: Number,
      default: 1
    },
    navigationDirection: {
      type: String,
      default: null
    }
  },
  emits: ['evaluator-selected', 'available-evaluators-changed'],
  data() {
    return {
      evaluators: [],
      selectedEvaluator: null,
      loading: false,
      draggedIndex: null,
      dragOverIndex: null,
      draggedTier: null,
      dragOverTier: null,
      showSaveNotification: false,
      // 档位数据
      goodTier: [],
      mediumTier: [],
      poorTier: [],
      availableEvaluators: [], // 左侧可用的作答者
      // 自动滚动相关
      autoScrollInterval: null,
      scrollSpeed: 5,
      scrollThreshold: 50
    }
  },
  computed: {
    // 获取全局排名
    getGlobalRank() {
      return (evaluator) => {
        // 在拖拽过程中，不更新排名，保持稳定
        if (this.draggedIndex !== null || this.dragOverIndex !== null) {
          return evaluator.stableRank || 1;
        }
        
        const allEvaluators = [...this.goodTier, ...this.mediumTier, ...this.poorTier];
        const rank = allEvaluators.findIndex(e => e.id === evaluator.id) + 1;
        
        // 缓存稳定排名
        evaluator.stableRank = rank;
        return rank;
      }
    }
  },
  methods: {
    async loadEvaluators() {
      this.loading = true;
      
      try {
        // 首先从后端加载用户评分数据
        await this.loadUserScoresFromBackend();
        
        // 然后获取当前案例信息，以确定正确的案例ID
        const caseResponse = await fetch(`/api/evaluation/current-case?username=${this.username}`);
        const caseData = await caseResponse.json();
        
        if (caseData.status !== 'success') {
          throw new Error('获取当前案例信息失败');
        }
        
        // 从case_filename中提取案例ID
        let actualCaseId = this.currentCaseId;
        if (caseData.case_filename && caseData.case_filename.startsWith('case')) {
          actualCaseId = parseInt(caseData.case_filename.replace('case', ''));
        }
        
        const apiUrl = `/api/evaluation/case/${actualCaseId}/evaluators`;
        console.log('请求API:', apiUrl, '实际caseId:', actualCaseId, '传入caseId:', this.currentCaseId);
        
        const response = await fetch(apiUrl);
        console.log('API响应状态:', response.status, response.statusText);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('API响应数据:', data);
        
        if (data.status === 'success') {
          this.evaluators = data.evaluators;
          
          // 为每个评估者添加初始顺序（player x）
          this.evaluators.forEach((evaluator, index) => {
            evaluator.initialOrder = index + 1;
          });
          
          // 初始化档位分配
          this.initializeTiers();
          
          // 从后端加载排序数据
          await this.loadUserRankingFromBackend();
          
          // 如果没有后端数据，尝试从localStorage加载
          if (this.goodTier.length === 0 && this.mediumTier.length === 0 && this.poorTier.length === 0) {
            this.loadSavedOrder();
          }
          
          // 默认选中第一个评估者
          if (this.evaluators.length > 0 && !this.selectedEvaluator) {
            this.selectEvaluator(this.evaluators[0]);
          }
          console.log(`成功加载用户 ${this.username} 的评估者:`, this.evaluators);
        } else {
          console.error('加载评估者失败:', data.error);
        }
      } catch (error) {
        console.error('加载评估者请求失败:', error);
      } finally {
        this.loading = false;
      }
    },

    selectEvaluator(evaluator) {
      this.selectedEvaluator = evaluator;
      // 向父组件发送选中的评估者信息
      this.$emit('evaluator-selected', {
        caseId: this.currentCaseId,
        evaluator: evaluator
      });
    },

    // 初始化档位分配
    initializeTiers() {
      // 将所有作答者放在左侧可用区域
      this.availableEvaluators = [...this.evaluators];
      this.goodTier = [];
      this.mediumTier = [];
      this.poorTier = [];
      
      // 初始化完成
      
      // 通知父组件初始状态
      this.$emit('available-evaluators-changed', this.availableEvaluators.length);
    },

    // 档位间拖拽相关方法
    handleTierDragOver(event) {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
      console.log('档位拖拽悬停:', event.target.className);
    },

    handleTierDragEnter(event, tier) {
      event.preventDefault();
      this.dragOverTier = tier;
    },

    handleTierDragLeave(event) {
      // 检查鼠标是否真的离开了档位区域
      const rect = event.currentTarget.getBoundingClientRect();
      const x = event.clientX;
      const y = event.clientY;
      
      if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
        this.dragOverTier = null;
      }
    },

        async handleTierDrop(event, targetTier) {
      event.preventDefault();
      event.stopPropagation(); // 阻止事件冒泡
      
      console.log('档位拖拽事件触发:', {
        draggedTier: this.draggedTier,
        targetTier: targetTier,
        draggedIndex: this.draggedIndex
      });
      
      if (!this.draggedTier) {
        console.log('无效的拖拽操作');
        this.draggedTier = null;
        this.dragOverTier = null;
        return;
      }

      // 获取拖拽的评估者
      const sourceTier = this.getTierArray(this.draggedTier);
      const draggedEvaluator = sourceTier[this.draggedIndex];
      
      if (!draggedEvaluator) {
        console.log('未找到拖拽的评估者');
        return;
      }

      console.log('移动评估者:', {
        evaluator: draggedEvaluator.initialOrder,
        from: this.draggedTier,
        to: targetTier
      });

      // 从源档位移除
      this.removeFromTier(this.draggedTier, this.draggedIndex);
      
      // 添加到目标档位
      this.addToTier(targetTier, draggedEvaluator);
      
      // 保存排序
      await this.saveOrderToLocalStorage();
      
      // 只在有评分数据时才保存到后端，避免覆盖评分
      const hasScores = this.checkIfCaseHasScores();
      if (hasScores) {
        this.markCaseAsSorted();
      }
      
      // 强制重新计算布局
      this.forceLayoutUpdate();
      
      // 重置拖拽状态
      this.draggedIndex = null;
      this.draggedTier = null;
      this.dragOverTier = null;
      
      console.log('拖拽完成，当前状态:', {
        available: this.availableEvaluators.length,
        good: this.goodTier.length,
        medium: this.mediumTier.length,
        poor: this.poorTier.length
      });
    },

    // 获取档位数组
    getTierArray(tier) {
      switch (tier) {
        case 'available': return this.availableEvaluators;
        case 'good': return this.goodTier;
        case 'medium': return this.mediumTier;
        case 'poor': return this.poorTier;
        default: return [];
      }
    },

    // 从档位移除评估者
    removeFromTier(tier, index) {
      switch (tier) {
        case 'available':
          this.availableEvaluators.splice(index, 1);
          break;
        case 'good':
          this.goodTier.splice(index, 1);
          break;
        case 'medium':
          this.mediumTier.splice(index, 1);
          break;
        case 'poor':
          this.poorTier.splice(index, 1);
          break;
      }
    },

    // 添加评估者到档位
    addToTier(tier, evaluator) {
      switch (tier) {
        case 'available':
          this.availableEvaluators.push(evaluator);
          break;
        case 'good':
          this.goodTier.push(evaluator);
          break;
        case 'medium':
          this.mediumTier.push(evaluator);
          break;
        case 'poor':
          this.poorTier.push(evaluator);
          break;
      }
    },

    // 拖拽相关方法
    handleDragStart(index, event, tier) {
      console.log('开始拖拽:', {
        index: index,
        tier: tier,
        evaluator: this.getTierArray(tier)[index]?.initialOrder
      });
      
      // 在开始拖拽时，为所有评估者设置稳定排名
      this.evaluators.forEach(evaluator => {
        const allEvaluators = [...this.goodTier, ...this.mediumTier, ...this.poorTier];
        evaluator.stableRank = allEvaluators.findIndex(e => e.id === evaluator.id) + 1;
      });
      
      this.draggedIndex = index;
      this.draggedTier = tier;
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/html', event.target.outerHTML);
      
      // 开始监听拖拽移动事件
      document.addEventListener('dragover', this.handleGlobalDragOver);
    },



    handleDragOver(event) {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
    },

    handleDragEnter(index, event) {
      event.preventDefault();
      this.dragOverIndex = index;
    },

         handleDragLeave(event) {
       // 只有当鼠标真正离开元素时才清除高亮
       // 检查鼠标是否真的离开了当前元素
       const rect = event.currentTarget.getBoundingClientRect();
       const x = event.clientX;
       const y = event.clientY;
       
       if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
         this.dragOverIndex = null;
       }
     },

         async handleDrop(index, event, tier) {
       event.preventDefault();
       event.stopPropagation(); // 阻止事件冒泡
       
       console.log('处理拖拽放置:', {
         draggedIndex: this.draggedIndex,
         targetIndex: index,
         draggedTier: this.draggedTier,
         targetTier: tier
       });
       
       if (this.draggedIndex === null) {
         this.draggedIndex = null;
         this.dragOverIndex = null;
         this.draggedTier = null;
         return;
       }

       // 如果是同一容器内的排序
       if (this.draggedTier === tier) {
         if (this.draggedIndex === index) {
           // 没有实际移动
           this.draggedIndex = null;
           this.dragOverIndex = null;
           this.draggedTier = null;
           return;
         }
         
         // 同一容器内重新排序
         const tierArray = this.getTierArray(tier);
         const draggedEvaluator = tierArray[this.draggedIndex];
         
         // 移除拖拽的元素
         tierArray.splice(this.draggedIndex, 1);
         // 在目标位置插入
         tierArray.splice(index, 0, draggedEvaluator);
         
         console.log('同一容器内重新排序完成');
       } else {
         // 跨容器移动
         const sourceTier = this.getTierArray(this.draggedTier);
         const draggedEvaluator = sourceTier[this.draggedIndex];
         
         if (!draggedEvaluator) {
           this.draggedIndex = null;
           this.dragOverIndex = null;
           this.draggedTier = null;
           return;
         }
         
         // 从源容器移除
         this.removeFromTier(this.draggedTier, this.draggedIndex);
         
         // 添加到目标容器
         this.addToTier(tier, draggedEvaluator);
         
         console.log('跨容器移动完成');
       }
       
       // 保存排序
       await this.saveOrderToLocalStorage();
       
       // 只在有评分数据时才保存到后端，避免覆盖评分
       const hasScores = this.checkIfCaseHasScores();
       if (hasScores) {
         this.markCaseAsSorted();
       }
       
       // 强制重新计算布局
       this.forceLayoutUpdate();
       
       // 重置拖拽状态
       this.draggedIndex = null;
       this.dragOverIndex = null;
       this.draggedTier = null;
     },

     handleDragEnd() {
       console.log('拖拽结束，清除状态');
       // 拖拽结束时清除所有拖拽状态
       this.draggedIndex = null;
       this.dragOverIndex = null;
       this.draggedTier = null;
       this.dragOverTier = null;
       
       // 清除所有评估者的稳定排名，让排名恢复正常更新
       this.evaluators.forEach(evaluator => {
         delete evaluator.stableRank;
       });
       
       // 停止自动滚动
       this.stopAutoScroll();
       
       // 移除全局事件监听
       document.removeEventListener('dragover', this.handleGlobalDragOver);
     },

     // 全局拖拽移动监听
     handleGlobalDragOver(event) {
       this.checkAutoScroll(event);
     },

     // 检查是否需要自动滚动
     checkAutoScroll(event) {
       const container = this.$refs.splitLayout;
       if (!container) return;

       const rect = container.getBoundingClientRect();
       const mouseY = event.clientY;
       
       // 计算距离容器顶部和底部的距离
       const distanceFromTop = mouseY - rect.top;
       const distanceFromBottom = rect.bottom - mouseY;
       
       // 停止之前的自动滚动
       this.stopAutoScroll();
       
       // 检查是否需要向上滚动
       if (distanceFromTop < this.scrollThreshold && distanceFromTop > 0 && container.scrollTop > 0) {
         this.startAutoScroll('up');
       }
       // 检查是否需要向下滚动
       else if (distanceFromBottom < this.scrollThreshold && distanceFromBottom > 0 && 
                container.scrollTop < container.scrollHeight - container.clientHeight) {
         this.startAutoScroll('down');
       }
     },

     // 开始自动滚动
     startAutoScroll(direction) {
       const container = this.$refs.splitLayout;
       if (!container) return;

       this.autoScrollInterval = setInterval(() => {
         if (direction === 'up') {
           container.scrollTop -= this.scrollSpeed;
         } else {
           container.scrollTop += this.scrollSpeed;
         }
       }, 16); // 约60fps
     },

     // 停止自动滚动
     stopAutoScroll() {
       if (this.autoScrollInterval) {
         clearInterval(this.autoScrollInterval);
         this.autoScrollInterval = null;
       }
     },

     // 强制重新计算容器高度
     forceLayoutUpdate() {
       this.$nextTick(() => {
         // 触发重新布局
         const container = this.$refs.splitLayout;
         if (container) {
           container.style.height = container.scrollHeight + 'px';
           setTimeout(() => {
             container.style.height = '';
           }, 10);
         }
       });
     },

             // 保存排序到localStorage和后端
    async saveOrderToLocalStorage() {
      const username = this.username;
      const caseId = this.currentCaseId;
      const storageKey = `evaluator_ranking_${username}`;
      
      // 获取现有的排序数据
      const existingRankings = JSON.parse(localStorage.getItem(storageKey) || '{}');
      
      // 更新当前case的排序（保存真实ID用于后端）
      // 只保存档位内的排序：好 -> 中 -> 差
      const allEvaluators = [...this.goodTier, ...this.mediumTier, ...this.poorTier];
      const ranking = allEvaluators.map(evaluator => evaluator.id);
      existingRankings[`case${caseId}`] = ranking;
      
      // 保存回localStorage
      localStorage.setItem(storageKey, JSON.stringify(existingRankings));
      
      // 构建档位数据
      const tiers = {
        good: this.goodTier.map(evaluator => evaluator.id),
        medium: this.mediumTier.map(evaluator => evaluator.id),
        poor: this.poorTier.map(evaluator => evaluator.id)
      };
      
      // 保存到后端
      try {
        const response = await fetch('/api/evaluation/save-ranking', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: username,
            case_id: `case${caseId}`,
            ranking: ranking,
            tiers: tiers
          })
        });
        
        if (response.ok) {
          console.log(`排序数据已保存到后端: case${caseId}`, { ranking, tiers });
        } else {
          console.error('保存排序数据到后端失败:', response.statusText);
        }
      } catch (error) {
        console.error('保存排序数据到后端出错:', error);
      }
      
      console.log(`保存case${caseId}的评估者排序:`, ranking);
    },

    // 从后端加载用户评分数据
    async loadUserScoresFromBackend() {
      if (!this.username) return
      
      try {
        const response = await fetch(`/api/evaluation/get-user-scores?username=${this.username}`)
        if (response.ok) {
          const data = await response.json()
          if (data.status === 'success' && data.scores) {
            // 将后端数据同步到localStorage
            const storageKey = `evaluation_scores_${this.username}`
            localStorage.setItem(storageKey, JSON.stringify(data.scores))
            console.log('SectionA 从后端加载用户评分数据成功:', data.scores)
          }
        } else {
          console.error('SectionA 从后端加载用户评分数据失败:', response.statusText)
        }
      } catch (error) {
        console.error('SectionA 从后端加载用户评分数据出错:', error)
      }
    },

    // 从后端加载用户排序数据
    async loadUserRankingFromBackend() {
      if (!this.username || !this.currentCaseId) return
      
      try {
        const response = await fetch(`/api/evaluation/get-ranking?username=${this.username}&case_id=case${this.currentCaseId}`)
        if (response.ok) {
          const data = await response.json()
          if (data.status === 'success') {
            console.log('SectionA 从后端加载排序数据成功:', data)
            
            // 如果有排序数据，应用排序
            if (data.ranking && data.ranking.length > 0) {
              this.applyRankingFromBackend(data.ranking, data.tiers)
            }
          }
        } else {
          console.error('SectionA 从后端加载排序数据失败:', response.statusText)
        }
      } catch (error) {
        console.error('SectionA 从后端加载排序数据出错:', error)
      }
    },

    // 应用从后端加载的排序数据
    applyRankingFromBackend(ranking, tiers) {
      if (!ranking || ranking.length === 0) return
      
      const evaluatorMap = new Map(this.evaluators.map(e => [e.id, e]))
      
      // 清空档位
      this.goodTier = []
      this.mediumTier = []
      this.poorTier = []
      this.availableEvaluators = []
      
      // 如果有档位数据，使用档位数据
      if (tiers && Object.keys(tiers).length > 0) {
        // 使用保存的档位数据
        if (tiers.good) {
          tiers.good.forEach(evaluatorId => {
            const evaluator = evaluatorMap.get(evaluatorId)
            if (evaluator) {
              this.goodTier.push(evaluator)
              evaluatorMap.delete(evaluatorId)
            }
          })
        }
        
        if (tiers.medium) {
          tiers.medium.forEach(evaluatorId => {
            const evaluator = evaluatorMap.get(evaluatorId)
            if (evaluator) {
              this.mediumTier.push(evaluator)
              evaluatorMap.delete(evaluatorId)
            }
          })
        }
        
        if (tiers.poor) {
          tiers.poor.forEach(evaluatorId => {
            const evaluator = evaluatorMap.get(evaluatorId)
            if (evaluator) {
              this.poorTier.push(evaluator)
              evaluatorMap.delete(evaluatorId)
            }
          })
        }
      } else {
        // 如果没有档位数据，根据排序数据自动分配档位
        ranking.forEach(evaluatorId => {
          const evaluator = evaluatorMap.get(evaluatorId)
          if (evaluator) {
            const index = ranking.indexOf(evaluatorId)
            const totalCount = ranking.length
            const goodCount = Math.ceil(totalCount / 3)
            const mediumCount = Math.ceil((totalCount - goodCount) / 2)
            
            if (index < goodCount) {
              this.goodTier.push(evaluator)
            } else if (index < goodCount + mediumCount) {
              this.mediumTier.push(evaluator)
            } else {
              this.poorTier.push(evaluator)
            }
            
            evaluatorMap.delete(evaluatorId)
          }
        })
      }
      
      // 添加任何未在排序中的评估者到可用区域
      evaluatorMap.forEach(evaluator => {
        this.availableEvaluators.push(evaluator)
      })
      
      console.log('从后端应用排序数据完成:', {
        good: this.goodTier.length,
        medium: this.mediumTier.length,
        poor: this.poorTier.length,
        available: this.availableEvaluators.length
      })
      
      // 通知父组件availableEvaluators数量发生变化
      this.$emit('available-evaluators-changed', this.availableEvaluators.length)
    },

    // 从localStorage加载保存的排序
    loadSavedOrder() {
      const username = this.username;
      const caseId = this.currentCaseId;
      const storageKey = `evaluator_ranking_${username}`;
      
      const savedRankings = JSON.parse(localStorage.getItem(storageKey) || '{}');
      const savedOrder = savedRankings[`case${caseId}`];
      
      if (savedOrder && savedOrder.length > 0) {
        // 根据保存的顺序重新分配档位
        const evaluatorMap = new Map(this.evaluators.map(e => [e.id, e]));
        
        // 清空档位
        this.goodTier = [];
        this.mediumTier = [];
        this.poorTier = [];
        this.availableEvaluators = [];
        
        // 按照保存的顺序重新分配档位
        savedOrder.forEach(evaluatorId => {
          const evaluator = evaluatorMap.get(evaluatorId);
          if (evaluator) {
            // 根据在保存顺序中的位置决定档位
            const index = savedOrder.indexOf(evaluatorId);
            const totalCount = savedOrder.length;
            const goodCount = Math.ceil(totalCount / 3);
            const mediumCount = Math.ceil((totalCount - goodCount) / 2);
            
            if (index < goodCount) {
              this.goodTier.push(evaluator);
            } else if (index < goodCount + mediumCount) {
              this.mediumTier.push(evaluator);
            } else {
              this.poorTier.push(evaluator);
            }
            
            evaluatorMap.delete(evaluatorId);
          }
        });
        
        // 添加任何未在保存顺序中的评估者（新添加的）
        evaluatorMap.forEach(evaluator => {
          this.availableEvaluators.push(evaluator);
        });
        
                 console.log(`加载case${caseId}的档位排序:`, {
           good: this.goodTier.length,
           medium: this.mediumTier.length,
           poor: this.poorTier.length,
           available: this.availableEvaluators.length
         });
         
         // 通知父组件availableEvaluators数量发生变化
         this.$emit('available-evaluators-changed', this.availableEvaluators.length);
      }
    },

    // 获取当前case的排序数据（供SectionE使用）
    getCurrentCaseRanking() {
      // 只返回档位内的排序：好 -> 中 -> 差
      const allEvaluators = [...this.goodTier, ...this.mediumTier, ...this.poorTier];
      return allEvaluators.map(evaluator => evaluator.id);
    },

    // 检查case的排序状态并相应处理
    async checkCaseSortingStatus() {
      try {
        const caseId = this.currentCaseId;
        const response = await fetch(`/api/evaluation/get-case-state?username=${this.username}&case_id=case${caseId}`);
        const data = await response.json();
        
        if (data.status === 'success') {
          const caseState = data.case_state;
          console.log(`case${caseId} 状态:`, caseState);
          console.log(`导航方向:`, this.navigationDirection);
          
          if (caseState.saved && caseState.ranking && caseState.ranking.length > 0) {
            // case已经被保存过，使用保存的排序
            this.applySavedRanking(caseState.ranking);
            console.log(`case${caseId} 使用保存的排序:`, caseState.ranking);
            
            // 恢复保存的评分数据
            if (caseState.evaluators) {
              this.restoreSavedScores(caseState.evaluators);
            }
          } else {
            // case没有被保存过，根据导航方向决定是否随机打乱
            if (this.navigationDirection === 'previous') {
              // 点击"上一个"：不打乱，使用默认顺序
              console.log(`case${caseId} 点击"上一个"，不打乱顺序`);
            } else if (this.navigationDirection === null) {
              // 返回修改时：尝试从localStorage加载排序，如果没有则不打乱
              this.loadSavedOrder();
              console.log(`case${caseId} 返回修改，尝试从localStorage加载排序`);
            } else {
              // 点击"下一个"或初始加载：保持原始顺序，不随机打乱
              // 这样可以避免在提交时出现意外的顺序变化
              console.log(`case${caseId} 点击"下一个"或初始加载，保持原始顺序`);
            }
          }
        }
      } catch (error) {
        console.error('检查case排序状态失败:', error);
        // 出错时根据导航方向决定
        if (this.navigationDirection === 'previous') {
          console.log('出错时点击"上一个"，不打乱顺序');
        } else if (this.navigationDirection === null) {
          // 返回修改时，尝试从localStorage加载排序
          this.loadSavedOrder();
          console.log('出错时导航方向为null，尝试从localStorage加载排序');
        } else {
          // 出错时保持原始顺序，不随机打乱
          console.log('出错时保持原始顺序，不随机打乱');
        }
      }
    },

    // 应用保存的排序
    applySavedRanking(savedRanking) {
      if (!savedRanking || savedRanking.length === 0) return;
      
      const evaluatorMap = new Map(this.evaluators.map(e => [e.id, e]));
      
      // 清空档位
      this.goodTier = [];
      this.mediumTier = [];
      this.poorTier = [];
      this.availableEvaluators = [];
      
      // 按照保存的顺序重新分配档位
      savedRanking.forEach(evaluatorId => {
        const evaluator = evaluatorMap.get(evaluatorId);
        if (evaluator) {
          // 根据在保存顺序中的位置决定档位
          const index = savedRanking.indexOf(evaluatorId);
          const totalCount = savedRanking.length;
          const goodCount = Math.ceil(totalCount / 3);
          const mediumCount = Math.ceil((totalCount - goodCount) / 2);
          
          if (index < goodCount) {
            this.goodTier.push(evaluator);
          } else if (index < goodCount + mediumCount) {
            this.mediumTier.push(evaluator);
          } else {
            this.poorTier.push(evaluator);
          }
          
          evaluatorMap.delete(evaluatorId);
        }
      });
      
      // 添加任何未在保存顺序中的评估者
      evaluatorMap.forEach(evaluator => {
        this.availableEvaluators.push(evaluator);
      });
      
      // 通知父组件availableEvaluators数量发生变化
      this.$emit('available-evaluators-changed', this.availableEvaluators.length);
    },

    // 恢复保存的评分数据
    restoreSavedScores(savedEvaluators) {
      if (!savedEvaluators || typeof savedEvaluators !== 'object') return;
      
      const username = this.username;
      const caseId = this.currentCaseId;
      const storageKey = `evaluation_scores_${username}`;
      const scores = JSON.parse(localStorage.getItem(storageKey) || '{}');
      
      const caseKey = `case${caseId}`;
      if (!scores[caseKey]) {
        scores[caseKey] = {};
      }
      
      // 恢复每个评估者的评分数据
      Object.keys(savedEvaluators).forEach(evaluatorId => {
        const evaluatorData = savedEvaluators[evaluatorId];
        if (evaluatorData && evaluatorData.dimensions) {
          scores[caseKey][evaluatorId] = evaluatorData.dimensions;
        }
      });
      
      // 保存回localStorage
      localStorage.setItem(storageKey, JSON.stringify(scores));
      console.log(`恢复了case${caseId}的评分数据`);
    },

    // 随机打乱评估者顺序
    shuffleEvaluators() {
      const shuffled = [...this.evaluators];
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      this.evaluators = shuffled;
    },

    // 标记当前case为已排序（保存到后端）
    async markCaseAsSorted() {
      try {
        // 获取当前case的所有评估者
        const caseEvaluators = await this.getCaseEvaluators(this.currentCaseId);
        
        // 获取当前所有维度的列表
        const currentDimensions = await this.getCurrentDimensions();
        
        // 获取排名数据，如果没有则使用评估者的原始顺序（从API获取的顺序）
        let rankingData = this.getCurrentCaseRanking();
        if (!rankingData || rankingData.length === 0) {
          rankingData = caseEvaluators;
        }
        
        // 构建完整的case数据
        const caseData = {
          username: this.username,
          case_id: `case${this.currentCaseId}`,
          ranking: rankingData
        };
        
        // 遍历当前case的所有评估者，获取每个评估者的评分数据
        for (const evaluatorId of caseEvaluators) {
          // 获取该评估者的评分数据
          const evaluatorScores = this.getEvaluatorScores(this.currentCaseId, evaluatorId);
          
          // 直接以评估者ID为键，dimensions为值
          caseData[evaluatorId] = {
            dimensions: { ...evaluatorScores } // 直接复制已有的评分数据
          };
          
          // 处理所有维度，只填充缺失的维度（设为0分）
          currentDimensions.forEach((dimension) => {
            if (!(dimension.id in caseData[evaluatorId].dimensions)) {
              caseData[evaluatorId].dimensions[dimension.id] = 0;
            }
          });
        }
        
        const response = await fetch('/api/evaluation/save-case-state', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(caseData)
        });
        
        const data = await response.json();
        if (data.status === 'success') {
          console.log(`case${this.currentCaseId} 已标记为已排序并保存评分数据`);
          // 显示保存成功提示
          this.showSaveSuccessNotification();
        } else {
          console.error('标记case为已排序失败:', data);
        }
      } catch (error) {
        console.error('标记case为已排序请求失败:', error);
      }
    },

    // 显示保存成功提示
    showSaveSuccessNotification() {
      this.showSaveNotification = true;
      // 2秒后自动隐藏
      setTimeout(() => {
        this.showSaveNotification = false;
      }, 2000);
    },

    // 获取指定case的评估者列表
    async getCaseEvaluators(caseId) {
      try {
        const response = await fetch(`/api/evaluation/case/${caseId}/evaluators`);
        const data = await response.json();
        if (data.status === 'success' && data.evaluators) {
          return data.evaluators.map(evaluator => evaluator.id);
        }
        return [];
      } catch (error) {
        console.error(`获取case ${caseId} 的evaluator列表失败:`, error);
        return [];
      }
    },

    // 获取当前所有维度的列表
    async getCurrentDimensions() {
      try {
        const response = await fetch('/api/evaluation/dimensions');
        if (response.ok) {
          const savedCategories = await response.json();
          
          // 将分类结构转换为扁平化的维度列表
          const dimensions = [];
          savedCategories.forEach((category) => {
            category.dimensions.forEach((dimension) => {
              dimensions.push({
                id: `${category.category}-${dimension}`,
                name: dimension,
                category: category.category
              });
            });
          });
          
          return dimensions;
        } else {
          console.error('获取维度数据失败');
          return [];
        }
      } catch (error) {
        console.error('获取维度数据出错:', error);
        return [];
      }
    },

    // 获取指定评估者的评分数据
    getEvaluatorScores(caseId, evaluatorId) {
      const username = this.username;
      const storageKey = `evaluation_scores_${username}`;
      const scores = JSON.parse(localStorage.getItem(storageKey) || '{}');
      
      const caseKey = `case${caseId}`;
      const evaluatorData = scores[caseKey]?.[evaluatorId] || {};
      
      // 返回dimensions对象，保持与新的数据结构一致
      return evaluatorData.dimensions || {};
    },

    // 检查当前case是否有评分数据
    checkIfCaseHasScores() {
      const username = this.username;
      const caseId = this.currentCaseId;
      const storageKey = `evaluation_scores_${username}`;
      const scores = JSON.parse(localStorage.getItem(storageKey) || '{}');
      
      const caseKey = `case${caseId}`;
      const caseScores = scores[caseKey] || {};
      
      // 检查是否有任何评估者有评分数据
      for (const evaluatorId in caseScores) {
        const evaluatorData = caseScores[evaluatorId];
        if (evaluatorData && evaluatorData.dimensions) {
          const dimensions = evaluatorData.dimensions;
          for (const dimensionKey in dimensions) {
            if (dimensions[dimensionKey] > 0) {
              return true; // 找到有评分的维度
            }
          }
        }
      }
      return false; // 没有找到任何评分
    }
  },
  watch: {
    currentCaseId: {
      handler() {
        // 清除当前选择，让loadEvaluators方法重新选择默认的第一个
        this.selectedEvaluator = null;
        this.loadEvaluators();
        // 延迟检查排序状态，确保evaluators已加载
        this.$nextTick(() => {
          this.checkCaseSortingStatus();
        });
      },
      immediate: true
    },
    username: {
      handler(newUsername, oldUsername) {
        // 当用户改变时，清除之前的数据并重新加载
        console.log(`用户从 ${oldUsername} 切换到 ${newUsername}`);
        this.selectedEvaluator = null;
        this.evaluators = []; // 清除当前评估者列表
        this.loadEvaluators();
      },
      immediate: true
    },
    // 监听档位数据变化，强制更新布局
    availableEvaluators: {
      handler() {
        this.$nextTick(() => {
          this.forceLayoutUpdate();
        });
        // 通知父组件availableEvaluators数量发生变化
        this.$emit('available-evaluators-changed', this.availableEvaluators.length);
      },
      deep: true
    },
    goodTier: {
      handler() {
        this.$nextTick(() => {
          this.forceLayoutUpdate();
        });
      },
      deep: true
    },
    mediumTier: {
      handler() {
        this.$nextTick(() => {
          this.forceLayoutUpdate();
        });
      },
      deep: true
    },
    poorTier: {
      handler() {
        this.$nextTick(() => {
          this.forceLayoutUpdate();
        });
      },
      deep: true
    }
  },
     mounted() {
     this.loadEvaluators();
     this.checkCaseSortingStatus();
   },
   
   beforeUnmount() {
     // 清理所有事件监听和定时器
     this.stopAutoScroll();
     document.removeEventListener('dragover', this.handleGlobalDragOver);
   }
};
</script>

<style scoped>
.content {
  padding: clamp(3px, 0.4vw, 6px);
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: clamp(3px, 0.6vw, 8px);
  box-sizing: border-box;
  background-color: #e3f2fd; /* 柔和的蓝色背景 */
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: clamp(40px, 5vh, 70px);
  color: #666;
  font-size: clamp(5px, 0.5vw, 7px);
}

.evaluators-grid {
  display: flex;
  flex-direction: column;
  gap: clamp(2px, 0.4vw, 5px);
  flex: 1;
  height: 100%;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: clamp(2px, 0.25vw, 4px);
}

.evaluator-item {
  display: flex;
  flex-direction: column;
  gap: clamp(1px, 0.25vw, 3px);
  padding: clamp(2px, 0.35vw, 4px);
  background: white;
  border: clamp(1px, 0.1vw, 1px) solid #dee2e6;
  border-radius: clamp(1px, 0.25vw, 3px);
  transition: all 0.3s ease;
  justify-content: center;
  align-items: center;
  min-height: clamp(18px, 2.5vh, 25px);
  cursor: grab;
  position: relative;
  flex-shrink: 0;
  user-select: none;
  margin-bottom: clamp(1px, 0.15vw, 2px);
  box-sizing: border-box;
}

.evaluator-item:active {
  cursor: grabbing;
}

.evaluator-item:hover {
  border-color: #2196f3;
  background: #e3f2fd;
  transform: translateY(-0.5px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.evaluator-item.selected {
  border-color: #2196f3;
  background: #e3f2fd;
  box-shadow: 0 1px 4px rgba(33, 150, 243, 0.3);
  transform: scale(1.01);
}

.evaluator-item.dragging {
  opacity: 0.5;
  transform: rotate(5deg);
}

.evaluator-item.drag-over {
  border-color: #4caf50 !important;
  background: #e8f5e8 !important;
  transform: scale(1.01);
  box-shadow: 0 2px 5px rgba(76, 175, 80, 0.3);
}

.evaluator-item.drag-over::before {
  content: '';
  position: absolute;
  top: -0.5px;
  left: -0.5px;
  right: -0.5px;
  bottom: -0.5px;
  border: 0.5px solid #4caf50;
  border-radius: clamp(1px, 0.25vw, 3px);
  pointer-events: none;
  z-index: 1;
}

.evaluator-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(0px, 0.05vw, 1px);
  width: 100%;
}

.evaluator-image-container {
  flex-shrink: 0;
}

.evaluator-image {
  width: clamp(10px, 1.2vw, 20px);
  height: clamp(10px, 1.2vw, 20px);
  border-radius: 50%;
  object-fit: cover;
  border: clamp(1px, 0.05vw, 1px) solid #e9ecef;
  transition: transform 0.3s ease;
}

.evaluator-image:hover {
  transform: scale(1.05);
}



.rank-indicator {
  position: absolute;
  top: clamp(1px, 0.21vw, 3px);
  right: clamp(1px, 0.21vw, 3px);
  background: #2196f3;
  color: white;
  border-radius: 50%;
  width: clamp(8px, 0.98vw, 11px);
  height: clamp(8px, 0.98vw, 11px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: clamp(4px, 0.35vw, 5px);
  font-weight: bold;
}

.player-name {
  font-size: clamp(8px, 0.49vw, 8px);
  font-weight: 500;
  color: #333;
  text-align: center;
  margin-top: clamp(1px, 0.21vw, 3px);
}



/* 响应式断点 */
@media (max-width: 1200px) {
  .evaluator-image {
    width: clamp(22px, 3.5vw, 46px);
    height: clamp(22px, 3.5vw, 46px);
  }
}

@media (max-width: 768px) {
  .instruction-box {
    flex-direction: column;
    gap: clamp(3px, 0.56vw, 6px);
  }
  
  .instruction-content {
    gap: clamp(1px, 0.14vw, 1px);
  }
  
  .instruction-text {
    font-size: clamp(7px, 0.7vw, 10px);
  }
}

@media (max-width: 768px) {
  .content {
    padding: clamp(4px, 0.56vw, 8px);
    gap: clamp(4px, 0.7vw, 10px);
  }
  
  .split-layout {
    flex-direction: column;
    gap: clamp(6px, 0.84vw, 11px);
  }
  
  .left-panel {
    min-height: clamp(105px, 17.5vh, 175px);
  }
  
  .right-panel {
    gap: clamp(4px, 0.7vw, 8px);
    min-height: clamp(105px, 17.5vh, 175px);
  }
  
  .panel-header {
    padding: clamp(4px, 0.7vw, 8px) clamp(7px, 0.84vw, 11px);
    font-size: clamp(7px, 0.7vw, 10px);
  }
  
  .evaluators-list {
    padding: clamp(4px, 0.7vw, 8px);
    gap: clamp(2px, 0.42vw, 4px);
    min-height: clamp(21px, 3.5vh, 42px);
  }
  
  .tier-section {
    min-height: clamp(35px, 5.6vh, 56px);
  }
  
  .tier-header {
    padding: clamp(3px, 0.56vw, 7px) clamp(6px, 0.84vw, 10px);
    font-size: clamp(7px, 0.7vw, 10px);
  }
  
  .tier-content {
    padding: clamp(3px, 0.56vw, 7px);
    gap: clamp(2px, 0.42vw, 4px);
    min-height: clamp(21px, 3.5vh, 42px);
  }
  
  .evaluator-item {
    padding: clamp(3px, 0.56vw, 6px);
    gap: clamp(2px, 0.42vw, 6px);
    min-height: clamp(25px, 2.8vh, 35px);
  }
  
  .evaluator-image {
    width: clamp(18px, 2.45vw, 32px);
    height: clamp(18px, 2.45vw, 32px);
  }
}

@media (max-height: 600px) {
  .split-layout {
    gap: clamp(4px, 0.7vw, 8px);
  }
  
  .left-panel {
    min-height: clamp(84px, 14vh, 140px);
  }
  
  .right-panel {
    min-height: clamp(84px, 14vh, 140px);
  }
  
  .panel-header {
    padding: clamp(3px, 0.56vw, 7px) clamp(6px, 0.7vw, 10px);
    font-size: clamp(6px, 0.63vw, 9px);
  }
  
  .evaluators-list {
    padding: clamp(3px, 0.56vw, 7px);
    gap: clamp(1px, 0.28vw, 4px);
  }
  
  .right-panel {
    gap: clamp(3px, 0.56vw, 7px);
  }
  
  .tier-section {
    min-height: clamp(28px, 4.2vh, 42px);
  }
  
  .tier-header {
    padding: clamp(2px, 0.42vw, 6px) clamp(4px, 0.7vw, 8px);
    font-size: clamp(6px, 0.63vw, 9px);
  }
  
  .tier-content {
    padding: clamp(2px, 0.42vw, 6px);
    gap: clamp(1px, 0.28vw, 4px);
    min-height: clamp(18px, 2.8vh, 28px);
  }
  
  .evaluator-item {
    padding: clamp(2px, 0.42vw, 6px);
    gap: clamp(1px, 0.28vw, 4px);
    min-height: clamp(21px, 2.1vh, 32px);
  }
  
  .evaluator-image {
    width: clamp(14px, 1.75vw, 25px);
    height: clamp(14px, 1.75vw, 25px);
  }
}

/* 保存成功提示弹窗样式 */
.save-notification {
  position: fixed;
  top: 14px;
  right: 14px;
  z-index: 1000;
}

.notification-content {
  background: #4caf50;
  color: white;
  padding: clamp(6px, 0.84vw, 11px) clamp(8px, 1.26vw, 17px);
  border-radius: clamp(3px, 0.42vw, 6px);
  box-shadow: 0 3px 8px rgba(76, 175, 80, 0.3);
  display: flex;
  align-items: center;
  gap: clamp(4px, 0.7vw, 8px);
  font-size: clamp(8px, 0.84vw, 11px);
  font-weight: 500;
  min-width: clamp(84px, 10.5vw, 140px);
}

.notification-icon {
  font-size: clamp(10px, 0.98vw, 13px);
  font-weight: bold;
}

.notification-text {
  flex: 1;
  text-align: center;
}

/* Vue transition 动画 */
.notification-enter-active {
  transition: all 0.3s ease-out;
}

.notification-leave-active {
  transition: all 0.3s ease-in;
}

.notification-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.notification-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* 醒目的提示框样式 */
.instruction-box {
  background-color: #fff3e0; /* 柔和的橙色背景 */
  border: 1px solid #ffcc80;
  border-radius: clamp(3px, 0.42vw, 6px);
  padding: clamp(6px, 0.7vw, 8px) clamp(8px, 1.05vw, 13px);
  display: flex;
  align-items: center;
  gap: clamp(4px, 0.7vw, 8px);
  margin-top: clamp(4px, 0.7vw, 10px);
  box-shadow: 0 1px 6px rgba(255, 204, 128, 0.3);
}

.instruction-icon {
  font-size: clamp(13px, 1.4vw, 17px);
  color: #ff9800; /* 橙色图标 */
}

.instruction-content {
  display: flex;
  flex-direction: column;
  gap: clamp(1px, 0.21vw, 3px);
}

.instruction-text {
  font-size: clamp(8px, 0.84vw, 11px);
  font-weight: 900;
  color: #333;
  text-align: left;
}

/* 自定义滚动条样式 */
.evaluators-grid::-webkit-scrollbar {
  width: clamp(4px, 0.56vw, 7px);
}

.evaluators-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: clamp(2px, 0.28vw, 4px);
}

.evaluators-grid::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: clamp(2px, 0.28vw, 4px);
  transition: background 0.3s ease;
}

.evaluators-grid::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Firefox 滚动条样式 */
.evaluators-grid {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

/* 整个布局的滚动条样式 */
.split-layout::-webkit-scrollbar {
  width: clamp(4px, 0.56vw, 7px);
}

.split-layout::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: clamp(2px, 0.28vw, 4px);
}

.split-layout::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: clamp(2px, 0.28vw, 4px);
  transition: background 0.3s ease;
}

.split-layout::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.split-layout {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

/* 左右分栏布局样式 */
.split-layout {
  display: flex;
  gap: clamp(2px, 0.3vw, 4px);
  flex: 1;
  height: 100%;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: clamp(3px, 0.35vw, 6px);
  scroll-behavior: smooth;
  align-items: flex-start;
}

/* 左侧面板样式 */
.left-panel {
  flex: 1.5;
  display: flex;
  flex-direction: column;
  border: clamp(1px, 0.14vw, 2px) solid #dee2e6;
  border-radius: clamp(3px, 0.42vw, 6px);
  background: #f8f9fa;
  min-height: clamp(140px, 17.5vh, 210px);
  transition: all 0.3s ease;
  position: relative;
  flex-shrink: 0;
  height: fit-content;
}

.left-panel.drag-over {
  border-color: #4caf50 !important;
  background: #e8f5e8 !important;
  transform: scale(1.02);
  box-shadow: 0 3px 8px rgba(76, 175, 80, 0.3);
}

.left-panel.drag-over::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  border: 1px solid #4caf50;
  border-radius: clamp(3px, 0.42vw, 6px);
  pointer-events: none;
  z-index: 1;
}

/* 右侧面板样式 */
.right-panel {
  flex: 1.5;
  display: flex;
  flex-direction: column;
  gap: clamp(6px, 0.84vw, 11px);
  min-height: clamp(140px, 17.5vh, 210px);
  transition: all 0.3s ease;
  flex-shrink: 0;
  height: fit-content;
}

/* 面板头部样式 */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: clamp(6px, 0.84vw, 11px) clamp(8px, 1.05vw, 14px);
  background: linear-gradient(135deg, #2196f3, #42a5f5);
  color: white;
  border-bottom: clamp(1px, 0.14vw, 1px) solid #dee2e6;
  border-radius: clamp(3px, 0.42vw, 6px) clamp(3px, 0.42vw, 6px) 0 0;
  font-weight: bold;
  font-size: clamp(8px, 0.84vw, 11px);
}

.panel-title {
  font-weight: bold;
}

.panel-count {
  font-size: clamp(7px, 0.7vw, 10px);
  opacity: 0.9;
}

/* 作答者列表样式 */
.evaluators-list {
  display: flex;
  flex-direction: column;
  gap: clamp(3px, 0.56vw, 6px);
  padding: clamp(6px, 0.84vw, 11px);
  min-height: clamp(28px, 4.2vh, 56px);
  flex-shrink: 0;
  height: fit-content;
}

/* 作答者列表的滚动条样式 */
.evaluators-list::-webkit-scrollbar {
  width: clamp(3px, 0.42vw, 6px);
}

.evaluators-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: clamp(1px, 0.21vw, 3px);
}

.evaluators-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: clamp(1px, 0.21vw, 3px);
  transition: background 0.3s ease;
}

.evaluators-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.evaluators-list {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

/* 档位区域样式 */
.tier-section {
  display: flex;
  flex-direction: column;
  border: clamp(1px, 0.14vw, 2px) solid #dee2e6;
  border-radius: clamp(3px, 0.42vw, 6px);
  background: #f8f9fa;
  transition: all 0.3s ease;
  min-height: clamp(35px, 4.5vh, 60px);
  position: relative;
  flex-shrink: 0;
  height: fit-content;
}

.tier-section.drag-over {
  border-color: #4caf50 !important;
  background: #e8f5e8 !important;
  transform: scale(1.02);
  box-shadow: 0 3px 8px rgba(76, 175, 80, 0.3);
}

.tier-section.drag-over::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  border: 1px solid #4caf50;
  border-radius: clamp(3px, 0.42vw, 6px);
  pointer-events: none;
  z-index: 1;
}

/* 档位头部样式 */
.tier-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: clamp(3px, 0.5vw, 6px) clamp(6px, 0.9vw, 9px);
  border-bottom: clamp(1px, 0.14vw, 1px) solid #dee2e6;
  font-weight: bold;
  font-size: clamp(7px, 0.7vw, 10px);
}

.good-tier {
  background: linear-gradient(135deg, #4caf50, #66bb6a);
  color: white;
}

.medium-tier {
  background: linear-gradient(135deg, #ff9800, #ffb74d);
  color: white;
}

.poor-tier {
  background: linear-gradient(135deg, #f44336, #ef5350);
  color: white;
}

.tier-title {
  font-weight: bold;
}

.tier-count {
  font-size: clamp(6px, 0.6vw, 8px);
  opacity: 0.9;
}

/* 档位内容区域样式 */
.tier-content {
  display: flex;
  flex-direction: column;
  gap: clamp(2px, 0.4vw, 5px);
  padding: clamp(3px, 0.5vw, 6px);
  min-height: clamp(22px, 3vh, 45px);
  position: relative;
  flex-shrink: 0;
  height: fit-content;
}

/* 档位内容区域的滚动条样式 */
.tier-content::-webkit-scrollbar {
  width: clamp(3px, 0.42vw, 6px);
}

.tier-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: clamp(1px, 0.21vw, 3px);
}

.tier-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: clamp(1px, 0.21vw, 3px);
  transition: background 0.3s ease;
}

.tier-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.tier-content {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

/* 右侧排序说明容器样式 */
.sorting-instruction-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(8px, 1.2vw, 12px) clamp(3px, 0.4vw, 5px);
  background: linear-gradient(135deg, #333, #555);
  color: white;
  border-radius: clamp(3px, 0.42vw, 6px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  font-size: clamp(7px, 0.8vw, 10px);
  font-weight: bold;
  width: clamp(20px, 2.5vw, 30px);
  min-width: clamp(20px, 2.5vw, 30px);
  max-width: clamp(20px, 2.5vw, 30px);
  text-align: center;
  white-space: nowrap;
  flex-shrink: 0;
  height: fit-content;
  align-self: flex-start;
  margin-top: clamp(6px, 0.84vw, 11px);
}

.instruction-text-vertical {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  text-align: center;
  line-height: 1.2;
  padding: clamp(2px, 0.3vw, 4px) 0;
  letter-spacing: clamp(0.5px, 0.05vw, 1px);
}
</style>