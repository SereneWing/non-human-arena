<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useSessionStore } from '@/stores'

const sessionStore = useSessionStore()

onMounted(() => {
  sessionStore.fetchSessions()
})

function getStateClass(state: string) {
  const stateMap: Record<string, string> = {
    running: 'state-running',
    paused: 'state-paused',
    completed: 'state-completed',
    created: 'state-created',
  }
  return stateMap[state] || ''
}
</script>

<template>
  <div class="session-list">
    <header class="page-header">
      <h1>会话列表</h1>
      <RouterLink to="/sessions/create" class="btn btn-primary">创建会话</RouterLink>
    </header>
    
    <div v-if="sessionStore.loading" class="loading">加载中...</div>
    
    <div v-else-if="sessionStore.sessions.length === 0" class="empty-state">
      <p>暂无会话</p>
      <RouterLink to="/sessions/create" class="btn btn-primary">创建第一个会话</RouterLink>
    </div>
    
    <div v-else class="session-grid">
      <div v-for="session in sessionStore.sessions" :key="session.id" class="session-card">
        <div class="session-header">
          <h3>{{ session.name }}</h3>
          <span :class="['session-state', getStateClass(session.state)]">{{ session.state }}</span>
        </div>
        <p class="session-topic">{{ session.topic || '无主题' }}</p>
        <div class="session-meta">
          <span>角色数: {{ session.role_ids.length }}</span>
          <span>{{ new Date(session.created_at).toLocaleDateString() }}</span>
        </div>
        <div class="session-actions">
          <RouterLink :to="`/sessions/${session.id}`" class="btn btn-small">进入</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.session-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.session-card {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: 12px;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.session-header h3 {
  margin: 0;
}

.session-state {
  font-size: 0.8rem;
  padding: 4px 10px;
  border-radius: 12px;
  text-transform: uppercase;
}

.state-running { background: #4caf50; color: white; }
.state-paused { background: #ff9800; color: white; }
.state-completed { background: #9e9e9e; color: white; }
.state-created { background: #2196f3; color: white; }

.session-topic {
  color: var(--text-secondary);
  margin: 10px 0;
}

.session-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 15px 0;
}

.session-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-small {
  padding: 6px 12px;
  font-size: 0.9rem;
  background: var(--primary-color);
  color: white;
}

.loading, .empty-state {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}
</style>
