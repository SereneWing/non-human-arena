# 前端状态管理

## 一、Pinia Store 定义

```typescript
// stores/session.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { sessionApi } from '@/api'
import type { Session, Message, SessionConfig } from '@/types'

export const useSessionStore = defineStore('session', () => {
  // 状态
  const sessions = ref<Session[]>([])
  const currentSession = ref<Session | null>(null)
  const messages = ref<Message[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 计算属性
  const activeSessions = computed(() => 
    sessions.value.filter(s => s.state === 'running' || s.state === 'paused')
  )
  
  const sessionById = computed(() => (id: string) => 
    sessions.value.find(s => s.id === id)
  )
  
  // Actions
  async function fetchSessions(params?: {
    skip?: number
    limit?: number
    state?: string
  }) {
    loading.value = true
    error.value = null
    
    try {
      const result = await sessionApi.list(params)
      sessions.value = result.items
      return result
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }
  
  async function fetchSession(id: string) {
    loading.value = true
    error.value = null
    
    try {
      const session = await sessionApi.get(id)
      currentSession.value = session
      return session
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }
  
  async function createSession(data: {
    name: string
    templateId: string
    roleIds: string[]
    config?: SessionConfig
  }) {
    loading.value = true
    error.value = null
    
    try {
      const session = await sessionApi.create(data)
      sessions.value.unshift(session)
      return session
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }
  
  async function updateSession(id: string, data: Partial<Session>) {
    loading.value = true
    error.value = null
    
    try {
      const session = await sessionApi.update(id, data)
      
      const index = sessions.value.findIndex(s => s.id === id)
      if (index !== -1) {
        sessions.value[index] = session
      }
      
      if (currentSession.value?.id === id) {
        currentSession.value = session
      }
      
      return session
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }
  
  async function deleteSession(id: string) {
    loading.value = true
    error.value = null
    
    try {
      await sessionApi.delete(id)
      sessions.value = sessions.value.filter(s => s.id !== id)
      
      if (currentSession.value?.id === id) {
        currentSession.value = null
      }
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }
  
  async function startSession(id: string) {
    return updateSession(id, { state: 'running' })
  }
  
  async function pauseSession(id: string) {
    return updateSession(id, { state: 'paused' })
  }
  
  async function resumeSession(id: string) {
    return updateSession(id, { state: 'running' })
  }
  
  async function endSession(id: string) {
    return updateSession(id, { state: 'completed' })
  }
  
  async function fetchMessages(sessionId: string, params?: {
    skip?: number
    limit?: number
  }) {
    try {
      const msgs = await sessionApi.getMessages(sessionId, params)
      messages.value = msgs
      return msgs
    } catch (e) {
      error.value = e.message
      throw e
    }
  }
  
  async function sendMessage(sessionId: string, data: {
    content: string
    type: 'text' | 'action'
  }) {
    try {
      const message = await sessionApi.sendMessage(sessionId, data)
      messages.value.push(message)
      return message
    } catch (e) {
      error.value = e.message
      throw e
    }
  }
  
  async function skipTurn(sessionId: string) {
    try {
      await sessionApi.skipTurn(sessionId)
      await fetchMessages(sessionId)
    } catch (e) {
      error.value = e.message
      throw e
    }
  }
  
  function clearCurrentSession() {
    currentSession.value = null
    messages.value = []
  }
  
  return {
    // 状态
    sessions,
    currentSession,
    messages,
    loading,
    error,
    
    // 计算属性
    activeSessions,
    sessionById,
    
    // Actions
    fetchSessions,
    fetchSession,
    createSession,
    updateSession,
    deleteSession,
    startSession,
    pauseSession,
    resumeSession,
    endSession,
    fetchMessages,
    sendMessage,
    skipTurn,
    clearCurrentSession
  }
})
```

## 二、角色 Store

```typescript
// stores/role.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { roleApi } from '@/api'
import type { Role, RoleCategory } from '@/types'

export const useRoleStore = defineStore('role', () => {
  // 状态
  const roles = ref<Role[]>([])
  const currentRole = ref<Role | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 计算属性
  const rolesByCategory = computed(() => (category: RoleCategory) =>
    roles.value.filter(r => r.category === category)
  )
  
  const roleById = computed(() => (id: string) =>
    roles.value.find(r => r.id === id)
  )
  
  // Actions
  async function fetchRoles(params?: {
    skip?: number
    limit?: number
    category?: RoleCategory
  }) {
    loading.value = true
    error.value = null
    
    try {
      const result = await roleApi.list(params)
      roles.value = result.items
      return result
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }
  
  async function fetchRole(id: string) {
    loading.value = true
    error.value = null
    
    try {
      const role = await roleApi.get(id)
      currentRole.value = role
      return role
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }
  
  async function createRole(data: Partial<Role>) {
    loading.value = true
    error.value = null
    
    try {
      const role = await roleApi.create(data)
      roles.value.unshift(role)
      return role
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }
  
  async function updateRole(id: string, data: Partial<Role>) {
    loading.value = true
    error.value = null
    
    try {
      const role = await roleApi.update(id, data)
      
      const index = roles.value.findIndex(r => r.id === id)
      if (index !== -1) {
        roles.value[index] = role
      }
      
      if (currentRole.value?.id === id) {
        currentRole.value = role
      }
      
      return role
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }
  
  async function deleteRole(id: string) {
    loading.value = true
    error.value = null
    
    try {
      await roleApi.delete(id)
      roles.value = roles.value.filter(r => r.id !== id)
      
      if (currentRole.value?.id === id) {
        currentRole.value = null
      }
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }
  
  function clearCurrentRole() {
    currentRole.value = null
  }
  
  return {
    // 状态
    roles,
    currentRole,
    loading,
    error,
    
    // 计算属性
    rolesByCategory,
    roleById,
    
    // Actions
    fetchRoles,
    fetchRole,
    createRole,
    updateRole,
    deleteRole,
    clearCurrentRole
  }
})
```

## 三、WebSocket Store

```typescript
// stores/websocket.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export const useWebSocketStore = defineStore('websocket', () => {
  const status = ref<WebSocketStatus>('disconnected')
  const error = ref<string | null>(null)
  const listeners = ref<Map<string, Set<(data: any) => void>>>(new Map())
  
  let ws: WebSocket | null = null
  let reconnectTimer: number | null = null
  let currentUrl: string | null = null
  
  function connect(url: string) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      return
    }
    
    currentUrl = url
    status.value = 'connecting'
    error.value = null
    
    try {
      ws = new WebSocket(url)
      
      ws.onopen = () => {
        status.value = 'connected'
        error.value = null
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          notifyListeners(data.type, data)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }
      
      ws.onerror = (e) => {
        status.value = 'error'
        error.value = 'WebSocket connection error'
        console.error('WebSocket error:', e)
      }
      
      ws.onclose = () => {
        status.value = 'disconnected'
        scheduleReconnect()
      }
    } catch (e) {
      status.value = 'error'
      error.value = e.message
    }
  }
  
  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    
    currentUrl = null
    
    if (ws) {
      ws.close()
      ws = null
    }
    
    status.value = 'disconnected'
  }
  
  function send(type: string, data: any) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type, ...data }))
    } else {
      console.warn('WebSocket not connected')
    }
  }
  
  function subscribe(type: string, callback: (data: any) => void) {
    if (!listeners.value.has(type)) {
      listeners.value.set(type, new Set())
    }
    listeners.value.get(type)!.add(callback)
    
    return () => {
      listeners.value.get(type)?.delete(callback)
    }
  }
  
  function notifyListeners(type: string, data: any) {
    listeners.value.get(type)?.forEach(cb => cb(data))
  }
  
  function scheduleReconnect() {
    if (reconnectTimer || !currentUrl) {
      return
    }
    
    reconnectTimer = window.setTimeout(() => {
      reconnectTimer = null
      if (currentUrl) {
        connect(currentUrl)
      }
    }, 3000)
  }
  
  return {
    status,
    error,
    connect,
    disconnect,
    send,
    subscribe
  }
})
```
