<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useRoleStore } from '@/stores'

const roleStore = useRoleStore()

onMounted(() => {
  roleStore.fetchRoles()
})
</script>

<template>
  <div class="role-list">
    <header class="page-header">
      <h1>角色管理</h1>
      <RouterLink to="/roles/create" class="btn btn-primary">创建角色</RouterLink>
    </header>
    
    <div v-if="roleStore.loading" class="loading">加载中...</div>
    
    <div v-else-if="roleStore.roles.length === 0" class="empty-state">
      <p>暂无角色</p>
      <RouterLink to="/roles/create" class="btn btn-primary">创建第一个角色</RouterLink>
    </div>
    
    <div v-else class="role-grid">
      <div v-for="role in roleStore.roles" :key="role.id" class="role-card">
        <div class="role-avatar">
          {{ role.name.charAt(0) }}
        </div>
        <div class="role-info">
          <h3>{{ role.name }}</h3>
          <span class="role-category">{{ role.category }}</span>
          <p v-if="role.description">{{ role.description }}</p>
        </div>
        <div class="role-actions">
          <RouterLink :to="`/roles/${role.id}`" class="btn btn-small">编辑</RouterLink>
          <RouterLink :to="`/sessions/create?role_id=${role.id}`" class="btn btn-small btn-secondary">开始讨论</RouterLink>
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

.btn {
  padding: 10px 20px;
  border-radius: 6px;
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

.btn-small {
  padding: 6px 12px;
  font-size: 0.9rem;
}

.role-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.role-card {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.role-avatar {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
}

.role-info h3 {
  margin: 0 0 5px 0;
}

.role-category {
  font-size: 0.85rem;
  color: var(--text-secondary);
  text-transform: capitalize;
}

.role-info p {
  margin: 10px 0 0 0;
  color: var(--text-secondary);
}

.role-actions {
  display: flex;
  gap: 10px;
  margin-top: auto;
}

.loading, .empty-state {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}
</style>
