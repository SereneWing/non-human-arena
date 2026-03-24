<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore, useRoleStore } from '@/stores'

const router = useRouter()
const sessionStore = useSessionStore()
const roleStore = useRoleStore()

const form = ref({
  name: '',
  topic: '',
  role_ids: [] as string[],
})

onMounted(() => {
  roleStore.fetchRoles()
})

async function handleSubmit() {
  try {
    const session = await sessionStore.createSession(form.value)
    router.push(`/sessions/${session.id}`)
  } catch (error) {
    console.error('Failed to create session:', error)
  }
}
</script>

<template>
  <div class="session-create">
    <header class="page-header">
      <h1>创建会话</h1>
    </header>
    
    <form @submit.prevent="handleSubmit" class="create-form">
      <div class="form-group">
        <label for="name">会话名称</label>
        <input id="name" v-model="form.name" type="text" required />
      </div>
      
      <div class="form-group">
        <label for="topic">讨论主题</label>
        <textarea id="topic" v-model="form.topic" rows="3" placeholder="输入讨论的主题..."></textarea>
      </div>
      
      <div class="form-group">
        <label>选择角色</label>
        <div class="role-selector">
          <div
            v-for="role in roleStore.roles"
            :key="role.id"
            :class="['role-option', { selected: form.role_ids.includes(role.id) }]"
            @click="form.role_ids.includes(role.id) ? form.role_ids = form.role_ids.filter(id => id !== role.id) : form.role_ids.push(role.id)"
          >
            <span class="role-name">{{ role.name }}</span>
            <span class="role-category">{{ role.category }}</span>
          </div>
        </div>
      </div>
      
      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="form.role_ids.length === 0">
          创建并开始
        </button>
        <button type="button" class="btn btn-secondary" @click="router.back()">取消</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 30px;
}

.create-form {
  max-width: 600px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-color);
  color: var(--text-primary);
}

.role-selector {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.role-option {
  padding: 15px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.role-option:hover {
  border-color: var(--primary-color);
}

.role-option.selected {
  border-color: var(--primary-color);
  background: rgba(33, 150, 243, 0.1);
}

.role-category {
  font-size: 0.85rem;
  color: var(--text-secondary);
  text-transform: capitalize;
}

.form-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
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
</style>
