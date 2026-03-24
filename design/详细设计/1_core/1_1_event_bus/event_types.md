# 事件类型定义

## 一、事件类型枚举

```python
class EventType(Enum):
    """
    事件类型枚举
    
    分类：
    - ROLE: 角色事件
    - RULE: 规则事件
    - SESSION: 会话事件
    - MESSAGE: 消息事件
    - AI: AI行为事件
    - SKILL: 技能事件
    - SYSTEM: 系统事件
    """
    
    # ==================== 角色事件 ====================
    ROLE_CREATED = "role.created"           # 角色创建
    ROLE_UPDATED = "role.updated"           # 角色更新
    ROLE_DELETED = "role.deleted"           # 角色删除
    ROLE_LOADED = "role.loaded"             # 角色加载到会话
    
    # ==================== 规则事件 ====================
    RULE_LOADED = "rule.loaded"             # 规则加载
    RULE_TRIGGERED = "rule.triggered"       # 规则触发
    RULE_VIOLATED = "rule.violated"        # 规则违反
    RULE_CHECKED = "rule.checked"          # 规则检查完成
    RULE_SATISFIED = "rule.satisfied"      # 规则满足
    
    # ==================== 会话事件 ====================
    SESSION_CREATED = "session.created"     # 会话创建
    SESSION_STARTED = "session.started"     # 会话开始
    SESSION_PAUSED = "session.paused"      # 会话暂停
    SESSION_RESUMED = "session.resumed"   # 会话恢复
    SESSION_ENDED = "session.ended"        # 会话结束
    SESSION_ERROR = "session.error"        # 会话错误
    
    # ==================== 消息事件 ====================
    MESSAGE_SENT = "message.sent"          # 消息发送
    MESSAGE_RECEIVED = "message.received"  # 消息接收
    MESSAGE_DELIVERED = "message.delivered" # 消息送达
    MESSAGE_READ = "message.read"           # 消息已读
    
    # ==================== AI行为事件 ====================
    AI_THINK = "ai.think"                  # AI开始思考
    AI_ACT = "ai.act"                      # AI采取行动
    AI_SKIP = "ai.skip"                    # AI选择跳过
    AI_HEARTBEAT = "ai.heartbeat"         # AI心跳
    AI_READY = "ai.ready"                  # AI准备就绪
    AI_THINKING = "ai.thinking"           # AI思考中
    
    # ==================== 技能事件 ====================
    SKILL_TRIGGERED = "skill.triggered"     # 技能触发
    SKILL_RESULT = "skill.result"          # 技能执行结果
    SKILL_APPLIED = "skill.applied"        # 技能应用完成
    
    # ==================== 模板事件 ====================
    TEMPLATE_LOADED = "template.loaded"     # 模板加载
    TEMPLATE_RENDERED = "template.rendered" # 模板渲染完成
    
    # ==================== 历史事件 ====================
    HISTORY_SAVED = "history.saved"        # 历史保存
    HISTORY_EXPORTED = "history.exported"  # 历史导出
    
    # ==================== 系统事件 ====================
    HEARTBEAT_TICK = "heartbeat.tick"      # 心跳Tick
    SYSTEM_SHUTDOWN = "system.shutdown"   # 系统关闭
    SYSTEM_STARTUP = "system.startup"      # 系统启动
    ERROR = "error"                        # 通用错误
    
    # ==================== 会话状态事件 ====================
    SESSION_STATE_CHANGED = "session.state_changed"  # 会话状态变更
```

## 二、事件类型分组

```python
class EventGroup:
    """事件类型分组"""
    
    ROLE_EVENTS = [
        EventType.ROLE_CREATED,
        EventType.ROLE_UPDATED,
        EventType.ROLE_DELETED,
        EventType.ROLE_LOADED,
    ]
    
    RULE_EVENTS = [
        EventType.RULE_LOADED,
        EventType.RULE_TRIGGERED,
        EventType.RULE_VIOLATED,
        EventType.RULE_CHECKED,
        EventType.RULE_SATISFIED,
    ]
    
    SESSION_EVENTS = [
        EventType.SESSION_CREATED,
        EventType.SESSION_STARTED,
        EventType.SESSION_PAUSED,
        EventType.SESSION_RESUMED,
        EventType.SESSION_ENDED,
        EventType.SESSION_ERROR,
        EventType.SESSION_STATE_CHANGED,
    ]
    
    MESSAGE_EVENTS = [
        EventType.MESSAGE_SENT,
        EventType.MESSAGE_RECEIVED,
        EventType.MESSAGE_DELIVERED,
        EventType.MESSAGE_READ,
    ]
    
    AI_EVENTS = [
        EventType.AI_THINK,
        EventType.AI_ACT,
        EventType.AI_SKIP,
        EventType.AI_HEARTBEAT,
        EventType.AI_READY,
        EventType.AI_THINKING,
    ]
    
    SKILL_EVENTS = [
        EventType.SKILL_TRIGGERED,
        EventType.SKILL_RESULT,
        EventType.SKILL_APPLIED,
    ]
    
    SYSTEM_EVENTS = [
        EventType.HEARTBEAT_TICK,
        EventType.SYSTEM_SHUTDOWN,
        EventType.SYSTEM_STARTUP,
        EventType.ERROR,
    ]
```

## 三、事件类型文档

### 3.1 角色事件

| 事件类型 | 触发时机 | 发布者 | 订阅者 |
|---------|---------|--------|--------|
| ROLE_CREATED | 创建新角色 | RoleModule | API层、历史模块 |
| ROLE_UPDATED | 更新角色 | RoleModule | API层 |
| ROLE_DELETED | 删除角色 | RoleModule | 会话模块 |
| ROLE_LOADED | 角色加载到会话 | SessionModule | AI引擎 |

### 3.2 规则事件

| 事件类型 | 触发时机 | 发布者 | 订阅者 |
|---------|---------|--------|--------|
| RULE_LOADED | 规则加载到会话 | RuleModule | 会话模块 |
| RULE_TRIGGERED | 规则触发条件满足 | RuleEngine | 会话模块 |
| RULE_VIOLATED | 规则被违反 | RuleEngine | 会话模块、AI引擎 |
| RULE_CHECKED | 规则检查完成 | RuleEngine | AI引擎 |
| RULE_SATISFIED | 规则条件满足 | RuleEngine | 会话模块 |

### 3.3 会话事件

| 事件类型 | 触发时机 | 发布者 | 订阅者 |
|---------|---------|--------|--------|
| SESSION_CREATED | 创建新会话 | SessionModule | API层、历史模块 |
| SESSION_STARTED | 会话开始 | SessionModule | AI引擎、心跳引擎 |
| SESSION_PAUSED | 会话暂停 | SessionModule | AI引擎、心跳引擎 |
| SESSION_RESUMED | 会话恢复 | SessionModule | AI引擎、心跳引擎 |
| SESSION_ENDED | 会话结束 | SessionModule | AI引擎、心跳引擎、历史模块 |
    | SESSION_ERROR | 会话错误 | SessionModule | API层 |
    | SESSION_STATE_CHANGED | 会话状态变更 | SessionModule | 所有订阅状态的模块 |

### 3.4 消息事件

| 事件类型 | 触发时机 | 发布者 | 订阅者 |
|---------|---------|--------|--------|
| MESSAGE_SENT | 消息发送 | 会话模块 | AI引擎 |
| MESSAGE_RECEIVED | 消息接收 | 会话模块 | AI引擎、规则引擎 |
| MESSAGE_DELIVERED | 消息送达 | WebSocket | 会话模块 |
| MESSAGE_READ | 消息已读 | WebSocket | 会话模块 |

### 3.5 AI事件

> ⚠️ **重要**: AI事件处理说明

| 事件类型 | 触发时机 | 发布者 | 订阅者 | 处理说明 |
|---------|---------|--------|--------|----------|
| AI_THINK | AI开始思考 | AIDecisionEngine | 会话模块 | 会话模块记录AI思考开始，更新参与者状态 |
| AI_ACT | AI采取行动 | AIDecisionEngine | 会话模块、WebSocket | 会话模块处理AI动作，WebSocket推送前端显示 |
| AI_SKIP | AI选择跳过 | AIDecisionEngine | 会话模块 | 会话模块处理跳过，更新回合进度 |
| AI_HEARTBEAT | AI心跳 | HeartbeatEngine | AI引擎 | AI引擎更新活跃状态，检测超时 |
| AI_READY | AI准备就绪 | AIEngine | 会话模块 | 会话模块更新参与者状态，触发下一回合 |
| AI_THINKING | AI思考中 | AIEngine | WebSocket | WebSocket推送前端显示思考动画 |

#### AI事件处理流程

```
AIDecisionEngine 决策流程:
1. AI_THINK → 订阅者: SessionModule (记录思考开始)
2. AI_ACT → 订阅者: SessionModule (处理动作), WebSocket (推送显示)
3. AI_SKIP → 订阅者: SessionModule (处理跳过)

AIEngine 思考流程:
1. AI_THINKING → 订阅者: WebSocket (显示思考动画)
2. AI_READY → 订阅者: SessionModule (准备就绪)

HeartbeatEngine:
1. AI_HEARTBEAT → 订阅者: AIEngine (心跳响应)
```

### 3.6 系统事件

| 事件类型 | 触发时机 | 发布者 | 订阅者 |
|---------|---------|--------|--------|
| HEARTBEAT_TICK | 心跳Tick | HeartbeatEngine | 所有模块 |
| SYSTEM_SHUTDOWN | 系统关闭 | Main | 所有模块 |
| SYSTEM_STARTUP | 系统启动 | Main | 所有模块 |
| ERROR | 通用错误 | 任何模块 | 日志模块 |
