# 前端 API 层

## 一、API 客户端定义

```typescript
// api/client.ts
import axios, { AxiosInstance, AxiosError } from 'axios'

class ApiClient {
  private client: AxiosInstance
  
  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
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
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // 处理未授权
          localStorage.removeItem('token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }
  
  async get<T>(url: string, params?: any): Promise<T> {
    return this.client.get(url, { params })
  }
  
  async post<T>(url: string, data?: any): Promise<T> {
    return this.client.post(url, data)
  }
  
  async put<T>(url: string, data?: any): Promise<T> {
    return this.client.put(url, data)
  }
  
  async patch<T>(url: string, data?: any): Promise<T> {
    return this.client.patch(url, data)
  }
  
  async delete<T>(url: string): Promise<T> {
    return this.client.delete(url)
  }
}

export const apiClient = new ApiClient()
```

## 二、会话 API

```typescript
// api/session.ts
import { apiClient } from './client'
import type { Session, Message, SessionConfig, PaginationParams } from '@/types'

export interface CreateSessionParams {
  name: string
  templateId: string
  roleIds: string[]
  config?: SessionConfig
}

export interface UpdateSessionParams {
  name?: string
  state?: string
  config?: SessionConfig
}

export interface SendMessageParams {
  content: string
  type: 'text' | 'action'
}

class SessionApi {
  async list(params?: {
    skip?: number
    limit?: number
    state?: string
  }): Promise<{ items: Session[]; total: number }> {
    return apiClient.get('/sessions', params)
  }
  
  async get(id: string): Promise<Session> {
    return apiClient.get(`/sessions/${id}`)
  }
  
  async create(data: CreateSessionParams): Promise<Session> {
    return apiClient.post('/sessions', data)
  }
  
  async update(id: string, data: UpdateSessionParams): Promise<Session> {
    return apiClient.patch(`/sessions/${id}`, data)
  }
  
  async delete(id: string): Promise<void> {
    return apiClient.delete(`/sessions/${id}`)
  }
  
  async start(id: string): Promise<Session> {
    return apiClient.post(`/sessions/${id}/start`)
  }
  
  async pause(id: string): Promise<Session> {
    return apiClient.post(`/sessions/${id}/pause`)
  }
  
  async resume(id: string): Promise<Session> {
    return apiClient.post(`/sessions/${id}/resume`)
  }
  
  async end(id: string): Promise<Session> {
    return apiClient.post(`/sessions/${id}/end`)
  }
  
  async getMessages(
    sessionId: string,
    params?: { skip?: number; limit?: number }
  ): Promise<Message[]> {
    return apiClient.get(`/sessions/${sessionId}/messages`, params)
  }
  
  async sendMessage(
    sessionId: string,
    data: SendMessageParams
  ): Promise<Message> {
    return apiClient.post(`/sessions/${sessionId}/messages`, data)
  }
  
  async skipTurn(sessionId: string): Promise<void> {
    return apiClient.post(`/sessions/${sessionId}/skip`)
  }
  
  async getHistory(
    sessionId: string,
    format?: 'json' | 'markdown' | 'html'
  ): Promise<string> {
    return apiClient.get(`/sessions/${sessionId}/history`, { format })
  }
}

export const sessionApi = new SessionApi()
```

## 三、角色 API

```typescript
// api/role.ts
import { apiClient } from './client'
import type { Role, RoleCategory } from '@/types'

export interface CreateRoleParams {
  name: string
  category: RoleCategory
  description?: string
  avatar?: string
  systemPrompt: string
  basePersonality?: Record<string, number>
  mentalConfig?: any
  emotionalModel?: any
  speakingStyle?: any
  skills?: string[]
  parameters?: Record<string, any>
  variables?: Record<string, any>
}

export interface UpdateRoleParams extends Partial<CreateRoleParams> {}

class RoleApi {
  async list(params?: {
    skip?: number
    limit?: number
    category?: RoleCategory
  }): Promise<{ items: Role[]; total: number }> {
    return apiClient.get('/roles', params)
  }
  
  async get(id: string): Promise<Role> {
    return apiClient.get(`/roles/${id}`)
  }
  
  async create(data: CreateRoleParams): Promise<Role> {
    return apiClient.post('/roles', data)
  }
  
  async update(id: string, data: UpdateRoleParams): Promise<Role> {
    return apiClient.patch(`/roles/${id}`, data)
  }
  
  async delete(id: string): Promise<void> {
    return apiClient.delete(`/roles/${id}`)
  }
  
  async search(query: string): Promise<Role[]> {
    return apiClient.get('/roles/search', { query })
  }
  
  async duplicate(id: string, newName?: string): Promise<Role> {
    return apiClient.post(`/roles/${id}/duplicate`, { newName })
  }
  
  async getTemplates(): Promise<Role[]> {
    return apiClient.get('/roles/templates')
  }
}

export const roleApi = new RoleApi()
```

## 四、模板 API

```typescript
// api/template.ts
import { apiClient } from './client'
import type { Template, TemplateType } from '@/types'

export interface RenderTemplateParams {
  variables: Record<string, any>
  strict?: boolean
}

class TemplateApi {
  async list(params?: {
    skip?: number
    limit?: number
    type?: TemplateType
    category?: string
  }): Promise<{ items: Template[]; total: number }> {
    return apiClient.get('/templates', params)
  }
  
  async get(id: string): Promise<Template> {
    return apiClient.get(`/templates/${id}`)
  }
  
  async create(data: Partial<Template>): Promise<Template> {
    return apiClient.post('/templates', data)
  }
  
  async update(id: string, data: Partial<Template>): Promise<Template> {
    return apiClient.patch(`/templates/${id}`, data)
  }
  
  async delete(id: string): Promise<void> {
    return apiClient.delete(`/templates/${id}`)
  }
  
  async render(id: string, params: RenderTemplateParams): Promise<{
    success: boolean
    content: string
    errors?: string[]
  }> {
    return apiClient.post(`/templates/${id}/render`, params)
  }
  
  async validate(content: string, variables: Record<string, any>): Promise<string[]> {
    return apiClient.post('/templates/validate', { content, variables })
  }
  
  async search(query: string, type?: TemplateType): Promise<Template[]> {
    return apiClient.get('/templates/search', { query, type })
  }
  
  async getCategories(): Promise<string[]> {
    return apiClient.get('/templates/categories')
  }
}

export const templateApi = new TemplateApi()
```

## 五、历史 API

```typescript
// api/history.ts
import { apiClient } from './client'
import type { HistoryExportFormat } from '@/types'

class HistoryApi {
  async list(params?: {
    skip?: number
    limit?: number
    sessionId?: string
    startDate?: string
    endDate?: string
  }): Promise<{ items: any[]; total: number }> {
    return apiClient.get('/history', params)
  }
  
  async get(id: string): Promise<any> {
    return apiClient.get(`/history/${id}`)
  }
  
  async export(
    sessionId: string,
    format: HistoryExportFormat = 'json'
  ): Promise<string> {
    return apiClient.get(`/history/export`, { sessionId, format })
  }
  
  async delete(id: string): Promise<void> {
    return apiClient.delete(`/history/${id}`)
  }
  
  async deleteBySession(sessionId: string): Promise<void> {
    return apiClient.delete(`/history/session/${sessionId}`)
  }
}

export const historyApi = new HistoryApi()
```

## 六、API 统一导出

```typescript
// api/index.ts
export { apiClient } from './client'
export { sessionApi } from './session'
export { roleApi } from './role'
export { templateApi } from './template'
export { historyApi } from './history'
```
