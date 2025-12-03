from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel
import uvicorn
from sqlalchemy.orm import Session, defer
from starlette.middleware.cors import CORSMiddleware

# 导入我们在core.py中写好的AI引擎
from core import ai_engine
#引入核心逻辑和数据库模块
import models
from database import engine,get_db

# 3. 引入路由模块 (分机号)
# 注意：你需要确保 backend/routers/admin.py 文件存在，否则这里会报错
from routers import admin

#自动创建数据表
#这一步会自动在根目录生成 chat_history.db 文件
models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="敏宝无忧 API",version="1.0.0")

#配置允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],#允许所有来源
    allow_credentials=True,
    allow_methods=["*"],#允许所有方法
    allow_headers=["*"],#允许所有Header
)

# ✅ 注册路由：把管理员相关的接口挂载上来
# 访问 /api/v1/admin/... 的请求都会交给 admin.py 处理
app.include_router(admin.router)

# --- =定义数据模型(Pydantic) ---
# 这相当于定义了前端必须要传给后端的数据格式
class ChatRequest(BaseModel):
    question: str #必须包含 question字段，且是字符串

class ChatResponse(BaseModel):
    answer: str

# --- 业务接口 ---

@app.post("/")
def root():
    return {"message": "AllergyAgent Pro Backend (with SQLite) is Running! 🚀"}
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest,db: Session = Depends(get_db)):
    """
    智能对话接口(自动保存记录到数据库)
    输入: {"question": "纽康特怎么喝？"}
    输出: {"answer": "..."}
    """

    if not request.question.strip():
        raise HTTPException(status_code=400,detail="问题不能为空")

    #调用 AI 引擎的核心逻辑
    answer_text = ai_engine.chat(request.question)
    #将对话记录存入SQLite数据库
    try:
        new_log = models.ChatLog(
            user_question=request.question,
            ai_answer=answer_text
        )
        db.add(new_log)     #添加到暂存区
        db.commit()         #提交事务
        db.refresh(new_log) #刷新对象（获取生成的ID）
        print(f"[DB Log] 已保存对话记录 ID：{new_log.id}")
    except Exception as e:
        print(f"[DB ERROR] 保存日志失败：{e}")
        #注意：即使保存失败，也应该返回答案给用户，不要让用户感觉到错误

    return ChatResponse(answer=answer_text)

@app.post("/api/v1/rebuild")
async def rebuild_endpoint():
    """
    【管理员】重建知识库接口
    """
    result = ai_engine.rebuild_knowledge_base()
    return result

#--- 查看历史记录接口 ---
@app.post("/api/v1/history")
async def get_history(limit: int = 10,db: Session = Depends(get_db)):
    """获取最近的聊天记录"""
    logs = db.query(models.ChatLog).order_by(models.ChatLog.created_at.desc()).limit(limit).all()
    return logs

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ArgyAgent"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000,reload=True)

