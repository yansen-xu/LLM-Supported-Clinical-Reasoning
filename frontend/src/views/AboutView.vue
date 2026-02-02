<template>
  <div class="about-view">
    <h2>About This Project</h2>
    
    <div class="tech-stack">
      <h3>Technology Stack</h3>
      <div class="stack-grid">
        <div class="stack-item">
          <div class="stack-icon">🟢</div>
          <h4>Vue.js</h4>
          <p>Progressive JavaScript framework for building user interfaces</p>
        </div>
        
        <div class="stack-item">
          <div class="stack-icon">🐍</div>
          <h4>Python</h4>
          <p>Powerful programming language for backend development</p>
        </div>
        
        <div class="stack-item">
          <div class="stack-icon">🌶️</div>
          <h4>Flask</h4>
          <p>Lightweight Python web framework for building APIs</p>
        </div>
        
        <div class="stack-item">
          <div class="stack-icon">🔀</div>
          <h4>Axios</h4>
          <p>Promise-based HTTP client for making API requests</p>
        </div>
      </div>
    </div>
    
    <div class="project-structure">
      <h3>Project Structure</h3>
      <pre class="structure-code">
vue-flask-project/
├── frontend/          # Vue 3 frontend
│   ├── public/        # Static assets
│   ├── src/           # Application source
│   │   ├── assets/    # Images, fonts
│   │   ├── components/# Vue components
│   │   ├── router/    # Vue Router
│   │   ├── store/     # Vuex store
│   │   ├── views/     # Page components
│   │   ├── App.vue    # Root component
│   │   └── main.js    # Entry point
│   ├── .env           # Environment variables
│   └── package.json   # Dependencies
│
├── backend/           # Flask backend
│   ├── app/           # Application package
│   │   ├── __init__.py# App factory
│   │   ├── routes.py  # API routes
│   │   └── models.py  # Data models
│   ├── venv/          # Python virtual environment
│   ├── .env           # Environment variables
│   ├── config.py      # Configuration
│   └── run.py         # Entry point
│
├── .gitignore         # Git ignore rules
└── README.md          # Project documentation</pre>
    </div>
    
    <div class="setup-instructions">
      <h3>Setup Instructions</h3>
      <ol>
        <li>Clone the repository: <code>git clone https://github.com/your/repo.git</code></li>
        <li>
          <strong>Frontend Setup:</strong>
          <ul>
            <li>Navigate to <code>frontend</code> directory</li>
            <li>Install dependencies: <code>npm install</code></li>
            <li>Start development server: <code>npm run serve</code></li>
          </ul>
        </li>
        <li>
          <strong>Backend Setup:</strong>
          <ul>
            <li>Navigate to <code>backend</code> directory</li>
            <li>Create virtual environment: <code>python -m venv venv</code></li>
            <li>Activate venv: 
              <ul>
                <li>Windows: <code>venv\Scripts\activate</code></li>
                <li>Unix/macOS: <code>source venv/bin/activate</code></li>
              </ul>
            </li>
            <li>Install dependencies: <code>pip install -r requirements.txt</code></li>
            <li>Start Flask server: <code>flask run</code></li>
          </ul>
        </li>
      </ol>
    </div>
  </div>
</template>

<style lang="css" scoped>
.about-view {
  max-width: 1000px;
  margin: 0 auto;
  
  h2 {
    color: #1976d2;
    text-align: center;
    margin-bottom: 2rem;
  }
  
  .tech-stack {
    margin-bottom: 2rem;
    
    h3 {
      color: #1565c0;
      border-bottom: 2px solid #e3f2fd;
      padding-bottom: 0.5rem;
    }
    
    .stack-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1.5rem;
      margin-top: 1rem;
      
      .stack-item {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        
        .stack-icon {
          font-size: 2.5rem;
          margin-bottom: 1rem;
        }
        
        h4 {
          margin-top: 0;
          color: #1976d2;
        }
        
        p {
          color: #455a64;
          line-height: 1.5;
        }
      }
    }
  }
  
  .project-structure {
    margin-bottom: 2rem;
    
    h3 {
      color: #1565c0;
      border-bottom: 2px solid #e3f2fd;
      padding-bottom: 0.5rem;
    }
    
    .structure-code {
      background: #2d2d2d;
      color: #f8f8f2;
      padding: 1.5rem;
      border-radius: 8px;
      overflow-x: auto;
      font-family: 'Fira Code', 'Consolas', monospace;
      line-height: 1.5;
      margin-top: 1rem;
    }
  }
  
  .setup-instructions {
    background: #e3f2fd;
    padding: 1.5rem;
    border-radius: 8px;
    
    h3 {
      color: #1565c0;
      margin-top: 0;
    }
    
    ol, ul {
      padding-left: 1.5rem;
    }
    
    li {
      margin-bottom: 0.8rem;
      line-height: 1.6;
    }
    
    code {
      background: rgba(0, 0, 0, 0.05);
      padding: 0.2rem 0.4rem;
      border-radius: 4px;
      font-family: monospace;
    }
    
    strong {
      color: #1976d2;
    }
  }
}
</style>