<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSessionStore } from '@/stores'

const sessionStore = useSessionStore()
const sessions = ref<any[]>([])

onMounted(async () => {
  await sessionStore.fetchSessions()
  sessions.value = sessionStore.sessions.filter(s => s.state === 'completed')
})
</script>

<template>
  <div class="history">
    <header class="page-header">
      <h1>历史记录</h1>
    </header>
    
    <div v-if="sessions.length === 0" class="empty-state">
      <p>暂无历史记录</p>
    </div>
    
    <div v-else class="history-list">
      <div v-for="session in sessions" :key="session.id" class="history-item">
        <div class="history-header">
          <h3>{{ session.name }}</h3>
          <span class="history-date">{{ new Date(session.ended_at || session.created_at).toLocaleDateString() }}</span>
        </div>
        <p class="history-topic">{{ session.topic || '无主题' }}</p>
        <div class="history-actions">
          <button class="btn btn-small">查看详情</button>
          <button class="btn btn-small btn-secondary">导出</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 30px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.history-item {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: 12px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.history-header h3 {
  margin: 0;
}

.history-date {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.history-topic {
  color: var(--text-secondary);
  margin: 0 0 15px 0;
}

.history-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
}

.btn-small {
  padding: 6px 12px;
  font-size: 0.9rem;
  background: var(--primary-color);
  color: white;
  border: none;
  cursor: pointer;
}

.btn-secondary {
  background: var(--bg-color);
  color: var(--text-primary);
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}
</style>
