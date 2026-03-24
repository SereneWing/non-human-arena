<script setup lang="ts">
import { useUIStore } from '@/stores'

const uiStore = useUIStore()
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <button class="menu-btn" @click="uiStore.toggleSidebar">
        ☰
      </button>
      <div class="logo">
        <span class="logo-icon">🎭</span>
        <span class="logo-text">非人竞技场</span>
      </div>
    </div>
    <div class="header-right">
      <button class="theme-btn" @click="uiStore.setTheme(uiStore.theme === 'light' ? 'dark' : 'light')">
        {{ uiStore.theme === 'light' ? '🌙' : '🌞' }}
      </button>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  padding: 0 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.menu-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 5px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-size: 1.2rem;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.theme-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 5px 10px;
}
</style>
