# 项目源代码结构说明

本文档描述 NonHumanArena 项目的源代码目录结构及其作用。

## 整体目录结构

```
src/
├── backend/                    # 后端应用 (Python/FastAPI)
│   ├── core/                   # 核心组件
│   ├── modules/                # 业务模块
│   ├── api/                    # API 层
│   ├── llm/                    # LLM 适配器
│   ├── events/                 # 事件定义
│   ├── infrastructure/         # 基础设施
│   └── utils/                  # 工具函数
│
└── frontend/                   # 前端应用 (Vue 3/TypeScript)
    ├── src/                    # 源代码
    ├── tests/                  # 测试
    ├── public/                 # 静态资源
    └── config/                 # 配置文件
```

---

## 后端目录详解 (backend/)

### 1. core/ - 核心组件

系统的核心基础设施，为整个应用提供基础服务。

| 目录 | 说明 |
|------|------|
| `core/container/` | **依赖注入容器** - 管理组件生命周期、解决依赖关系 |
| `core/event_bus/` | **事件总线** - 模块间通信的核心机制 |
| `core/heartbeat/` | **心跳引擎** - AI 主动思考和发言的调度器 |

**设计原则**：
- 核心组件应该保持简洁，无业务逻辑
- 核心组件应该是单例的
- 核心组件通过事件总线与其他模块通信

### 2. modules/ - 业务模块

按照领域划分的业务模块，每个模块包含完整的数据层、服务层。

| 模块 | 说明 | 核心功能 |
|------|------|----------|
| `modules/role/` | 角色模块 | AI 角色定义、性格特征、系统提示词 |
| `modules/rule/` | 规则模块 | 辩论规则、触发器、后果执行 |
| `modules/session/` | 会话模块 | 会话管理、状态机、消息处理 |
| `modules/ai/` | AI 引擎 | 决策引擎、心理活动、情绪系统 |
| `modules/skill/` | 技能模块 | 可插拔的专业辩论技巧 |
| `modules/template/` | 模板模块 | 角色模板、规则模板、场景模板 |
| `modules/history/` | 历史模块 | 会话记录、回放、导出 |

**模块内部结构** (每个模块都包含)：

```
modules/<module>/
├── models/          # SQLAlchemy 数据模型
├── schemas/        # Pydantic 请求/响应模型
├── repositories/    # 数据访问层
├── services/       # 业务逻辑层
└── __init__.py     # 模块导出
```

**设计原则**：
- 每个模块应该是一个独立的领域
- 模块间通过事件总线通信，不直接调用
- 模块内部使用仓储模式隔离数据访问

### 3. api/ - API 层

FastAPI 路由和端点定义。

| 目录 | 说明 | 端点示例 |
|------|------|----------|
| `api/roles/` | 角色相关 API | `GET/POST/PUT/DELETE /api/v1/roles` |
| `api/rules/` | 规则相关 API | `GET/POST/PUT/DELETE /api/v1/rules` |
| `api/sessions/` | 会话相关 API | `POST /api/v1/sessions`, `POST /api/v1/sessions/{id}/start` |
| `api/templates/` | 模板相关 API | `GET/POST /api/v1/templates` |
| `api/history/` | 历史相关 API | `GET /api/v1/history/{session_id}` |
| `api/ws/` | WebSocket 处理 | `/ws/{session_id}` |

**设计原则**：
- API 层只做请求验证和响应格式化
- 业务逻辑委托给 services 层
- 使用依赖注入获取 services

### 4. llm/ - LLM 适配器

大语言模型适配器，封装不同 LLM 提供商的接口。

| 目录 | 说明 |
|------|------|
| `llm/adapters/` | 具体适配器实现 (OpenAI, Claude, Ollama 等) |

**适配器接口**：
```python
class ILLMAdapter(Protocol):
    async def generate(self, prompt: str, config: LLMConfig) -> str: ...
    async def chat(self, messages: List[ChatMessage], config: LLMConfig) -> str: ...
```

**设计原则**：
- 使用适配器模式隔离不同 LLM 提供商
- 所有适配器实现统一的接口
- 配置与实现分离

### 5. events/ - 事件定义

系统中所有事件的类型定义。

```python
# events/__init__.py
class EventType(Enum):
    # 系统事件
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    
    # 会话事件
    SESSION_CREATED = "session.created"
    SESSION_STARTED = "session.started"
    SESSION_PAUSED = "session.paused"
    SESSION_RESUMED = "session.resumed"
    SESSION_ENDED = "session.ended"
    
    # 消息事件
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"
    MESSAGE_PROCESSED = "message.processed"
    
    # AI 事件
    AI_THINKING = "ai.thinking"
    AI_SPOKE = "ai.spoke"
    AI_HEARTBEAT = "ai.heartbeat"
    
    # 规则事件
    RULE_TRIGGERED = "rule.triggered"
    RULE_CONSEQUENCE_EXECUTED = "rule.consequence.executed"
```

### 6. infrastructure/ - 基础设施

数据库连接、缓存、配置等基础设施服务。

### 7. utils/ - 工具函数

通用的辅助函数和工具类。

---

## 前端目录详解 (frontend/)

### 1. src/ - 源代码

Vue 3 应用的主要源代码。

| 目录 | 说明 | 职责 |
|------|------|------|
| `src/api/` | API 客户端 | 封装 HTTP 请求、WebSocket 连接 |
| `src/assets/` | 静态资源 | 图片、样式文件 |
| `src/components/` | Vue 组件 | UI 组件库 |
| `src/composables/` | 组合式函数 | 可复用的逻辑 |
| `src/router/` | 路由配置 | Vue Router 配置 |
| `src/stores/` | 状态管理 | Pinia Store |
| `src/types/` | 类型定义 | TypeScript 类型 |
| `src/utils/` | 工具函数 | 通用工具 |
| `src/views/` | 页面视图 | 路由页面组件 |

#### 1.1 components/ - 组件目录

```
src/components/
├── common/          # 通用组件 (Button, Input, Modal 等)
├── form/            # 表单组件 (Form, FormItem, Select 等)
├── layout/          # 布局组件 (Header, Sidebar, Footer 等)
└── chat/            # 聊天组件 (MessageCard, ChatInput 等)
```

#### 1.2 views/ - 页面视图

| 页面 | 说明 |
|------|------|
| `views/Home.vue` | 首页 |
| `views/RoleList.vue` | 角色列表 |
| `views/RoleEditor.vue` | 角色编辑器 |
| `views/RuleList.vue` | 规则列表 |
| `views/RuleEditor.vue` | 规则编辑器 |
| `views/SessionList.vue` | 会话列表 |
| `views/ChatRoom.vue` | 讨论室 |
| `views/History.vue` | 历史记录 |
| `views/Settings.vue` | 设置页面 |

#### 1.3 stores/ - 状态管理

| Store | 说明 |
|-------|------|
| `stores/role.ts` | 角色相关状态 |
| `stores/rule.ts` | 规则相关状态 |
| `stores/session.ts` | 会话状态、WebSocket 连接 |
| `stores/history.ts` | 历史记录状态 |
| `stores/ui.ts` | UI 状态 (侧边栏、模态框等) |

### 2. tests/ - 测试

| 目录 | 说明 |
|------|------|
| `tests/unit/` | 单元测试 |
| `tests/e2e/` | 端到端测试 |

### 3. public/ - 静态资源

直接复制到构建输出目录的静态文件。

### 4. config/ - 配置文件

环境配置、开发配置等。

---

## 模块依赖关系图

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP/WebSocket
┌─────────────────────────────┴───────────────────────────────┐
│                        API Layer                             │
│   (roles, rules, sessions, templates, history, ws)           │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                     Service Layer                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────┐  │
│  │  Role   │ │  Rule   │ │ Session │ │      AI        │  │
│  │ Service │ │ Service │ │ Service │ │    Service     │  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────────┬────────┘  │
│       │            │            │               │            │
│  ┌────┴────────────┴────────────┴───────────────┴────┐    │
│  │                   Event Bus                          │    │
│  └─────────────────────────┬────────────────────────────┘    │
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                     Repository Layer                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────┐  │
│  │  Role   │ │  Rule   │ │ Session │ │    History      │  │
│  │   Repo  │ │   Repo  │ │   Repo  │ │      Repo       │  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────────┬────────┘  │
└───────┼────────────┼───────────┼───────────────┼────────────┘
        │            │           │               │
┌───────┼────────────┼───────────┼───────────────┼────────────┐
│       └────────────┴───────────┴───────────────┘            │
│                    Database (SQLite/PostgreSQL)              │
└──────────────────────────────────────────────────────────────┘
```

---

## 开发约定

### 后端约定

1. **命名规范**：
   - 模块名：全小写，下划线分隔 (如 `role_module`)
   - 类名：PascalCase (如 `RoleService`)
   - 函数名：snake_case (如 `get_role_by_id`)
   - 常量：UPPER_SNAKE_CASE (如 `MAX_RETRY_COUNT`)

2. **分层职责**：
   - **API 层**：只做请求验证、参数转换、响应格式化
   - **Service 层**：处理业务逻辑、事务管理
   - **Repository 层**：数据访问、查询优化
   - **Model 层**：数据结构、关系定义

3. **模块通信**：
   - 模块间通过事件总线通信
   - 禁止模块间直接调用
   - 使用事件类型常量定义事件名

### 前端约定

1. **组件规范**：
   - 使用 Composition API
   - 组件文件使用 PascalCase (如 `RoleEditor.vue`)
   - 组件内部使用 `setup` 语法

2. **状态管理**：
   - 使用 Pinia 进行状态管理
   - Store 按领域划分
   - 状态应该保持不可变性

3. **样式规范**：
   - 使用 CSS 变量管理主题
   - 组件样式使用 scoped
   - 使用 BEM 命名规范

---

*文档版本：1.0.0*
*最后更新：2026-03-25*
