# NonHumanArena

[中文说明](#中文项目说明) | English

## Project Overview

**NonHumanArena** (Chinese: 非人竞技场) is an AI-driven multi-agent debate and discussion platform that enables two AI characters to engage in structured conversations and debates based on customizable personalities and scenarios.

### Key Features

- 🎭 **Two AI Characters**: Create two AI agents with unique personalities, backgrounds, and speaking styles
- 💬 **Real-time Chat**: Both AI characters can converse with each other in real-time
- 🔄 **Auto Mode**: Automatic conversation mode where AI takes turns speaking
- 📊 **Conversation History**: Save and view conversation history
- 🔒 **Security**: API key only stored in memory during runtime (not persisted)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (HTML/JS)                   │
├─────────────────────────────────────────────────────────────┤
│                    REST API + SSE Streaming                 │
├─────────────────────────────────────────────────────────────┤
│                     FastAPI Backend                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐  │
│  │  Agent  │  │Conversation│  │   LLM   │  │   Storage   │  │
│  │ Module  │  │  Module  │  │ Adapter │  │    Module   │  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Backend**: Python 3.11+ / FastAPI
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **LLM**: MiniMax API (extensible to OpenAI, Claude, etc.)

## Quick Start

### Prerequisites
- Python 3.11+
- MiniMax API Key (or other compatible API)

### Installation

```bash
cd src
pip install -r requirements.txt
python -m src.main
```

Then open http://127.0.0.1:8000 in your browser.

### Configuration

On first use, configure your API key in the web interface:
- API Key (required) - stored only in memory during runtime
- Model: minimax-m2.7 (default)
- Base URL: https://api.minimax.chat/v1 (default)
- Max Tokens: 100000 (default)
- Temperature: 0.7 (default)

## Security Notes

- **Local Binding**: Server binds to `127.0.0.1` (localhost only)
- **API Key Protection**: API key is only cached in memory during runtime and is NOT saved to disk
- After server restart, you need to re-enter the API key

## Project Structure

```
NonHumanArena/
├── src/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration management
│   ├── api/
│   │   └── routes.py        # API endpoints
│   ├── agents/
│   │   ├── agent.py         # Agent model
│   │   └── conversation.py  # Conversation manager
│   ├── llm/
│   │   ├── adapter.py       # Chat message adapter
│   │   └── manager.py      # LLM manager
│   ├── storage/
│   │   └── file_storage.py  # File-based storage
│   ├── css/
│   │   └── style.css        # Styles
│   ├── js/
│   │   └── app.js           # Frontend logic
│   └── index.html           # Main page
├── data/
│   ├── config.txt           # Non-sensitive config
│   └── conversations/       # Saved conversations
├── design/                  # Design documentation
├── plan/                    # Development plan
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/config` | Get current configuration |
| POST | `/api/config` | Update configuration |
| GET | `/api/conversations` | List all conversations |
| POST | `/api/conversation` | Create new conversation |
| GET | `/api/conversation/{id}` | Get conversation details |
| DELETE | `/api/conversation/{id}` | Delete conversation |
| POST | `/api/conversation/{id}/message/{agent_id}` | Send message |
| POST | `/api/conversation/{id}/generate/{agent_id}` | Generate AI response |
| GET | `/api/conversation/{id}/stream/{agent_id}` | Stream AI response (SSE) |
| POST | `/api/conversation/{id}/auto/start` | Start auto mode |
| POST | `/api/conversation/{id}/auto/stop` | Stop auto mode |

## License

MIT License

---

## 中文项目说明

### 项目名：非人竞技场

**非人竞技场** (NonHumanArena) 是一个 AI 驱动的双智能体对话系统，让两个 AI 角色根据各自的人设和话题展开对话。

### 核心功能

- 🎭 双AI角色：创建两个具有独特性格的AI角色
- 💬 实时对话：两个AI角色实时交流
- 🔄 自动模式：AI自动轮流发言
- 📊 对话历史：保存和查看历史对话
- 🔒 安全保护：API Key仅在运行时缓存在内存中

### 快速开始

```bash
cd src
pip install -r requirements.txt
python -m src.main
```

然后在浏览器中打开 http://127.0.0.1:8000

### 安全说明

- **本地绑定**：服务仅监听 `127.0.0.1`（仅本地访问）
- **API Key保护**：API Key仅在运行时缓存在内存中，不会保存到磁盘
- 服务重启后需要重新输入API Key

### 项目结构

```
非人竞技场/
├── src/                     # 源代码
│   ├── main.py              # FastAPI入口
│   ├── config.py            # 配置管理
│   ├── api/routes.py        # API接口
│   ├── agents/              # 智能体模块
│   ├── llm/                 # LLM模块
│   ├── storage/             # 存储模块
│   ├── css/                 # 样式
│   ├── js/                  # 前端逻辑
│   └── index.html          # 主页
├── data/                    # 数据目录
├── design/                  # 设计文档
├── plan/                    # 开发计划
└── README.md
```
