// Role types
export interface Role {
  id: string
  name: string
  category: RoleCategory
  description?: string
  avatar?: string
  base_personality: Record<string, number>
  system_prompt: string
  mental_config?: Record<string, any>
  emotional_model?: Record<string, any>
  speaking_style?: SpeakingStyle
  skills: string[]
  parameters: Record<string, any>
  variables: Record<string, any>
  created_at: string
  updated_at: string
}

export type RoleCategory = 'debater' | 'mediator' | 'narrator' | 'judge' | 'player' | 'teacher' | 'student' | 'custom'

export interface SpeakingStyle {
  formality: number
  length_preference: 'short' | 'medium' | 'long'
  tone: string
  vocabulary_level: string
  use_emoji: boolean
  interruptions: boolean
  pause_frequency: number
}

// Session types
export interface Session {
  id: string
  name: string
  topic: string
  state: SessionState
  template_id?: string
  role_ids: string[]
  config: Record<string, any>
  metadata: Record<string, any>
  created_at: string
  started_at?: string
  ended_at?: string
  created_by?: string
}

export type SessionState = 'created' | 'initializing' | 'waiting' | 'running' | 'paused' | 'ending' | 'completed' | 'error' | 'cancelled'

export interface Message {
  id: string
  session_id: string
  participant_id?: string
  role_id?: string
  type: string
  content: string
  mental_activity?: string
  turn_number: number
  metadata: Record<string, any>
  created_at: string
}

export interface Participant {
  id: string
  session_id: string
  role_id: string
  name: string
  is_ai: boolean
  is_active: boolean
  joined_at: string
  left_at?: string
  metadata: Record<string, any>
}

// Rule types
export interface Rule {
  id: string
  name: string
  type: RuleType
  description?: string
  constraints: Constraint[]
  triggers: Trigger[]
  consequences: Consequence[]
  enabled: boolean
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export type RuleType = 'debate' | 'game' | 'negotiation' | 'teaching' | 'roleplay' | 'custom'

export interface Constraint {
  id: string
  type: string
  target: string
  condition: string
  error_message?: string
  enabled: boolean
  priority: number
}

export interface Trigger {
  id: string
  type: string
  event_type?: string
  condition: string
  enabled: boolean
  cooldown: number
}

export interface Consequence {
  id: string
  action: string
  params: Record<string, any>
  delay: number
  enabled: boolean
}

// Template types
export interface Template {
  id: string
  name: string
  type: TemplateType
  description?: string
  category: string
  content: Record<string, any>
  preview?: Record<string, any>
  tags: string[]
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export type TemplateType = 'role' | 'rule' | 'scene'

// API Response types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

export interface ApiError {
  detail: string
}
