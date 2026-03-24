# AI 模块服务层

## 一、AI 引擎接口

```python
from typing import Protocol, List, Optional, Dict, Any
from datetime import datetime

class IAIEngine(Protocol):
    """AI引擎接口"""
    
    async def make_decision(
        self,
        context: DecisionContext
    ) -> AIDecision:
        """做出决策"""
        ...
    
    async def generate_response(
        self,
        context: DecisionContext,
        prompt: str
    ) -> str:
        """生成响应"""
        ...
    
    async def think(
        self,
        context: DecisionContext
    ) -> str:
        """思考过程"""
        ...
    
    async def validate_response(
        self,
        content: str,
        context: DecisionContext
    ) -> bool:
        """验证响应"""
        ...
```

## 二、AI 引擎实现

```python
class AIEngine:
    """AI引擎实现"""
    
    def __init__(
        self,
        llm_client: ILLMClient,
        template_service: ITemplateService,
        rule_engine: IRuleEngine,
        event_bus: IEventBus,
        config: AIEngineConfig
    ):
        self.llm_client = llm_client
        self.template_service = template_service
        self.rule_engine = rule_engine
        self.event_bus = event_bus
        self.config = config
        self._stats: Dict[str, AIStats] = {}
    
    async def make_decision(
        self,
        context: DecisionContext
    ) -> AIDecision:
        """做出AI决策"""
        start_time = datetime.now()
        
        # 发布AI开始思考事件
        await self.event_bus.publish(Event(
            type=EventType.AI_THINK,
            source="ai_engine",
            session_id=context.session_id,
            data={"participant_id": context.participant_id}
        ))
        
        # 构建提示词
        prompt = await self._build_decision_prompt(context)
        
        # 生成响应
        response = await self.llm_client.complete(prompt)
        
        # 解析决策
        decision = self._parse_decision(response, context)
        
        # 验证响应
        is_valid = await self.validate_response(decision.content, context)
        
        if not is_valid:
            # 规则检查失败，强制跳过
            decision = AIDecision(
                decision_type=DecisionType.SKIP,
                content="",
                reasoning="响应未通过规则检查"
            )
        
        # 更新统计
        await self._update_stats(context.participant_id, decision, start_time)
        
        # 发布决策事件
        event_type = EventType.AI_ACT if decision.decision_type == DecisionType.SPEAK else EventType.AI_SKIP
        await self.event_bus.publish(Event(
            type=event_type,
            source="ai_engine",
            session_id=context.session_id,
            data={
                "participant_id": context.participant_id,
                "decision": decision.__dict__
            }
        ))
        
        return decision
    
    async def _build_decision_prompt(
        self,
        context: DecisionContext
    ) -> str:
        """构建决策提示词"""
        # 加载角色信息
        role = await self._get_role(context.participant_id)
        
        # 构建上下文
        prompt_parts = [
            role.system_prompt,
            "",
            "当前辩论状态:",
            f"- 回合: {context.turn_number}",
            f"- 会话状态: {context.session_state}",
        ]
        
        # 添加历史消息
        if context.recent_messages:
            prompt_parts.append("")
            prompt_parts.append("对话历史:")
            for msg in context.recent_messages[-5:]:
                speaker = msg.get("participant_name", "未知")
                content = msg.get("content", "")
                prompt_parts.append(f"{speaker}: {content}")
        
        return "\n".join(prompt_parts)
    
    def _parse_decision(
        self,
        response: str,
        context: DecisionContext
    ) -> AIDecision:
        """解析LLM响应为决策"""
        # 简单解析逻辑，实际可能需要更复杂的解析
        lines = response.strip().split("\n")
        content = response.strip()
        
        # 检查是否包含心理活动标记
        mental_activity = None
        if "[思考]" in content:
            parts = content.split("[思考]")
            content = parts[0].strip()
            mental_activity = parts[1].split("[/思考]")[0].strip() if "[/思考]" in parts[1] else parts[1].strip()
        
        return AIDecision(
            decision_type=DecisionType.SPEAK,
            content=content,
            mental_activity=mental_activity,
            confidence=0.8,
            reasoning=""
        )
    
    async def validate_response(
        self,
        content: str,
        context: DecisionContext
    ) -> bool:
        """验证响应是否满足规则"""
        # 调用规则引擎检查
        check_result = await self.rule_engine.check_rules(
            session_id=context.session_id,
            context={
                "message": {"content": content},
                "participant": {"id": context.participant_id},
                "session": {"state": context.session_state}
            }
        )
        
        return len(check_result.violated_rules) == 0
```

## 三、决策策略

```python
class DecisionStrategy(ABC):
    """决策策略基类"""
    
    @abstractmethod
    async def decide(
        self,
        context: DecisionContext,
        engine: AIEngine
    ) -> AIDecision:
        """做出决策"""
        pass

class ConservativeStrategy(DecisionStrategy):
    """保守策略 - 减少发言"""
    
    async def decide(
        self,
        context: DecisionContext,
        engine: AIEngine
    ) -> AIDecision:
        # 降低发言概率
        if random.random() < 0.2:
            return AIDecision(
                decision_type=DecisionType.SKIP,
                reasoning="保守策略选择跳过"
            )
        return await engine.make_decision(context)

class AggressiveStrategy(DecisionStrategy):
    """激进策略 - 增加发言"""
    
    async def decide(
        self,
        context: DecisionContext,
        engine: AIEngine
    ) -> AIDecision:
        # 提高发言概率
        return await engine.make_decision(context)

class BalancedStrategy(DecisionStrategy):
    """平衡策略"""
    
    async def decide(
        self,
        context: DecisionContext,
        engine: AIEngine
    ) -> AIDecision:
        return await engine.make_decision(context)
```
