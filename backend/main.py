from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from starlette.middleware.cors import CORSMiddleware

# 导入我们在core.py中写好的AI引擎
from core import ai_engine

app = FastAPI(title="敏宝无忧 API",version="1.0.0")

#配置允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],#允许所有来源
    allow_credentials=True,
    allow_methods=["*"],#允许所有方法
    allow_headers=["*"],#允许所有Header
)
# --- =定义数据模型(Pydantic) ---
# 这相当于定义了前端必须要传给后端的数据格式
class ChatRequest(BaseModel):
    question: str #必须包含 question字段，且是字符串

class ChatResponse(BaseModel):
    answer: str

# --- 业务接口 ---
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    对话接口
    输入: {"question": "纽康特怎么喝？"}
    输出: {"answer": "..."}
    """

    if not request.question.strip():
        raise HTTPException(status_code=400,detail="问题不能为空")

    #调用 AI 引擎的核心逻辑
    answer_text = ai_engine.chat(request.question)
    return ChatResponse(answer=answer_text)

@app.post("/api/v1/rebuild")
async def rebuild_endpoint():
    """
    【管理员】重建知识库接口
    """
    result = ai_engine.rebuild_knowledge_base()
    return result

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ArgyAgent"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000,reload=True)

