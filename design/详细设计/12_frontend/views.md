# 前端视图层

## 一、路由定义

```typescript
// router/routes.ts
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/sessions',
    name: 'SessionList',
    component: () => import('@/views/SessionList.vue')
  },
  {
    path: '/sessions/:id',
    name: 'SessionDetail',
    component: () => import('@/views/SessionDetail.vue'),
    props: true
  },
  {
    path: '/sessions/:id/chat',
    name: 'SessionChat',
    component: () => import('@/views/SessionChat.vue'),
    props: true
  },
  {
    path: '/roles',
    name: 'RoleList',
    component: () => import('@/views/RoleList.vue')
  },
  {
    path: '/roles/create',
    name: 'RoleCreate',
    component: () => import('@/views/RoleCreate.vue')
  },
  {
    path: '/roles/:id',
    name: 'RoleDetail',
    component: () => import('@/views/RoleDetail.vue'),
    props: true
  },
  {
    path: '/templates',
    name: 'TemplateList',
    component: () => import('@/views/TemplateList.vue')
  },
  {
    path: '/templates/:id',
    name: 'TemplateDetail',
    component: () => import('@/views/TemplateDetail.vue'),
    props: true
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue')
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})
```

## 二、视图组件

```typescript
// views/SessionList.vue
<template>
  <div class="session-list">
    <div class="header">
      <h1>会话列表</h1>
      <el-button type="primary" @click="createSession">
        创建会话
      </el-button>
    </div>
    
    <div class="filter-bar">
      <el-select v-model="filterState" placeholder="筛选状态">
        <el-option label="全部" value="" />
        <el-option label="等待中" value="waiting" />
        <el-option label="运行中" value="running" />
        <el-option label="已暂停" value="paused" />
        <el-option label="已完成" value="completed" />
      </el-select>
    </div>
    
    <el-table :data="filteredSessions" stripe>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="state" label="状态">
        <template #default="{ row }">
          <el-tag :type="getStateType(row.state)">
            {{ getStateLabel(row.state) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="创建时间" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button link @click="viewSession(row.id)">查看</el-button>
          <el-button link @click="enterChat(row.id)">进入</el-button>
          <el-button link type="danger" @click="deleteSession(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination
      v-model:current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      @current-change="loadSessions"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import type { Session } from '@/types'

const router = useRouter()
const sessionStore = useSessionStore()

const filterState = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const filteredSessions = computed(() => {
  if (!filterState.value) return sessionStore.sessions
  return sessionStore.sessions.filter(s => s.state === filterState.value)
})

const loadSessions = async () => {
  await sessionStore.fetchSessions({
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value
  })
}

const createSession = () => {
  router.push('/sessions/create')
}

const viewSession = (id: string) => {
  router.push(`/sessions/${id}`)
}

const enterChat = (id: string) => {
  router.push(`/sessions/${id}/chat`)
}

const deleteSession = async (id: string) => {
  await sessionStore.deleteSession(id)
  await loadSessions()
}

const getStateType = (state: string) => {
  const types: Record<string, string> = {
    waiting: 'info',
    running: 'success',
    paused: 'warning',
    completed: '',
    error: 'danger'
  }
  return types[state] || ''
}

const getStateLabel = (state: string) => {
  const labels: Record<string, string> = {
    waiting: '等待中',
    running: '运行中',
    paused: '已暂停',
    completed: '已完成',
    error: '错误'
  }
  return labels[state] || state
}

onMounted(loadSessions)
</script>
```

## 三、会话聊天视图

```typescript
// views/SessionChat.vue
<template>
  <div class="session-chat">
    <div class="chat-header">
      <el-button @click="goBack">返回</el-button>
      <h2>{{ session?.name }}</h2>
      <el-tag :type="getStateType(session?.state)">
        {{ getStateLabel(session?.state) }}
      </el-tag>
    </div>
    
    <div class="chat-messages" ref="messagesContainer">
      <div
        v-for="msg in messages"
        :key="msg.id"
        :class="['message', msg.role]"
      >
        <div class="message-header">
          <span class="sender">{{ msg.participantName }}</span>
          <span class="time">{{ formatTime(msg.timestamp) }}</span>
        </div>
        <div class="message-content" v-html="renderContent(msg.content)" />
        <div v-if="msg.mentalActivity" class="mental-activity">
          💭 {{ msg.mentalActivity }}
        </div>
      </div>
    </div>
    
    <div class="chat-input">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        placeholder="输入消息..."
        :disabled="!canSend"
        @keydown.enter.ctrl="sendMessage"
      />
      <div class="input-actions">
        <el-button @click="sendMessage" :disabled="!canSend">
          发送
        </el-button>
        <el-button @click="skipTurn" :disabled="!canSkip">
          跳过
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useWebSocket } from '@/composables/useWebSocket'

const props = defineProps<{ id: string }>()

const route = useRoute()
const router = useRouter()
const sessionStore = useSessionStore()
const ws = useWebSocket()

const messages = ref<any[]>([])
const inputMessage = ref('')
const messagesContainer = ref<HTMLElement>()

const session = computed(() => sessionStore.currentSession)
const canSend = computed(() => session.value?.state === 'running')
const canSkip = computed(() => session.value?.config?.allowSkip)

const loadSession = async () => {
  await sessionStore.fetchSession(props.id)
  await loadMessages()
}

const loadMessages = async () => {
  const msgs = await sessionStore.fetchMessages(props.id)
  messages.value = msgs
  scrollToBottom()
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  
  await sessionStore.sendMessage(props.id, {
    content: inputMessage.value,
    type: 'text'
  })
  
  inputMessage.value = ''
  await loadMessages()
}

const skipTurn = async () => {
  await sessionStore.skipTurn(props.id)
  await loadMessages()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const renderContent = (content: string) => {
  // 简单的Markdown渲染
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString()
}

const goBack = () => {
  router.back()
}

onMounted(async () => {
  await loadSession()
  
  // 连接WebSocket
  ws.connect(`/ws/sessions/${props.id}`)
  ws.onMessage((msg) => {
    if (msg.type === 'message') {
      messages.value.push(msg.data)
      scrollToBottom()
    }
  })
})

onUnmounted(() => {
  ws.disconnect()
})
</script>
```
