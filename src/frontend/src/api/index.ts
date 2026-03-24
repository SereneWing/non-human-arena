import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  Role,
  RoleCreate,
  RoleUpdate,
  Session,
  SessionCreate,
  Message,
  Rule,
  RuleCreate,
  Template,
} from '@/types'

const API_BASE_URL = '/api/v1'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  // Roles API
  async getRoles(skip = 0, limit = 100): Promise<Role[]> {
    const response = await this.client.get<Role[]>('/roles', {
      params: { skip, limit },
    })
    return response.data
  }

  async getRole(id: string): Promise<Role> {
    const response = await this.client.get<Role>(`/roles/${id}`)
    return response.data
  }

  async createRole(data: RoleCreate): Promise<Role> {
    const response = await this.client.post<Role>('/roles', data)
    return response.data
  }

  async updateRole(id: string, data: RoleUpdate): Promise<Role> {
    const response = await this.client.put<Role>(`/roles/${id}`, data)
    return response.data
  }

  async deleteRole(id: string): Promise<void> {
    await this.client.delete(`/roles/${id}`)
  }

  // Sessions API
  async getSessions(skip = 0, limit = 100): Promise<{ items: Session[]; total: number; page: number; page_size: number; has_more: boolean }> {
    const response = await this.client.get('/sessions', {
      params: { skip, limit },
    })
    return response.data
  }

  async getSession(id: string): Promise<Session & { participants: any[]; message_count: number }> {
    const response = await this.client.get(`/sessions/${id}`)
    return response.data
  }

  async createSession(data: SessionCreate): Promise<Session> {
    const response = await this.client.post<Session>('/sessions', data)
    return response.data
  }

  async startSession(id: string): Promise<Session> {
    const response = await this.client.post<Session>(`/sessions/${id}/start`)
    return response.data
  }

  async pauseSession(id: string): Promise<Session> {
    const response = await this.client.post<Session>(`/sessions/${id}/pause`)
    return response.data
  }

  async resumeSession(id: string): Promise<Session> {
    const response = await this.client.post<Session>(`/sessions/${id}/resume`)
    return response.data
  }

  async endSession(id: string): Promise<Session> {
    const response = await this.client.post<Session>(`/sessions/${id}/end`)
    return response.data
  }

  async getSessionMessages(sessionId: string, skip = 0, limit = 100): Promise<Message[]> {
    const response = await this.client.get<Message[]>(`/sessions/${sessionId}/messages`, {
      params: { skip, limit },
    })
    return response.data
  }

  async sendMessage(sessionId: string, data: { content: string; role_id?: string }): Promise<Message> {
    const response = await this.client.post<Message>(`/sessions/${sessionId}/messages`, data)
    return response.data
  }

  // Rules API
  async getRules(skip = 0, limit = 100): Promise<Rule[]> {
    const response = await this.client.get<Rule[]>('/rules', {
      params: { skip, limit },
    })
    return response.data
  }

  async getRule(id: string): Promise<Rule> {
    const response = await this.client.get<Rule>(`/rules/${id}`)
    return response.data
  }

  async createRule(data: RuleCreate): Promise<Rule> {
    const response = await this.client.post<Rule>('/rules', data)
    return response.data
  }

  async deleteRule(id: string): Promise<void> {
    await this.client.delete(`/rules/${id}`)
  }

  // Templates API
  async getRoleTemplates(): Promise<{ templates: Template[] }> {
    const response = await this.client.get('/templates/roles')
    return response.data
  }

  async getRuleTemplates(): Promise<{ templates: Template[] }> {
    const response = await this.client.get('/templates/rules')
    return response.data
  }

  async getSceneTemplates(): Promise<{ templates: Template[] }> {
    const response = await this.client.get('/templates/scenes')
    return response.data
  }
}

export const api = new ApiClient()
export default api
