<template>
  <div class="thank-you-overlay">
    <div class="thank-you-content">
      <h1 class="thank-you-title">感谢参与</h1>
      <p class="thank-you-message">您已完成所有案例的评估，感谢您的参与！</p>
      <div class="thank-you-icon">🎉</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ThankYouPage"
};
</script>

<style scoped>
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
  margin-bottom: clamp(20px, 3vh, 32px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .thank-you-content {
    padding: clamp(30px, 4vh, 60px) clamp(20px, 2.5vw, 40px);
  }
}
</style>
