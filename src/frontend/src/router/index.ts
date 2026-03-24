import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
  },
  {
    path: '/roles',
    name: 'RoleList',
    component: () => import('@/views/RoleList.vue'),
  },
  {
    path: '/roles/create',
    name: 'RoleCreate',
    component: () => import('@/views/RoleEditor.vue'),
  },
  {
    path: '/roles/:id',
    name: 'RoleEdit',
    component: () => import('@/views/RoleEditor.vue'),
  },
  {
    path: '/sessions',
    name: 'SessionList',
    component: () => import('@/views/SessionList.vue'),
  },
  {
    path: '/sessions/create',
    name: 'SessionCreate',
    component: () => import('@/views/SessionCreate.vue'),
  },
  {
    path: '/sessions/:id',
    name: 'ChatRoom',
    component: () => import('@/views/ChatRoom.vue'),
  },
  {
    path: '/rules',
    name: 'RuleList',
    component: () => import('@/views/RuleList.vue'),
  },
  {
    path: '/rules/create',
    name: 'RuleCreate',
    component: () => import('@/views/RuleEditor.vue'),
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue'),
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
