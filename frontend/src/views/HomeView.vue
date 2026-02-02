<template>
  <div class="home-view">
    <div class="hero">
      <h2>Vue + Flask Integration</h2>
      <p>Full-stack development with modern frontend and Python backend</p>
    </div>
    
    <div class="features">
      <div class="feature-card">
        <div class="icon">🚀</div>
        <h3>Fast Development</h3>
        <p>Vue's reactivity system and Flask's simplicity enable rapid development cycles.</p>
      </div>
      
      <div class="feature-card">
        <div class="icon">🔧</div>
        <h3>Easy Integration</h3>
        <p>Simple API communication between frontend and backend with Axios.</p>
      </div>
      
      <div class="feature-card">
        <div class="icon">⚙️</div>
        <h3>Scalable</h3>
        <p>Flask's blueprint system and Vue's component architecture support large applications.</p>
      </div>
    </div>
    
    <div class="api-demo">
      <h3>Backend API Demo</h3>
      
      <div class="demo-section">
        <button @click="checkHealth" class="demo-btn">Check Backend Health</button>
        <div v-if="healthStatus" class="response">
          <pre>{{ healthStatus }}</pre>
        </div>
      </div>
      
      <div class="demo-section">
        <div class="input-group">
          <input 
            v-model="message" 
            placeholder="Enter a message" 
            class="message-input"
          >
          <button @click="processMessage" class="demo-btn">Process Message</button>
        </div>
        <div v-if="processedMessage" class="response">
          <pre>{{ processedMessage }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'HomeView',
  data() {
    return {
      healthStatus: null,
      message: '',
      processedMessage: null,
      apiBaseUrl: process.env.VUE_APP_API_URL || 'http://localhost:5000'
    };
  },
  methods: {
    async checkHealth() {
      try {
        const response = await axios.get(`${this.apiBaseUrl}/api/health`);
        this.healthStatus = response.data;
      } catch (error) {
        this.healthStatus = { error: 'Backend not available' };
      }
    },
    async processMessage() {
      if (!this.message.trim()) return;
      
      try {
        const response = await axios.post(`${this.apiBaseUrl}/api/message`, {
          message: this.message
        });
        this.processedMessage = response.data;
      } catch (error) {
        this.processedMessage = { error: 'Failed to process message' };
      }
    }
  }
}
</script>

<style lang="css" scoped>
.home-view {
  .hero {
    text-align: center;
    padding: 2rem 1rem;
    background: linear-gradient(120deg, #e0f7fa, #bbdefb);
    border-radius: 10px;
    margin-bottom: 2rem;
    
    h2 {
      color: #1565c0;
      margin-bottom: 1rem;
    }
    
    p {
      font-size: 1.2rem;
      color: #37474f;
      max-width: 600px;
      margin: 0 auto;
    }
  }
  
  .features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
    
    .feature-card {
      background: white;
      border-radius: 8px;
      padding: 1.5rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      transition: transform 0.3s;
      
      &:hover {
        transform: translateY(-5px);
      }
      
      .icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
      }
      
      h3 {
        color: #1976d2;
        margin-top: 0;
      }
      
      p {
        color: #455a64;
        line-height: 1.6;
      }
    }
  }
  
  .api-demo {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    
    h3 {
      color: #1976d2;
      margin-top: 0;
      border-bottom: 2px solid #e3f2fd;
      padding-bottom: 0.5rem;
    }
    
    .demo-section {
      margin-bottom: 1.5rem;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    .demo-btn {
      background: #1976d2;
      color: white;
      border: none;
      padding: 0.7rem 1.5rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 1rem;
      transition: background 0.3s;
      margin-right: 1rem;
      
      &:hover {
        background: #1565c0;
      }
    }
    
    .input-group {
      display: flex;
      margin-bottom: 1rem;
      
      .message-input {
        flex: 1;
        padding: 0.7rem;
        border: 1px solid #90caf9;
        border-radius: 4px;
        font-size: 1rem;
        margin-right: 1rem;
        
        &:focus {
          outline: none;
          border-color: #1976d2;
          box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
        }
      }
    }
    
    .response {
      background: #f5f5f5;
      border: 1px solid #e0e0e0;
      border-radius: 4px;
      padding: 1rem;
      margin-top: 1rem;
      overflow-x: auto;
      
      pre {
        margin: 0;
        font-family: monospace;
        white-space: pre-wrap;
      }
    }
  }
}
</style>