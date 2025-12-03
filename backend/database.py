from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

#定义数据库文件路径（放在项目根目录）
#../chat_history.db
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chat_history.db')
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"

#创建引擎
#check_same_thread=False 是SQLite 在 FastAPI 多线程环境下的必须配置
engine = create_engine(
    SQLALCHEMY_DATABASE_URI,connect_args={"check_same_thread":False}
)

#创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#声明基类（所有模型都要继承它）
Base = declarative_base()

#依赖项（Dependency）:用于在 API 中获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()