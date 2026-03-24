# LLM 模块 API 路由

## 一、LLM 提供商管理

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/llm", tags=["LLM"])

# ==================== 提供商配置 ====================

@router.get("/providers", response_model=List[ProviderResponse])
async def list_providers(
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """列出可用的LLM提供商"""
    providers = await llm_service.list_providers()
    return providers

@router.get("/providers/{provider_name}", response_model=ProviderResponse)
async def get_provider(
    provider_name: str,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """获取提供商详情"""
    provider = await llm_service.get_provider(provider_name)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提供商不存在"
        )
    return provider

@router.post("/providers/", response_model=ProviderResponse)
async def create_provider(
    data: CreateProviderRequest,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """创建提供商配置"""
    try:
        provider = await llm_service.create_provider(data)
        return provider
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/providers/{provider_name}", response_model=ProviderResponse)
async def update_provider(
    provider_name: str,
    data: UpdateProviderRequest,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """更新提供商配置"""
    provider = await llm_service.update_provider(provider_name, data)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提供商不存在"
        )
    return provider

@router.delete("/providers/{provider_name}")
async def delete_provider(
    provider_name: str,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """删除提供商配置"""
    success = await llm_service.delete_provider(provider_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提供商不存在"
        )
    return {"success": True}

@router.post("/providers/{provider_name}/test")
async def test_provider(
    provider_name: str,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """测试提供商连接"""
    try:
        result = await llm_service.test_provider(provider_name)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"测试失败: {str(e)}"
        )

# ==================== 模型配置 ====================

@router.get("/models", response_model=List[ModelResponse])
async def list_models(
    provider_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """列出可用的模型"""
    if provider_name:
        models = await llm_service.get_models_by_provider(provider_name)
    else:
        models = await llm_service.list_models()
    return models

@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """获取模型详情"""
    model = await llm_service.get_model(model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在"
        )
    return model

# ==================== LLM 调用 ====================

@router.post("/chat", response_model=ChatResponse)
async def chat(
    messages: List[MessageRequest],
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    stream: bool = False,
    current_user: User = Depends(get_current_user),
    llm_client: LLMClient = Depends(get_llm_client)
):
    """发送聊天请求"""
    try:
        if stream:
            return StreamingResponse(
                llm_client.chat_stream(messages, model, temperature, max_tokens),
                media_type="text/event-stream"
            )
        
        response = await llm_client.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        )
        return response
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM调用失败: {str(e)}"
        )

@router.post("/embeddings", response_model=EmbeddingResponse)
async def get_embeddings(
    texts: List[str],
    model: str = "text-embedding-ada-002",
    current_user: User = Depends(get_current_user),
    llm_client: LLMClient = Depends(get_llm_client)
):
    """获取文本嵌入"""
    try:
        embeddings = await llm_client.get_embeddings(texts, model)
        return {"embeddings": embeddings}
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"嵌入生成失败: {str(e)}"
        )

@router.post("/complete", response_model=CompletionResponse)
async def complete(
    prompt: str,
    model: str = "gpt-3.5-turbo-instruct",
    temperature: float = 0.7,
    max_tokens: int = 256,
    current_user: User = Depends(get_current_user),
    llm_client: LLMClient = Depends(get_llm_client)
):
    """补全请求"""
    try:
        response = await llm_client.complete(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"补全失败: {str(e)}"
        )

# ==================== 使用统计 ====================

@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    provider_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """获取使用统计"""
    usage = await llm_service.get_usage_stats(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        provider_name=provider_name
    )
    return usage

@router.get("/usage/cost")
async def get_cost(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """获取费用统计"""
    cost = await llm_service.get_cost_stats(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    return cost

# ==================== 请求/响应模型 ====================

from pydantic import BaseModel, Field

class ProviderConfig(BaseModel):
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    organization: Optional[str] = None
    timeout: int = 60
    max_retries: int = 3

class CreateProviderRequest(BaseModel):
    name: str
    provider_type: str  # openai, anthropic, local, etc.
    config: ProviderConfig
    enabled: bool = True
    priority: int = 0

class UpdateProviderRequest(BaseModel):
    config: Optional[ProviderConfig] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None

class ModelConfig(BaseModel):
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None

class MessageRequest(BaseModel):
    role: str  # system, user, assistant
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageRequest]
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False

class ChatResponse(BaseModel):
    id: str
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    created: int

class EmbeddingRequest(BaseModel):
    texts: List[str]
    model: str = "text-embedding-ada-002"

class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    usage: Dict[str, int]

class CompletionRequest(BaseModel):
    prompt: str
    model: str = "gpt-3.5-turbo-instruct"
    temperature: float = 0.7
    max_tokens: int = 256

class CompletionResponse(BaseModel):
    id: str
    model: str
    text: str
    usage: Dict[str, int]
    created: int

class ProviderResponse(BaseModel):
    name: str
    provider_type: str
    config: Dict[str, Any]  # 不包含敏感信息
    enabled: bool
    priority: int
    models: List[str]

    class Config:
        from_attributes = True

class ModelResponse(BaseModel):
    id: str
    name: str
    provider: str
    capabilities: List[str]
    max_tokens: int
    default_temperature: float

    class Config:
        from_attributes = True

class UsageStats(BaseModel):
    total_requests: int
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    by_model: Dict[str, Dict[str, int]]

class CostStats(BaseModel):
    total_cost: float
    by_provider: Dict[str, float]
    by_model: Dict[str, float]

class UsageResponse(BaseModel):
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    stats: UsageStats
```
