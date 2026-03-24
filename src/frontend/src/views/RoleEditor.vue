<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRoleStore } from '@/stores'

const route = useRoute()
const router = useRouter()
const roleStore = useRoleStore()

const isEdit = ref(false)
const form = ref({
  name: '',
  category: 'debater',
  description: '',
  system_prompt: '',
  speaking_style: {
    formality: 0.5,
    length_preference: 'medium',
    tone: 'neutral',
    vocabulary_level: 'normal',
    use_emoji: false,
    interruptions: false,
    pause_frequency: 0.3,
  },
})

onMounted(async () => {
  if (route.params.id) {
    isEdit.value = true
    await roleStore.fetchRole(route.params.id as string)
    if (roleStore.currentRole) {
      form.value = {
        name: roleStore.currentRole.name,
        category: roleStore.currentRole.category,
        description: roleStore.currentRole.description || '',
        system_prompt: roleStore.currentRole.system_prompt,
        speaking_style: roleStore.currentRole.speaking_style || form.value.speaking_style,
      }
    }
  }
})

async function handleSubmit() {
  try {
    if (isEdit.value && route.params.id) {
      await roleStore.updateRole(route.params.id as string, form.value)
    } else {
      await roleStore.createRole({
        ...form.value,
        base_personality: { openness: 0.7, conscientiousness: 0.6 },
        skills: [],
        parameters: {},
        variables: {},
      } as any)
    }
    router.push('/roles')
  } catch (error) {
    console.error('Failed to save role:', error)
  }
}
</script>

<template>
  <div class="role-editor">
    <header class="page-header">
      <h1>{{ isEdit ? '编辑角色' : '创建角色' }}</h1>
    </header>
    
    <form @submit.prevent="handleSubmit" class="editor-form">
      <div class="form-group">
        <label for="name">角色名称</label>
        <input id="name" v-model="form.name" type="text" required />
      </div>
      
      <div class="form-group">
        <label for="category">角色类别</label>
        <select id="category" v-model="form.category">
          <option value="debater">辩手</option>
          <option value="mediator">主持人</option>
          <option value="judge">裁判</option>
          <option value="player">玩家</option>
          <option value="teacher">教师</option>
          <option value="student">学生</option>
          <option value="custom">自定义</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="description">描述</label>
        <textarea id="description" v-model="form.description" rows="3"></textarea>
      </div>
      
      <div class="form-group">
        <label for="system_prompt">系统提示词</label>
        <textarea id="system_prompt" v-model="form.system_prompt" rows="6" required></textarea>
      </div>
      
      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="roleStore.loading">
          {{ roleStore.loading ? '保存中...' : '保存' }}
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

.editor-form {
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
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-color);
  color: var(--text-primary);
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
