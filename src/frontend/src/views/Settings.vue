<script setup lang="ts">
import { ref } from 'vue'
import { useUIStore } from '@/stores'

const uiStore = useUIStore()

const settings = ref({
  theme: 'light',
  apiUrl: '/api/v1',
  wsUrl: '',
  language: 'zh-CN',
})
</script>

<template>
  <div class="settings">
    <header class="page-header">
      <h1>设置</h1>
    </header>
    
    <div class="settings-form">
      <div class="form-group">
        <label>主题</label>
        <div class="theme-options">
          <button
            :class="['theme-btn', { active: settings.theme === 'light' }]"
            @click="settings.theme = 'light'; uiStore.setTheme('light')"
          >
            🌞 浅色
          </button>
          <button
            :class="['theme-btn', { active: settings.theme === 'dark' }]"
            @click="settings.theme = 'dark'; uiStore.setTheme('dark')"
          >
            🌙 深色
          </button>
        </div>
      </div>
      
      <div class="form-group">
        <label for="apiUrl">API 地址</label>
        <input id="apiUrl" v-model="settings.apiUrl" type="text" />
      </div>
      
      <div class="form-group">
        <label for="language">语言</label>
        <select id="language" v-model="settings.language">
          <option value="zh-CN">简体中文</option>
          <option value="en-US">English</option>
        </select>
      </div>
      
      <div class="form-actions">
        <button class="btn btn-primary">保存设置</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 30px;
}

.settings-form {
  max-width: 500px;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-color);
  color: var(--text-primary);
}

.theme-options {
  display: flex;
  gap: 10px;
}

.theme-btn {
  flex: 1;
  padding: 15px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-color);
  cursor: pointer;
  transition: all 0.2s;
}

.theme-btn.active {
  border-color: var(--primary-color);
  background: rgba(33, 150, 243, 0.1);
}

.form-actions {
  margin-top: 30px;
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
</style>
