<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
import { useUIStore } from '@/stores'

const route = useRoute()
const uiStore = useUIStore()

const menuItems = [
  { path: '/', name: '首页', icon: '🏠' },
  { path: '/sessions', name: '会话', icon: '💬' },
  { path: '/roles', name: '角色', icon: '🎭' },
  { path: '/rules', name: '规则', icon: '📋' },
  { path: '/history', name: '历史', icon: '📜' },
  { path: '/settings', name: '设置', icon: '⚙️' },
]
</script>

<template>
  <aside :class="['app-sidebar', { collapsed: uiStore.sidebarCollapsed }]">
    <nav class="sidebar-nav">
      <RouterLink
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        :class="['nav-item', { active: route.path === item.path || (item.path !== '/' && route.path.startsWith(item.path)) }]"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-label">{{ item.name }}</span>
      </RouterLink>
    </nav>
  </aside>
</template>

<style scoped>
.app-sidebar {
  width: 200px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  transition: width 0.3s;
  overflow: hidden;
}

.app-sidebar.collapsed {
  width: 60px;
}

.sidebar-nav {
  padding: 15px 10px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 15px;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-primary);
  transition: background 0.2s;
}

.nav-item:hover {
  background: var(--bg-hover);
}

.nav-item.active {
  background: var(--primary-color);
  color: white;
}

.nav-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
}

.collapsed .nav-label {
  display: none;
}
</style>
