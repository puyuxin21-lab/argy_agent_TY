from sqlalchemy import Column, Integer, String,DateTime,Text
from database import Base
from datetime import datetime

class ChatLog(Base):
    """聊天记录表"""
    __tablename__ = 'chat_log'

    id = Column(Integer, primary_key=True,index=True)#主键
    session_id = Column(String,index=True,nullable=True)#会话ID（暂留空，未来做多轮对话使用）
    user_question = Column(Text,nullable=False)#用户的问题
    ai_answer = Column(Text,nullable=False)#AI的回答
    created_at = Column(DateTime,default=datetime.now)#提问时间

class User(Base):
    """后台管理员表"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True,index=True)
    username = Column(String,unique=True,index=True)
    hashed_password = Column(String)#注意：实际生产中要存哈希值，不能存明文
    role = Column(String,default="admin")