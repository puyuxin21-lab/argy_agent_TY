from fastapi import APIRouter,UploadFile,File,HTTPException,Depends,Query
from sqlalchemy.orm import Session
import shutil
import os
from typing import List
#引入核心模块
from database import get_db
import models
from core import ai_engine,DATA_PATH

#创建路由实例
router = APIRouter(
    prefix="/api/v1/admin",
    tags=["管理后台(Admin)"]
)

# --- 1. 知识库文件管理 ---

@router.get("/files")
async def list_files():
    """查看当前知识库中的文件列表"""
    if not os.path.isdir(DATA_PATH):
        return []
    files = [f for f in os.listdir(DATA_PATH) if f.endswith('.txt')]
    return {"files": files,"count":len(files)}

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    """上传新的知识文档"""
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400,detail="仅支持 .txt 格式文件")

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

