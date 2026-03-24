import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'
import wsClient from '@/api/websocket'
import type { Session, SessionCreate, Message } from '@/types'

export const useSessionStore = defineStore('session', () => {
  const sessions = ref<Session[]>([])
  const currentSession = ref<Session | null>(null)
  const messages = ref<Message[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const wsConnected = ref(false)

  const activeSessions = computed(() =>
    sessions.value.filter((s) => s.state === 'running' || s.state === 'paused')
  )

  async function fetchSessions(skip = 0, limit = 100) {
    loading.value = true
    error.value = null
    try {
      const response = await api.getSessions(skip, limit)
      sessions.value = response.items
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch sessions'
    } finally {
      loading.value = false
    }
  }

  async function fetchSession(id: string) {
    loading.value = true
    error.value = null
    try {
      currentSession.value = await api.getSession(id)
      return currentSession.value
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch session'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createSession(data: SessionCreate) {
    loading.value = true
    error.value = null
    try {
      const session = await api.createSession(data)
      sessions.value.unshift(session)
      return session
    } catch (e: any) {
      error.value = e.message || 'Failed to create session'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function startSession(id: string) {
    loading.value = true
    error.value = null
    try {
      const session = await api.startSession(id)
      updateSessionInList(session)
      if (currentSession.value?.id === id) {
        currentSession.value = session
      }
      return session
    } catch (e: any) {
      error.value = e.message || 'Failed to start session'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function pauseSession(id: string) {
    loading.value = true
    error.value = null
    try {
      const session = await api.pauseSession(id)
      updateSessionInList(session)
      if (currentSession.value?.id === id) {
        currentSession.value = session
      }
      return session
    } catch (e: any) {
      error.value = e.message || 'Failed to pause session'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function resumeSession(id: string) {
    loading.value = true
    error.value = null
    try {
      const session = await api.resumeSession(id)
      updateSessionInList(session)
      if (currentSession.value?.id === id) {
        currentSession.value = session
      }
      return session
    } catch (e: any) {
      error.value = e.message || 'Failed to resume session'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function endSession(id: string) {
    loading.value = true
    error.value = null
    try {
      const session = await api.endSession(id)
      updateSessionInList(session)
      if (currentSession.value?.id === id) {
        currentSession.value = session
      }
      return session
    } catch (e: any) {
      error.value = e.message || 'Failed to end session'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchMessages(sessionId: string, skip = 0, limit = 100) {
    try {
      messages.value = await api.getSessionMessages(sessionId, skip, limit)
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch messages'
    }
  }

  async function sendMessage(sessionId: string, content: string, roleId?: string) {
    try {
      const message = await api.sendMessage(sessionId, { content, role_id: roleId })
      messages.value.push(message)
      return message
    } catch (e: any) {
      error.value = e.message || 'Failed to send message'
      throw e
    }
  }

  function connectWebSocket(sessionId: string) {
    wsClient.connect(sessionId)
    wsClient.on('connected', () => {
      wsConnected.value = true
    })
    wsClient.on('disconnected', () => {
      wsConnected.value = false
    })
    wsClient.on('message', (data) => {
      if (data.session_id === sessionId) {
        messages.value.push(data.message)
      }
    })
  }

  function disconnectWebSocket() {
    wsClient.disconnect()
    wsConnected.value = false
  }

  function updateSessionInList(session: Session) {
    const index = sessions.value.findIndex((s) => s.id === session.id)
    if (index !== -1) {
      sessions.value[index] = session
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    sessions,
    currentSession,
    messages,
    loading,
    error,
    wsConnected,
    activeSessions,
    fetchSessions,
    fetchSession,
    createSession,
    startSession,
    pauseSession,
    resumeSession,
    endSession,
    fetchMessages,
    sendMessage,
    connectWebSocket,
    disconnectWebSocket,
    clearError,
  }
})
