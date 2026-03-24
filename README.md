# NonHumanArena

[中文说明](#中文项目说明) | English

## Project Overview

**NonHumanArena** (Chinese: 非人竞技场) is an AI-driven multi-agent debate and discussion platform that enables AI characters to engage in structured debates and conversations based on customizable rules and scenarios.

### Key Features

- 🎭 **Multi-Agent System**: Create and manage multiple AI characters with unique personalities, backgrounds, and speaking styles
- 📋 **Rule Engine**: Define custom debate rules including speaking order, time limits, and content requirements
- 🧠 **Mental Activity System**: AI characters generate internal monologues that influence their decision-making
- 💓 **Heartbeat Mechanism**: AI agents can proactively think and speak during idle periods
- 🔌 **Plugin Architecture**: Extensible skill system for specialized debate techniques
- 📝 **History & Playback**: Complete session recording with playback and export capabilities
- 🌐 **Real-time Communication**: WebSocket-based bidirectional communication
- 🎨 **Template System**: Pre-built templates for roles, rules, and complete scenarios

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3)                     │
├─────────────────────────────────────────────────────────────┤
│                    REST API + WebSocket                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐  │
│  │  Role   │  │  Rule   │  │ Session │  │     LLM     │  │
│  │ Module  │  │ Module  │  │ Module  │  │   Module   │  │
│  └───┬─────┘  └───┬─────┘  └───┬─────┘  └──────┬──────┘  │
│      │             │             │               │          │
│      └─────────────┴─────────────┴───────────────┘          │
│                        Event Bus                             │
│      ┌───────────────┬─────────────────┬───────────────┐  │
│      │               │                 │               │      │
│  ┌───┴───────────────┴─────────────────┴───────────────┴─┐│
│  │             Core (DI Container, Heartbeat)                ││
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                 Database (SQLite/PostgreSQL)                 │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **LLM**: OpenAI API (extensible to Claude, Ollama, etc.)

### Frontend
- **Framework**: Vue 3 + TypeScript
- **State Management**: Pinia
- **UI Library**: Custom components
- **Build Tool**: Vite

## Project Structure

```
NonHumanArena/
├── design/                    # Design documentation
│   ├── 需求和功能.md           # Requirements & Features
│   ├── 总体设计.md            # Overall Architecture
│   ├── 场景用例.md            # Use Cases
│   ├── 技术选型.md            # Technology Selection
│   ├── 设计检查报告.md        # Design Review Report
│   ├── 数据结构/              # Data Structures
│   └── 详细设计/              # Detailed Design
│       ├── 1_core/            # Core (Event Bus, DI, Heartbeat)
│       ├── 2_modules_role/    # Role Module
│       ├── 3_modules_rule/    # Rule Module
│       ├── 4_modules_session/ # Session Module
│       ├── 5_modules_ai/      # AI Engine
│       ├── 6_modules_llm/     # LLM Adapters
│       ├── 7_modules_skill/   # Skill Module
│       ├── 8_modules_template/ # Template Module
│       ├── 9_modules_history/  # History Module
│       ├── 10_api/            # API Layer
│       ├── 11_infrastructure/ # Infrastructure
│       └── 12_frontend/       # Frontend Design
├── plan/                      # Development Plan
│   └── 开发计划.md            # Development Roadmap
├── rules/                      # Coding Standards
│   ├── backend.md             # Backend Rules
│   └── frontend.md            # Frontend Rules
├── src/                       # Source Code
│   ├── backend/              # Backend Application
│   │   ├── core/             # Core components
│   │   │   ├── event_bus/    # Event Bus
│   │   │   ├── container/    # DI Container
│   │   │   └── heartbeat/    # Heartbeat Engine
│   │   ├── modules/          # Business modules
│   │   │   ├── role/         # Role Module
│   │   │   ├── rule/         # Rule Module
│   │   │   ├── session/      # Session Module
│   │   │   ├── ai/           # AI Engine
│   │   │   ├── llm/          # LLM Module
│   │   │   ├── skill/        # Skill Module
│   │   │   ├── template/     # Template Module
│   │   │   └── history/      # History Module
│   │   ├── api/              # API Layer
│   │   ├── models/           # SQLAlchemy Models
│   │   ├── schemas/          # Pydantic Schemas
│   │   ├── repositories/     # Repository Layer
│   │   ├── services/         # Service Layer
│   │   ├── events/           # Event Definitions
│   │   ├── llm/              # LLM Adapters
│   │   │   └── adapters/     # Adapter Implementations
│   │   ├── infrastructure/   # Infrastructure Layer
│   │   └── utils/            # Utilities
│   └── frontend/            # Frontend Application
│       ├── src/              # Source code
│       │   ├── api/          # API Client
│       │   ├── assets/       # Static assets
│       │   ├── components/   # Vue Components
│       │   ├── composables/  # Composition API
│       │   ├── router/       # Vue Router
│       │   ├── stores/        # Pinia Stores
│       │   ├── types/         # TypeScript Types
│       │   ├── utils/         # Utilities
│       │   └── views/        # Page Views
│       ├── tests/            # Tests
│       └── config/           # Configuration
└── README.md
```

## Development Progress

### Phase 1: MVP ✅ Design Complete
| Module | Status | Description |
|--------|--------|-------------|
| Requirements | ✅ Complete | Design documentation ready |
| Data Structures | ✅ Complete | Role, Rule, Session, AI models defined |
| Core Architecture | ✅ Complete | Event Bus, DI Container, Heartbeat designed |
| Module Design | ✅ Complete | All module interfaces and flows designed |
| Project Structure | ✅ Complete | Directory structure created |

### Phase 2: MVP Implementation 🔨 In Progress

| Phase | Module | Status | Priority |
|-------|--------|--------|----------|
| 1 | Infrastructure | ⏳ Todo | P0 |
| | - Dependency Injection Container | ⏳ Todo | P0 |
| | - Event Bus | ⏳ Todo | P0 |
| | - Database Infrastructure | ⏳ Todo | P1 |
| 2 | Data Layer | ⏳ Todo | P0 |
| | - Role Models & Repository | ⏳ Todo | P0 |
| | - Rule Models & Repository | ⏳ Todo | P0 |
| | - Session Models & Repository | ⏳ Todo | P0 |
| 3 | Service Layer | ⏳ Todo | P0 |
| | - Role Service | ⏳ Todo | P0 |
| | - Rule Service & Engine | ⏳ Todo | P0 |
| | - Session Service & State Machine | ⏳ Todo | P0 |
| 4 | LLM & AI Engine | ⏳ Todo | P0 |
| | - LLM Adapter (OpenAI) | ⏳ Todo | P0 |
| | - AI Decision Engine | ⏳ Todo | P0 |
| | - Mental Activity System | ⏳ Todo | P1 |
| | - Heartbeat Engine | ⏳ Todo | P0 |
| 5 | API Layer | ⏳ Todo | P0 |
| | - REST API | ⏳ Todo | P0 |
| | - WebSocket | ⏳ Todo | P0 |
| 6 | Frontend | ⏳ Todo | P1 |
| | - Project Setup | ⏳ Todo | P0 |
| | - Chat Room Page | ⏳ Todo | P0 |
| | - Role/Rule Editor | ⏳ Todo | P1 |
| 7 | Integration | ⏳ Todo | P1 |
| 8 | Advanced Features | 📋 Planned | P2 |

### Phase 3: Enhanced Features 📋 Planned
| Feature | Priority | Description |
|---------|----------|-------------|
| Mental Activity | P1 | AI internal monologue generation |
| Heartbeat Mechanism | P1 | Proactive AI thinking |
| History & Playback | P1 | Session recording and playback |
| Skill System | P2 | Pluggable debate techniques |
| Template System | P2 | Scenario templates |
| Multi-LLM Support | P2 | Claude, Ollama adapters |

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API Key

### Installation (Coming Soon)

```bash
# Clone the repository
git clone https://github.com/SereneWing/non-human-arena.git
cd non-human-arena

# Backend setup
cd src/backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Frontend setup
cd ../src/frontend
npm install
npm run dev
```

## Development Guide

See [plan/开发计划.md](./plan/开发计划.md) for detailed development roadmap.

See [rules/backend.md](./rules/backend.md) for backend coding standards.

See [rules/frontend.md](./rules/frontend.md) for frontend coding standards.

## Use Cases

1. **Academic Debates**: Formal debates on various topics
2. **Game Simulation**: Werewolf, Detective games
3. **Negotiation Training**: Business negotiation scenarios
4. **Socratic Dialogue**: Knowledge exploration through Q&A
5. **Story Roleplay**: Custom characters and narratives

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

---

## 中文项目说明

### 项目名：非人竞技场

**非人竞技场** (NonHumanArena) 是一个 AI 驱动的多智能体辩论与讨论平台，支持创建具有独特个性的 AI 角色、定义灵活的辩论规则，让 AI 角色围绕预设议题展开富有深度的讨论与辩论。

### 核心功能

| 功能 | 说明 |
|------|------|
| 🎭 角色管理 | 创建具有独特性格和发言风格的 AI 角色 |
| 📋 规则引擎 | 自定义辩论规则（发言顺序、时间限制、内容要求等） |
| 🧠 心理活动 | AI 生成内心独白，影响决策行为 |
| 💓 心跳机制 | AI 在空闲时主动思考或发言 |
| 🔌 技能系统 | 可插拔的专业辩论技巧 |
| 📝 历史回放 | 完整保存和回放讨论内容 |

### 项目结构

```
非人竞技场/
├── design/              # 设计文档
├── plan/                # 开发计划
├── rules/               # 编码规范
├── src/                 # 源代码
│   ├── backend/         # 后端应用
│   └── frontend/        # 前端应用
└── README.md
```

### 开发阶段

- **第一阶段（MVP）**：✅ 设计完成，🔨 目录结构创建完成，实现中
- **第二阶段（增强版）**：📋 规划中
- **第三阶段（完善版）**：📋 规划中

详细设计文档见 [design/](./design/) 目录，开发计划见 [plan/](./plan/) 目录。
