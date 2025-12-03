🛡️ 敏宝守护者 Pro (AllergyGuard Pro) - 开发文档

1. 项目概述

本项目是一个基于 RAG (检索增强生成) 架构的垂直领域 AI 智能问答系统，采用 前后端分离 架构。

后端：Python FastAPI + LangChain + FAISS (本地向量库)。

前端：(待开发) Vue/React 或 微信小程序。

部署：支持 Windows/Linux 跨平台运行。

2. 核心技术栈

模块

技术选型

说明

API 框架

FastAPI

高性能异步框架，自动生成 Swagger 文档。

RAG 引擎

LangChain

负责文档加载、切分、检索链的编排。

向量库

FAISS (CPU版)

本地文件存储，无需安装数据库，彻底解决 Windows 闪退问题。

Embedding

text2vec

本地运行的中文嵌入模型，零成本，数据隐私高。

LLM

OpenAI (GPT-3.5)

云端推理，保证回答的逻辑性和共情能力。

配置管理

python-dotenv

使用 .env 文件管理敏感密钥，安全规范。

3. 目录结构

AllergyGuard_Pro/
├── .env                    # [配置文件] 存放 API_KEY 和模型配置 (勿上传 GitHub)
├── data/                   # [知识库] 存放 .txt 业务文档
├── faiss_index_store/      # [索引文件] 程序自动生成的向量数据库
├── backend/                # [后端代码]
│   ├── main.py             # API 入口
│   ├── core.py             # AI 核心逻辑类
│   ├── requirements.txt    # 依赖清单
│   └── venv/               # 虚拟环境
└── Project_Document.md     # 项目文档


4. 快速启动 (Windows)

4.1 环境初始化

进入 backend 目录：

cd backend


创建虚拟环境：

python -m venv venv


激活环境并安装依赖：

.\venv\Scripts\activate
pip install -r requirements.txt -i [https://pypi.tuna.tsinghua.edu.cn/simple](https://pypi.tuna.tsinghua.edu.cn/simple)
# ⚠️ 关键：强制重装 torch CPU 版以防 DLL 报错
pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cpu](https://download.pytorch.org/whl/cpu)


4.2 启动服务

在 backend 目录下运行：

# 使用模块方式启动 uvicorn，避免路径问题
python -m uvicorn main:app --reload


4.3 接口测试

打开浏览器访问：http://127.0.0.1:8000/docs

第一步：调用 /api/v1/rebuild 接口初始化知识库。

第二步：调用 /api/v1/chat 接口进行对话测试。

5. API 接口说明

5.1 重建知识库

URL: /api/v1/rebuild

Method: POST

描述: 扫描 data/ 目录下的所有 txt 文件，重新切分并向量化，保存到磁盘。

Response:

{
  "status": "success",
  "message": "✅ 知识库重建成功，共收录 12 条片段"
}


5.2 智能问答

URL: /api/v1/chat

Method: POST

Request:

{
  "question": "纽康特适合什么宝宝？"
}


Response:

{
  "answer": "您好呀！纽康特是一款专门为..."
}


6. 后续规划 (Roadmap)

前端开发：使用 Vue3 + ElementPlus 搭建管理后台。

多轮对话：在 API 中增加 history 字段，支持上下文记忆。

流式输出：升级接口为 SSE (Server-Sent Events) 流式响应，提升用户体验。