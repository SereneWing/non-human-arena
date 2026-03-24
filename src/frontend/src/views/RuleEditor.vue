<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = ref({
  name: '',
  type: 'debate',
  description: '',
  constraints: [] as any[],
  triggers: [] as any[],
  consequences: [] as any[],
})
</script>

<template>
  <div class="rule-editor">
    <header class="page-header">
      <h1>创建规则</h1>
    </header>
    
    <form @submit.prevent class="editor-form">
      <div class="form-group">
        <label for="name">规则名称</label>
        <input id="name" v-model="form.name" type="text" required />
      </div>
      
      <div class="form-group">
        <label for="type">规则类型</label>
        <select id="type" v-model="form.type">
          <option value="debate">辩论</option>
          <option value="game">游戏</option>
          <option value="negotiation">谈判</option>
          <option value="teaching">教学</option>
          <option value="roleplay">角色扮演</option>
          <option value="custom">自定义</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="description">描述</label>
        <textarea id="description" v-model="form.description" rows="3"></textarea>
      </div>
      
      <div class="form-actions">
        <button type="submit" class="btn btn-primary">保存</button>
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
