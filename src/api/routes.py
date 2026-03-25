"""
API路由模块
定义所有HTTP和SSE接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import uuid
import json

from ..config import load_config, save_config, AppConfig, LLMConfig
from ..llm.manager import llm_manager
from ..llm.adapter import ChatMessage
from ..agents.agent import Agent
from ..agents.conversation import Conversation, Message, conversation_manager
from ..storage.file_storage import FileStorage

# 初始化存储
from pathlib import Path
storage = FileStorage(Path(__file__).parent.parent / "data")

router = APIRouter()


# ============ 请求/响应模型 ============

class ConfigRequest(BaseModel):
    api_key: str
    model: str = "minimax-m2.7"
    base_url: str = "https://api.minimax.chat/v1"
    temperature: float = 0.7
    max_tokens: int = 100000
    auto_interval: int = 3


class AgentRequest(BaseModel):
    name: str
    personality: str
    description: str = ""


class CreateConversationRequest(BaseModel):
    agent1: AgentRequest
    agent2: AgentRequest


class SendMessageRequest(BaseModel):
    content: str
    is_user: bool = False


# ============ 配置接口 ============

@router.get("/api/config")
async def get_config():
    """获取当前配置"""
    config = load_config()
    return {
        "api_key": config.llm.api_key[:4] + "****" + config.llm.api_key[-4:] if config.llm.api_key else "",
        "api_key_set": bool(config.llm.api_key),
        "model": config.llm.model,
        "base_url": config.llm.base_url,
        "temperature": config.llm.temperature,
        "max_tokens": config.llm.max_tokens,
        "auto_interval": config.auto_interval,
        "llm_ready": llm_manager.is_initialized()
    }


@router.post("/api/config")
async def update_config(req: ConfigRequest):
    """更新配置（仅运行时生效，api_key不持久保存）"""
    config = AppConfig()
    config.llm = LLMConfig(
        api_key=req.api_key,
        model=req.model,
        base_url=req.base_url,
        temperature=req.temperature,
        max_tokens=req.max_tokens
    )
    config.auto_interval = req.auto_interval
    
    # 仅保存非敏感配置（不保存api_key）
    save_config(config)
    
    # 重新初始化LLM管理器
    await llm_manager.initialize(config.llm)
    
    return {"status": "ok", "message": "配置已更新（api_key仅在本次运行时有效）"}


# ============ 对话接口 ============

@router.post("/api/conversation")
async def create_conversation(req: CreateConversationRequest):
    """创建新对话"""
    agent1 = Agent(
        id=str(uuid.uuid4())[:8],
        name=req.agent1.name,
        personality=req.agent1.personality,
        description=req.agent1.description
    )
    agent2 = Agent(
        id=str(uuid.uuid4())[:8],
        name=req.agent2.name,
        personality=req.agent2.personality,
        description=req.agent2.description
    )
    
    conversation = conversation_manager.create_conversation(agent1, agent2)
    
    # 保存到文件
    storage.save_conversation(conversation)
    
    return conversation.to_dict()


@router.get("/api/conversation/{conv_id}")
async def get_conversation(conv_id: str):
    """获取对话详情"""
    conversation = conversation_manager.get_conversation(conv_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return conversation.to_dict()


@router.delete("/api/conversation/{conv_id}")
async def delete_conversation(conv_id: str):
    """删除对话"""
    conversation_manager.delete_conversation(conv_id)
    storage.delete_conversation(conv_id)
    return {"status": "ok"}


@router.get("/api/conversations")
async def list_conversations():
    """列出所有对话"""
    return conversation_manager.list_conversations()


# ============ 消息接口 ============

@router.post("/api/conversation/{conv_id}/message/{agent_id}")
async def send_message(conv_id: str, agent_id: str, req: SendMessageRequest):
    """发送消息"""
    conversation = conversation_manager.get_conversation(conv_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 确定是哪个agent
    if conversation.agent1.id == agent_id:
        speaker = conversation.agent1
    elif conversation.agent2.id == agent_id:
        speaker = conversation.agent2
    else:
        raise HTTPException(status_code=400, detail="无效的agent_id")
    
    # 创建消息
    message = Message(
        id=str(uuid.uuid4())[:8],
        agent_id=speaker.id,
        agent_name=speaker.name,
        content=req.content,
        is_user=req.is_user
    )
    
    conversation.add_message(message)
    
    # 保存到文件
    storage.save_conversation(conversation)
    
    return message.to_dict()


@router.post("/api/conversation/{conv_id}/generate/{agent_id}")
async def generate_response(conv_id: str, agent_id: str):
    """让AI生成回复（非流式）"""
    conversation = conversation_manager.get_conversation(conv_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 确定是哪个agent
    if conversation.agent1.id == agent_id:
        speaker = conversation.agent1
        other = conversation.agent2
    elif conversation.agent2.id == agent_id:
        speaker = conversation.agent2
        other = conversation.agent1
    else:
        raise HTTPException(status_code=400, detail="无效的agent_id")
    
    # 构建提示词
    prompt = conversation.build_prompt(speaker, other)
    
    # 调用LLM
    messages = [
        ChatMessage(role="system", content=speaker.get_system_prompt()),
        ChatMessage(role="user", content=prompt)
    ]
    
    response = await llm_manager.chat(messages)
    
    # 创建消息
    message = Message(
        id=str(uuid.uuid4())[:8],
        agent_id=speaker.id,
        agent_name=speaker.name,
        content=response.content
    )
    
    conversation.add_message(message)
    
    # 保存到文件
    storage.save_conversation(conversation)
    
    return message.to_dict()


@router.get("/api/conversation/{conv_id}/stream/{agent_id}")
async def stream_generate(conv_id: str, agent_id: str):
    """流式生成回复"""
    conversation = conversation_manager.get_conversation(conv_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 确定是哪个agent
    if conversation.agent1.id == agent_id:
        speaker = conversation.agent1
        other = conversation.agent2
    elif conversation.agent2.id == agent_id:
        speaker = conversation.agent2
        other = conversation.agent1
    else:
        raise HTTPException(status_code=400, detail="无效的agent_id")
    
    # 构建提示词
    prompt = conversation.build_prompt(speaker, other)
    
    # 调用LLM
    messages = [
        ChatMessage(role="system", content=speaker.get_system_prompt()),
        ChatMessage(role="user", content=prompt)
    ]
    
    async def event_generator():
        message_id = str(uuid.uuid4())[:8]
        full_content = ""
        
        # 先发送开始事件
        yield f"event: start\ndata: {json.dumps({'id': message_id, 'agent_id': speaker.id, 'agent_name': speaker.name})}\n\n"
        
        try:
            async for chunk in llm_manager.chat_stream(messages):
                full_content += chunk
                yield f"event: chunk\ndata: {json.dumps({'content': chunk})}\n\n"
            
            # 发送完成事件
            yield f"event: done\ndata: {json.dumps({'id': message_id, 'content': full_content})}\n\n"
            
            # 保存消息
            message = Message(
                id=message_id,
                agent_id=speaker.id,
                agent_name=speaker.name,
                content=full_content
            )
            conversation.add_message(message)
            storage.save_conversation(conversation)
            
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ============ 自动模式接口 ============

# 存储自动模式的状态
auto_mode_tasks: dict = {}


@router.post("/api/conversation/{conv_id}/auto/start")
async def start_auto_mode(conv_id: str, interval: int = 3):
    """启动自动对话模式"""
    conversation = conversation_manager.get_conversation(conv_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    if conv_id in auto_mode_tasks and not auto_mode_tasks[conv_id].done():
        raise HTTPException(status_code=400, detail="自动模式已在运行")
    
    conversation.is_auto_mode = True
    
    async def auto_generate():
        try:
            while conversation.is_auto_mode:
                # 确定当前轮到谁
                if conversation.current_turn == "agent1":
                    speaker = conversation.agent1
                    other = conversation.agent2
                else:
                    speaker = conversation.agent2
                    other = conversation.agent1
                
                # 构建提示词
                prompt = conversation.build_prompt(speaker, other)
                
                # 调用LLM
                messages = [
                    ChatMessage(role="system", content=speaker.get_system_prompt()),
                    ChatMessage(role="user", content=prompt)
                ]
                
                response = await llm_manager.chat(messages)
                
                # 创建消息
                message = Message(
                    id=str(uuid.uuid4())[:8],
                    agent_id=speaker.id,
                    agent_name=speaker.name,
                    content=response.content
                )
                
                conversation.add_message(message)
                storage.save_conversation(conversation)
                
                # 切换轮次
                conversation.current_turn = "agent2" if conversation.current_turn == "agent1" else "agent1"
                
                # 等待间隔
                await asyncio.sleep(interval)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Auto mode error: {e}")
    
    task = asyncio.create_task(auto_generate())
    auto_mode_tasks[conv_id] = task
    
    return {"status": "ok", "message": "自动模式已启动"}


@router.post("/api/conversation/{conv_id}/auto/stop")
async def stop_auto_mode(conv_id: str):
    """停止自动对话模式"""
    conversation = conversation_manager.get_conversation(conv_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    conversation.is_auto_mode = False
    
    if conv_id in auto_mode_tasks:
        auto_mode_tasks[conv_id].cancel()
        del auto_mode_tasks[conv_id]
    
    return {"status": "ok", "message": "自动模式已停止"}


@router.get("/api/conversation/{conv_id}/auto/status")
async def get_auto_status(conv_id: str):
    """获取自动模式状态"""
    is_running = conv_id in auto_mode_tasks and not auto_mode_tasks[conv_id].done()
    return {
        "is_running": is_running,
        "current_turn": conversation_manager.get_conversation(conv_id).current_turn if conversation_manager.get_conversation(conv_id) else None
    }
