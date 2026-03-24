# 前端编码规范

## 一、代码风格

### 1.1 基础规范

- **使用 TypeScript**：所有组件和逻辑必须使用 TypeScript
- **使用 Composition API**：`<script setup>` 语法优先
- **使用 Pinia**：状态管理统一使用 Pinia，不使用 Vuex
- **组件文件命名**：使用 PascalCase，如 `UserProfile.vue`
- **组合式函数命名**：使用 camelCase，以 `use` 开头，如 `useUserProfile`
- **类型定义文件**：使用 `.ts` 后缀（如 `user.ts`），或 `.d.ts` 用于全局类型声明

### 1.2 缩进与格式

- **缩进**：使用 2 空格
- **分号**：使用分号结尾
- **引号**：使用单引号
- **换行**：使用 LF 风格

```typescript
// ✅ 正确
const getUserName = (user: User): string => {
  return user.name;
};

// ❌ 错误
const getUserName = (user: User): string => {
  return user.name
}
```

### 1.3 命名规范

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 组件 | PascalCase | `ChatRoom.vue` |
| 组合式函数 | camelCase (use前缀) | `useWebSocket.ts` |
| Store | camelCase | `useSessionStore.ts` |
| 类型/接口 | PascalCase | `UserProfile`, `IMessage` |
| 枚举 | PascalCase | `SessionStatus` |
| 常量 | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 文件夹 | kebab-case | `chat-room/` |

### 1.4 Vue 组件规范

#### 模板部分

```vue
<template>
  <div class="component-name">
    <slot name="header" />
    
    <div class="content">
      <ChildComponent
        :prop-a="valueA"
        :prop-b="valueB"
        @event-a="handleEventA"
      />
    </div>
    
    <slot name="footer" />
  </div>
</template>
```

#### 脚本部分

```vue
<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import type { User } from '@/types'

// Props 定义
interface Props {
  userId: string
  showDetail?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetail: false
})

// Emits 定义
const emit = defineEmits<{
  (e: 'update', value: User): void
  (e: 'delete', id: string): void
}>()

// Store
const userStore = useUserStore()

// 响应式数据
const isLoading = ref(false)
const localData = ref<User | null>(null)

// 计算属性
const displayName = computed(() => {
  return localData.value?.name ?? 'Unknown'
})

// 方法
const fetchData = async () => {
  isLoading.value = true
  try {
    localData.value = await userStore.getUser(props.userId)
  } finally {
    isLoading.value = false
  }
}

// 生命周期
onMounted(() => {
  fetchData()
})

// 暴露给父组件
defineExpose({
  refresh: fetchData
})
</script>

<style scoped lang="scss">
.component-name {
  padding: 16px;
}
</style>
```

## 二、类型定义

### 2.1 类型组织结构

```
src/
├── types/
│   ├── index.ts          # 导出所有类型
│   ├── user.ts           # 用户相关类型
│   ├── session.ts        # 会话相关类型
│   └── api.ts            # API 响应类型
```

### 2.2 接口与类型定义

```typescript
// types/user.ts

export interface User {
  id: string
  name: string
  email: string
  avatar?: string
  createdAt: Date
}

export interface UserProfile extends User {
  bio: string
  preferences: UserPreferences
}

export interface UserPreferences {
  theme: 'light' | 'dark'
  language: string
  notifications: NotificationSettings
}

export type UserRole = 'admin' | 'user' | 'guest'

// 枚举
export enum UserStatus {
  Active = 'active',
  Inactive = 'inactive',
  Banned = 'banned'
}

// 工厂函数
export const createDefaultUser = (partial: Partial<User>): User => ({
  id: crypto.randomUUID(),
  name: 'Anonymous',
  email: '',
  createdAt: new Date(),
  ...partial
})
```

### 2.3 API 类型

```typescript
// types/api.ts

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: ApiError
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, unknown>
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}

export interface ApiRequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  url: string
  params?: Record<string, unknown>
  data?: unknown
  headers?: Record<string, string>
}
```

## 三、状态管理 (Pinia)

### 3.1 Store 组织

```
src/
├── stores/
│   ├── index.ts          # 导出所有 store
│   ├── user.ts           # 用户状态
│   ├── session.ts        # 会话状态
│   └── ui.ts             # UI 状态
```

### 3.2 Store 定义规范

```typescript
// stores/session.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Session, Message, Participant } from '@/types'
import { sessionApi } from '@/api'

export const useSessionStore = defineStore('session', () => {
  // ===== 状态 =====
  const currentSession = ref<Session | null>(null)
  const messages = ref<Message[]>([])
  const participants = ref<Participant[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // ===== 计算属性 =====
  const isRunning = computed(() => 
    currentSession.value?.status === 'running'
  )
  
  const messageCount = computed(() => messages.value.length)
  
  const participantNames = computed(() =>
    participants.value.map(p => p.name)
  )
  
  // ===== Actions =====
  const createSession = async (data: CreateSessionDto) => {
    isLoading.value = true
    error.value = null
    
    try {
      currentSession.value = await sessionApi.create(data)
      messages.value = []
      participants.value = []
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isLoading.value = false
    }
  }
  
  const sendMessage = async (content: string) => {
    if (!currentSession.value) {
      throw new Error('No active session')
    }
    
    const message = await sessionApi.sendMessage(currentSession.value.id, content)
    messages.value.push(message)
  }
  
  const clearSession = () => {
    currentSession.value = null
    messages.value = []
    participants.value = []
    error.value = null
  }
  
  // ===== 返回 =====
  return {
    // 状态
    currentSession,
    messages,
    participants,
    isLoading,
    error,
    
    // 计算属性
    isRunning,
    messageCount,
    participantNames,
    
    // Actions
    createSession,
    sendMessage,
    clearSession
  }
})
```

### 3.3 Store 使用规范

```typescript
// ✅ 正确：在组件中使用
<script setup>
import { useSessionStore } from '@/stores/session'

const sessionStore = useSessionStore()

// 解构响应式数据（保持响应式）
const { currentSession, messages, isLoading } = storeToRefs(sessionStore)

// 解构 actions（保持响应式）
const { sendMessage, clearSession } = storeToRefs(sessionStore)
</script>

// ❌ 错误：直接解构
const { currentSession } = useSessionStore() // 会失去响应式
```

## 四、API 调用

### 4.1 API 模块组织

```
src/
├── api/
│   ├── index.ts           # API 客户端实例
│   ├── user.ts            # 用户 API
│   ├── session.ts        # 会话 API
│   └── types.ts           # API 特定类型
```

### 4.2 API 客户端

```typescript
// api/index.ts
import axios, { AxiosInstance, AxiosError } from 'axios'
import type { ApiResponse, ApiError } from '@/types'

class ApiClient {
  private client: AxiosInstance
  
  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    this.setupInterceptors()
  }
  
  private setupInterceptors() {
    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )
    
    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => response.data,
      (error: AxiosError<ApiError>) => {
        const message = error.response?.data?.message ?? error.message
        return Promise.reject(new Error(message))
      }
    )
  }
  
  async get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
    return this.client.get(url, { params })
  }
  
  async post<T>(url: string, data?: unknown): Promise<T> {
    return this.client.post(url, data)
  }
  
  async put<T>(url: string, data?: unknown): Promise<T> {
    return this.client.put(url, data)
  }
  
  async delete<T>(url: string): Promise<T> {
    return this.client.delete(url)
  }
}

export const apiClient = new ApiClient()
```

### 4.3 API 模块定义

```typescript
// api/session.ts
import { apiClient } from './index'
import type { Session, Message, CreateSessionDto } from '@/types'

export const sessionApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    apiClient.get<Session[]>('/sessions', params),
  
  get: (id: string) =>
    apiClient.get<Session>(`/sessions/${id}`),
  
  create: (data: CreateSessionDto) =>
    apiClient.post<Session>('/sessions', data),
  
  update: (id: string, data: Partial<Session>) =>
    apiClient.put<Session>(`/sessions/${id}`, data),
  
  delete: (id: string) =>
    apiClient.delete(`/sessions/${id}`),
  
  start: (id: string) =>
    apiClient.post<Session>(`/sessions/${id}/start`),
  
  stop: (id: string) =>
    apiClient.post<Session>(`/sessions/${id}/stop`),
  
  sendMessage: (sessionId: string, content: string) =>
    apiClient.post<Message>(`/sessions/${sessionId}/messages`, { content }),
  
  getMessages: (sessionId: string, params?: { skip?: number; limit?: number }) =>
    apiClient.get<Message[]>(`/sessions/${sessionId}/messages`, params)
}
```

## 五、组件规范

### 5.1 组件分类

| 类型 | 存放位置 | 命名规范 | 示例 |
|------|----------|----------|------|
| 基础组件 | `components/common/` | PascalCase | `BaseButton.vue` |
| 业务组件 | `components/` | PascalCase | `ChatRoom.vue` |
| 布局组件 | `components/layout/` | PascalCase | `AppHeader.vue` |
| 表单组件 | `components/form/` | PascalCase | `UserForm.vue` |

### 5.2 Props 定义

```typescript
// ✅ 使用 withDefaults 定义默认值
interface Props {
  title: string
  count?: number
  items: string[]
  status: 'pending' | 'success' | 'error'
}

const props = withDefaults(defineProps<Props>(), {
  count: 0,
  status: 'pending'
})

// ✅ 使用 validator 验证
interface Props {
  size: 'small' | 'medium' | 'large'
}

const props = defineProps<Props>()
const validSizes = ['small', 'medium', 'large']

// ⚠️ validator 示例
// defineProps({
//   size: {
//     type: String,
//     validator: (value: string) => validSizes.includes(value)
//   }
// })
```

### 5.3 事件定义

```typescript
// ✅ 使用 defineEmits 定义事件
const emit = defineEmits<{
  (e: 'update', value: string): void
  (e: 'delete', id: string): void
  (e: 'click'): void
}>()

// 使用
emit('update', newValue)
```

## 六、WebSocket 规范

### 6.1 WebSocket 管理器

```typescript
// utils/websocket.ts
interface WebSocketOptions {
  url: string
  reconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  onMessage: (data: unknown) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
}

class WebSocketManager {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private reconnectTimer: number | null = null
  private options: Required<WebSocketOptions>
  
  constructor(options: WebSocketOptions) {
    this.options = {
      reconnect: true,
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
      ...options
    }
    
    this.connect()
  }
  
  connect() {
    this.ws = new WebSocket(this.options.url)
    
    this.ws.onopen = () => {
      this.reconnectAttempts = 0
      this.options.onOpen?.()
    }
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.options.onMessage(data)
    }
    
    this.ws.onclose = () => {
      this.options.onClose?.()
      this.scheduleReconnect()
    }
    
    this.ws.onerror = (error) => {
      this.options.onError?.(error)
    }
  }
  
  private scheduleReconnect() {
    if (!this.options.reconnect) return
    if (this.reconnectAttempts >= this.options.maxReconnectAttempts) return
    
    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectAttempts++
      this.connect()
    }, this.options.reconnectInterval)
  }
  
  send(data: unknown): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
      return true
    }
    return false
  }
  
  close() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }
    this.ws?.close()
    this.ws = null
  }
}

export { WebSocketManager }
```

### 6.2 使用示例

```typescript
// stores/session.ts
import { WebSocketManager } from '@/utils/websocket'

const connectWebSocket = (sessionId: string) => {
  const ws = new WebSocketManager({
    url: `ws://localhost:8000/ws/${sessionId}`,
    onMessage: (data) => {
      const message = data as WebSocketMessage
      switch (message.type) {
        case 'message':
          messages.value.push(message.payload)
          break
        case 'participant_joined':
          participants.value.push(message.payload)
          break
      }
    },
    onOpen: () => {
      isConnected.value = true
    },
    onClose: () => {
      isConnected.value = false
    }
  })
  
  return ws
}
```

## 七、样式规范

### 7.1 样式组织

```vue
<template>
  <div class="component-wrapper">
    <div class="component-content">
      <!-- 内容 -->
    </div>
  </div>
</template>

<style scoped lang="scss">
// 使用 scoped 避免污染全局样式
// 使用 lang="scss" 使用 SCSS 功能

.component-wrapper {
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  
  .component-content {
    color: var(--text-color);
  }
}

// 使用 CSS 变量
.component-wrapper {
  color: var(--el-text-color-primary);
  background: var(--el-bg-color);
}
</style>
```

### 7.2 响应式断点

```scss
// styles/variables.scss

// 断点
$breakpoints: (
  'sm': 640px,
  'md': 768px,
  'lg': 1024px,
  'xl': 1280px,
  '2xl': 1536px
);

// 使用
@media (min-width: map-get($breakpoints, 'md')) {
  .container {
    padding: 24px;
  }
}
```

## 八、目录结构

```
src/
├── api/                    # API 调用模块
├── assets/                 # 静态资源
│   ├── images/
│   └── styles/
├── components/             # Vue 组件
│   ├── common/            # 基础组件
│   ├── form/              # 表单组件
│   └── layout/            # 布局组件
├── composables/           # 组合式函数 (可选)
├── router/                 # 路由配置
├── stores/                 # Pinia 状态管理
├── types/                  # TypeScript 类型定义
├── utils/                  # 工具函数
├── views/                  # 页面组件
├── App.vue
└── main.ts
```

## 九、Git 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
perf: 性能优化
test: 测试
chore: 构建/工具变更
```

示例：
```
feat(session): 添加会话实时消息推送
fix(role): 修复角色列表加载问题
docs(api): 更新 API 文档
```
