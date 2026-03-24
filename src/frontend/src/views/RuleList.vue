<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const rules = ref([
  { id: '1', name: '自由辩论', type: 'debate', description: '无限制自由辩论规则', enabled: true },
  { id: '2', name: '正式辩论', type: 'debate', description: '有顺序和时间限制的正式辩论', enabled: true },
])
</script>

<template>
  <div class="rule-list">
    <header class="page-header">
      <h1>规则管理</h1>
      <RouterLink to="/rules/create" class="btn btn-primary">创建规则</RouterLink>
    </header>
    
    <div class="rule-grid">
      <div v-for="rule in rules" :key="rule.id" class="rule-card">
        <div class="rule-header">
          <h3>{{ rule.name }}</h3>
          <span :class="['rule-status', { enabled: rule.enabled }]">
            {{ rule.enabled ? '启用' : '禁用' }}
          </span>
        </div>
        <p>{{ rule.description }}</p>
        <div class="rule-actions">
          <button class="btn btn-small">编辑</button>
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

.rule-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.rule-card {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: 12px;
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rule-header h3 {
  margin: 0;
}

.rule-status {
  font-size: 0.8rem;
  padding: 4px 10px;
  border-radius: 12px;
  background: #9e9e9e;
  color: white;
}

.rule-status.enabled {
  background: #4caf50;
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
  border: none;
  cursor: pointer;
}
</style>
