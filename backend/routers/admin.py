from fastapi import APIRouter,UploadFile,File,HTTPException,Depends,Query
from openai import BaseModel
from sqlalchemy.orm import Session
import shutil
import os
from typing import List, Optional
#引入核心模块
from database import get_db
import models
from core import ai_engine,DATA_PATH

#创建路由实例
router = APIRouter(
    prefix="/api/v1/admin",
    tags=["管理后台(Admin)"]
)

# --- 0.系统配置管理（新增） ---
class ConfigUpdate(BaseModel):
    model: Optional[str] = None
    temperature: Optional[float] = None

@router.get("/config")
async def get_system_config():
    """查看当前AI模型"""
    return ai_engine.get_llm_config()

@router.post("/config")
async def update_system_config(config: ConfigUpdate):
    """
    修改AI模型配置
    model:例如"gpt-3.5_turbo","gpt-4.1-mini"
    temperature:0.0 - 2.0(越低越严谨)
    """
    new_config = ai_engine.update_llm_config(
        model=config.model,
        temperature=config.temperature
    )
    return {"message":"配置更新成功","config":new_config}
# --- 1. 知识库文件管理 ---

@router.get("/files")
async def list_files():
    """查看当前知识库中的文件列表"""
    if not os.path.isdir(DATA_PATH):
        return []
    #支持显示 txt和pdf
    valid_exts = ('.txt','.pdf')
    files = [f for f in os.listdir(DATA_PATH) if f.endswith(valid_exts)]
    return {"files": files,"count":len(files)}

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    """上传新的知识文档(.txt/.pdf)"""
    if not file.filename.endswith(('.txt',".pdf")):
        raise HTTPException(status_code=400,detail="仅支持 .txt 或 .pdf格式文件")

    #确保目录存在
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    file_location = os.path.join(DATA_PATH, file.filename)

    #保存文件到 data 目录
    try:
        with open(file_location,"wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"文件保存失败：{e}")

    return {"message":f"文件 ‘{file.filename}' 上传成功","path":file_location}

@router.delete("/files/{file.filename}")
async def delete(filename: str):
    """删除指定文件"""
    file_path = os.path.join(DATA_PATH, filename)
    # 🔍 调试打印：看看程序到底去哪找文件了
    print(f"🔍 [Debug] 尝试删除文件: {filename}")
    print(f"📂 [Debug] 完整路径是: {os.path.abspath(file_path)}")
    print(f"❓ [Debug] 文件存在吗? {os.path.exists(file_path)}")
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404,detail="文件不存在")

    try:
        os.remove(file_path)
        return {"message": f"文件 '{filename}' 已删除"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"删除失败：{e}")

# --- 2.知识库操作 ---
@router.post("/rebuild")
async def rebuild():
    """触发知识库重建（上传/删除文件后需要调用此接口生效）"""
    result = ai_engine.rebuild_knowledge_base()
    return result

# --- 3.数据审计 ---

@router.get("/logs")
async def get_chat_logs(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1,le=100),
        db: Session = Depends(get_db),
):
    """
    分页查看聊天日志
    :param page: 页码（从1开始）
    :param size: 每页条数
    """
    offset = (page - 1) * size
    logs = db.query(models.ChatLog)\
             .order_by(models.ChatLog.created_at.desc())\
             .offset(offset)\
             .limit(size)\
             .all()

    total = db.query(models.ChatLog) .count()

    return {
        "total": total,
        "page": page,
        "size": size,
        "logs": logs
    }

