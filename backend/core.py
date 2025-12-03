import os
# ✅ 正确的写法
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv

# --- 配置 ---
#os.environ["OPENAI_API_KEY"] = "sk-i0HXYWyGQZ6v5VKdoM0alDBvTpPD8GxVHja1ex6rR0lfP29G"
#os.environ["OPENAI_API_BASE"] = "https://api.openai-proxy.org/v1"
#os.environ["HF_ENDPOINT"] = "https://hf-mirror.com" # 国内镜像
#API_KEY=os.getenv("OPENAI_API_KEY")
#API_BASE=os.getenv("OPENAI_API_BASE")
load_dotenv(find_dotenv(),override=True)
HF_ENDPOINT=os.getenv("HF_ENDPOINT")

INDEX_PATH = "faiss_index_store"
DATA_PATH = "../data"#注意：相对于 backend文件夹，data在上一级
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME")

class AllergyAgentAI:
    def __init__(self):
        """初始化时加载本地模型"""
        print(f"[AI Core] 正在加载本地模型: {LOCAL_MODEL_NAME} ...")
        try:
            self.embeddings = HuggingFaceEmbeddings(
            model_name=LOCAL_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            self.embeddings = None
        self.vectorstore = None
        self.load_vector_store()#尝试加载已有索引

    def load_vector_store(self):
        """尝试从硬盘加载索引"""
        if os.path.exists(INDEX_PATH):
            try:
                self.vectorstore = FAISS.load_local(
                    INDEX_PATH,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print("[AI Core] 成功加载本地知识库索引")
            except Exception as e:
                print("[AI Core] 加载索引失败: {e}")
        else:
            print("[AI Core] 未找到本地索引，请先执行重建知识库")

    def rebuild_knowledge_base(self):
        """重建知识库(ETL 流程)"""
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)
            return {"status":"error","message":f"未找到数据目录{DATA_PATH}"}

        #1.读取
        loader = DirectoryLoader(DATA_PATH,glob="**/*.txt",loader_cls=TextLoader,loader_kwargs={"encoding": "utf-8"})
        docs = loader.load()
        if not docs:
            return {"status":"warning","message":"数据目录为空"}

        #2.切分
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400,chunk_overlap=50)
        splits = text_splitter.split_documents(docs)

        #3.向量化并保存
        try:
            self.vectorstore = FAISS.from_documents(splits,self.embeddings)
            self.vectorstore.save_local(INDEX_PATH)
            return {"status":"success","message":f"知识库构建成功，收录{len(splits)}条片段"}
        except Exception as e:
            return {"status":"error","message":str(e)}

    def chat(self,question: str):
        """问答核心逻辑"""
        if not self.vectorstore:
            return "知识库尚未建立，请联系管理员重建知识库。"

        #检索
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})

        #生成
        llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.2)

        template = """
                你是一位儿科过敏专科营养师“敏宝守护者”。
                【参考资料】：
                {context}

                家长的问题：{question}

                请温柔、专业地回答。如果资料里没有，请直说不知道。
                """
        prompt = ChatPromptTemplate.from_template(template)

        def format_docs(docs):
            return "\n\n".join(d.page_content for d in docs)

        chain = (
            {"context":retriever | format_docs,"question":RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return chain.invoke(question)


#创建一个全局案例，方便main.py调用
ai_engine = AllergyAgentAI()