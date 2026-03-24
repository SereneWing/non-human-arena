<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionStore } from '@/stores'

const route = useRoute()
const router = useRouter()
const sessionStore = useSessionStore()

const messageInput = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

onMounted(async () => {
  const sessionId = route.params.id as string
  await sessionStore.fetchSession(sessionId)
  await sessionStore.fetchMessages(sessionId)
  sessionStore.connectWebSocket(sessionId)
  scrollToBottom()
})

onUnmounted(() => {
  sessionStore.disconnectWebSocket()
})

async function sendMessage() {
  if (!messageInput.value.trim()) return
  
  const sessionId = route.params.id as string
  try {
    await sessionStore.sendMessage(sessionId, messageInput.value)
    messageInput.value = ''
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Failed to send message:', error)
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

async function handleStart() {
  const sessionId = route.params.id as string
  await sessionStore.startSession(sessionId)
}

async function handlePause() {
  const sessionId = route.params.id as string
  await sessionStore.pauseSession(sessionId)
}

async function handleEnd() {
  const sessionId = route.params.id as string
  await sessionStore.endSession(sessionId)
}
</script>

<template>
  <div class="chat-room">
    <header class="chat-header">
      <div class="header-left">
        <button class="btn btn-back" @click="router.push('/sessions')">← 返回</button>
        <h2>{{ sessionStore.currentSession?.name || '讨论室' }}</h2>
      </div>
      <div class="header-status">
        <span :class="['status-badge', `status-${sessionStore.currentSession?.state}`]">
          {{ sessionStore.currentSession?.state || 'loading' }}
        </span>
      </div>
    </header>
    
    <div class="session-controls">
      <button v-if="sessionStore.currentSession?.state === 'created'" class="btn btn-primary" @click="handleStart">
        开始讨论
      </button>
      <button v-if="sessionStore.currentSession?.state === 'running'" class="btn btn-secondary" @click="handlePause">
        暂停
      </button>
      <button v-if="sessionStore.currentSession?.state === 'paused'" class="btn btn-primary" @click="sessionStore.resumeSession(route.params.id as string)">
        继续
      </button>
      <button v-if="['running', 'paused'].includes(sessionStore.currentSession?.state || '')" class="btn btn-danger" @click="handleEnd">
        结束
      </button>
    </div>
    
    <div class="messages-container" ref="messagesContainer">
      <div v-if="sessionStore.messages.length === 0" class="empty-messages">
        <p>暂无消息</p>
        <p class="hint">开始讨论后，AI角色将开始对话</p>
      </div>
      
      <div v-for="message in sessionStore.messages" :key="message.id" class="message">
        <div class="message-header">
          <span class="message-role">{{ message.role_id || '系统' }}</span>
          <span class="message-time">{{ new Date(message.created_at).toLocaleTimeString() }}</span>
        </div>
        <div class="message-content">{{ message.content }}</div>
        <div v-if="message.mental_activity" class="message-mental">
          💭 {{ message.mental_activity }}
        </div>
      </div>
    </div>
    
    <form @submit.prevent="sendMessage" class="message-input-form">
      <input
        v-model="messageInput"
        type="text"
        placeholder="输入消息..."
        class="message-input"
        :disabled="sessionStore.currentSession?.state !== 'running'"
      />
      <button type="submit" class="btn btn-send" :disabled="!messageInput.trim() || sessionStore.currentSession?.state !== 'running'">
        发送
      </button>
    </form>
    
    <div class="connection-status">
      <span :class="['ws-indicator', { connected: sessionStore.wsConnected }]"></span>
      {{ sessionStore.wsConnected ? '已连接' : '未连接' }}
    </div>
  </div>
</template>

<style scoped>
.chat-room {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 40px);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.btn-back {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
}

.session-controls {
  display: flex;
  gap: 10px;
  padding: 15px 0;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
}

.empty-messages {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}

.empty-messages .hint {
  font-size: 0.9rem;
  margin-top: 10px;
}

.message {
  margin-bottom: 20px;
  padding: 15px;
  background: var(--bg-secondary);
  border-radius: 10px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.message-role {
  font-weight: 600;
}

.message-time {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.message-content {
  line-height: 1.6;
}

.message-mental {
  margin-top: 10px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-style: italic;
}

.message-input-form {
  display: flex;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid var(--border-color);
}

.message-input {
  flex: 1;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-color);
  color: var(--text-primary);
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

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-send {
  background-color: var(--primary-color);
  color: white;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 10px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.ws-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f44336;
}

.ws-indicator.connected {
  background: #4caf50;
}
</style>
