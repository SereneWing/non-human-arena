# Skill 模块服务层

## 一、技能服务接口

```python
from typing import Protocol, List, Optional, Dict, Any

class ISkillService(Protocol):
    """技能服务接口"""
    
    async def register_skill(
        self,
        participant_id: str,
        skill: Skill
    ) -> SkillInstance:
        """注册技能"""
        ...
    
    async def unregister_skill(
        self,
        participant_id: str,
        skill_id: str
    ) -> bool:
        """注销技能"""
        ...
    
    async def get_skills(
        self,
        participant_id: str
    ) -> List[SkillInstance]:
        """获取参与者技能"""
        ...
    
    async def trigger_skill(
        self,
        participant_id: str,
        skill_id: str,
        context: Dict[str, Any]
    ) -> SkillResult:
        """触发技能"""
        ...
    
    async def check_and_trigger_auto_skills(
        self,
        participant_id: str,
        context: Dict[str, Any]
    ) -> List[SkillResult]:
        """检查并触发自动技能"""
        ...
```

## 二、技能服务实现

```python
class SkillService:
    """技能服务实现"""
    
    def __init__(
        self,
        event_bus: IEventBus,
        llm_client: ILLMClient,
        skill_repository: ISkillRepository
    ):
        self.event_bus = event_bus
        self.llm_client = llm_client
        self.repository = skill_repository
        self._active_skills: Dict[str, Dict[str, SkillInstance]] = {}  # participant_id -> skill_id -> instance
        self._skill_handlers: Dict[str, callable] = {}
        self._setup_event_handlers()
    
    def _setup_event_handlers(self) -> None:
        """设置事件处理器"""
        self.event_bus.subscribe(EventType.MESSAGE_RECEIVED, self._on_message_received)
    
    async def register_skill(
        self,
        participant_id: str,
        skill: Skill
    ) -> SkillInstance:
        """注册技能"""
        if participant_id not in self._active_skills:
            self._active_skills[participant_id] = {}
        
        instance = SkillInstance(
            skill=skill,
            participant_id=participant_id,
            session_id=""
        )
        
        self._active_skills[participant_id][skill.id] = instance
        
        # 发布技能注册事件
        await self.event_bus.publish(Event(
            type=EventType.SKILL_TRIGGERED,
            source="skill_service",
            data={
                "action": "registered",
                "participant_id": participant_id,
                "skill_id": skill.id
            }
        ))
        
        return instance
    
    async def trigger_skill(
        self,
        participant_id: str,
        skill_id: str,
        context: Dict[str, Any]
    ) -> SkillResult:
        """触发技能"""
        start_time = time.time()
        
        instance = self._active_skills.get(participant_id, {}).get(skill_id)
        if not instance or not instance.can_use():
            return SkillResult(
                success=False,
                skill_id=skill_id,
                error="Skill not available or on cooldown"
            )
        
        try:
            # 执行技能
            result = await self._execute_skill(instance, context)
            instance.use()
            
            # 发布技能结果事件
            await self.event_bus.publish(Event(
                type=EventType.SKILL_RESULT,
                source="skill_service",
                data={
                    "participant_id": participant_id,
                    "skill_id": skill_id,
                    "success": result.success
                }
            ))
            
            return result
            
        except Exception as e:
            return SkillResult(
                success=False,
                skill_id=skill_id,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _execute_skill(
        self,
        instance: SkillInstance,
        context: Dict[str, Any]
    ) -> SkillResult:
        """执行技能"""
        skill = instance.skill
        
        # 根据技能类型执行
        if skill.skill_type == SkillType.SPEECH:
            return await self._execute_speech_skill(instance, context)
        elif skill.skill_type == SkillType.LOGIC:
            return await self._execute_logic_skill(instance, context)
        elif skill.skill_type == SkillType.EMOTION:
            return await self._execute_emotion_skill(instance, context)
        else:
            return await self._execute_generic_skill(instance, context)
    
    async def _execute_speech_skill(
        self,
        instance: SkillInstance,
        context: Dict[str, Any]
    ) -> SkillResult:
        """执行发言技能"""
        skill = instance.skill
        
        # 构建提示词
        prompt = skill.prompt_template.format(**context)
        
        # 调用LLM
        response = await self.llm_client.complete(prompt)
        
        return SkillResult(
            success=True,
            skill_id=skill.id,
            output=response
        )
    
    async def _execute_logic_skill(
        self,
        instance: SkillInstance,
        context: Dict[str, Any]
    ) -> SkillResult:
        """执行逻辑技能"""
        # 逻辑分析实现
        return SkillResult(
            success=True,
            skill_id=instance.skill.id,
            output=""
        )
    
    async def _execute_emotion_skill(
        self,
        instance: SkillInstance,
        context: Dict[str, Any]
    ) -> SkillResult:
        """执行情感技能"""
        # 情感分析实现
        return SkillResult(
            success=True,
            skill_id=instance.skill.id,
            output=""
        )
    
    async def _execute_generic_skill(
        self,
        instance: SkillInstance,
        context: Dict[str, Any]
    ) -> SkillResult:
        """执行通用技能"""
        return SkillResult(
            success=True,
            skill_id=instance.skill.id,
            output=""
        )
    
    async def check_and_trigger_auto_skills(
        self,
        participant_id: str,
        context: Dict[str, Any]
    ) -> List[SkillResult]:
        """检查并触发自动技能"""
        results = []
        
        skills = self._active_skills.get(participant_id, {})
        for skill_id, instance in skills.items():
            if (instance.skill.trigger == SkillTrigger.AUTO and 
                instance.can_use() and
                self._check_condition(instance.skill, context)):
                
                result = await self.trigger_skill(participant_id, skill_id, context)
                results.append(result)
        
        return results
    
    def _check_condition(
        self,
        skill: Skill,
        context: Dict[str, Any]
    ) -> bool:
        """检查触发条件"""
        # 简单条件检查实现
        return True
```

## 三、技能仓储

```python
class SkillRepository:
    """技能仓储"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def save(self, skill: Skill) -> None:
        """保存技能"""
        await self.db.skills.update_one(
            {"_id": skill.id},
            {"$set": skill.__dict__},
            upsert=True
        )
    
    async def find_by_id(self, skill_id: str) -> Optional[Skill]:
        """根据ID查找"""
        doc = await self.db.skills.find_one({"_id": skill_id})
        if doc:
            return Skill(**doc)
        return None
    
    async def find_by_type(self, skill_type: SkillType) -> List[Skill]:
        """根据类型查找"""
        docs = await self.db.skills.find({"skill_type": skill_type.value}).to_list(100)
        return [Skill(**doc) for doc in docs]
    
    async def find_by_participant(self, participant_id: str) -> List[Skill]:
        """根据参与者查找"""
        docs = await self.db.participant_skills.find(
            {"participant_id": participant_id}
        ).to_list(100)
        return [Skill(**doc) for doc in docs]
```
