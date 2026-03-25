"""
NonHumanArena - AI对话系统
FastAPI 主入口
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import load_config, ensure_data_dirs
from .llm.manager import llm_manager
from .api.routes import router

# 创建应用
app = FastAPI(
    title="NonHumanArena",
    description="两个AI互相对话的系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    # 确保数据目录存在
    ensure_data_dirs()
    
    # 加载配置并初始化LLM
    config = load_config()
    if config.llm.api_key:
        await llm_manager.initialize(config.llm)
        print(f"LLM已初始化: {config.llm.model}")
    else:
        print("请先配置API Key")


@app.get("/", response_class=HTMLResponse)
async def root():
    """返回前端页面"""
    with open("src/index.html", "r", encoding="utf-8") as f:
        return f.read()


# 提供静态文件（CSS、JS）
app.mount("/css", StaticFiles(directory="src/css"), name="css")
app.mount("/js", StaticFiles(directory="src/js"), name="js")


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
