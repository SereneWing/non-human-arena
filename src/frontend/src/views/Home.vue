<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="home">
    <header class="hero">
      <h1>非人竞技场</h1>
      <p class="subtitle">AI驱动的多智能体辩论与讨论平台</p>
      <div class="cta-buttons">
        <RouterLink to="/sessions/create" class="btn btn-primary">开始讨论</RouterLink>
        <RouterLink to="/roles" class="btn btn-secondary">管理角色</RouterLink>
      </div>
    </header>
    
    <section class="features">
      <h2>核心功能</h2>
      <div class="feature-grid">
        <div class="feature-card">
          <h3>🎭 多智能体系统</h3>
          <p>创建具有独特个性的人工智能角色</p>
        </div>
        <div class="feature-card">
          <h3>📋 规则引擎</h3>
          <p>自定义辩论规则和触发条件</p>
        </div>
        <div class="feature-card">
          <h3>🧠 心理活动</h3>
          <p>AI生成内心独白影响决策</p>
        </div>
        <div class="feature-card">
          <h3>💓 心跳机制</h3>
          <p>AI空闲时主动思考发言</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 60px 20px;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.5rem;
  color: var(--text-secondary);
  margin-bottom: 30px;
}

.cta-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.btn {
  padding: 12px 30px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-secondary {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
}

.features {
  padding: 40px 20px;
}

.features h2 {
  text-align: center;
  margin-bottom: 30px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.feature-card {
  background: var(--bg-secondary);
  padding: 25px;
  border-radius: 12px;
}

.feature-card h3 {
  margin-bottom: 10px;
}
</style>
