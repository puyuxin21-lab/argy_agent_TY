import os
# ✅ 正确的写法
from langchain_community.document_loaders import DirectoryLoader, TextLoader,PyPDFLoader
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
        """初始化"""
        #默认LLM配置（存放在内存中）
        self.current_llm_model = "gpt-3.5-turbo"
        self.current_llm_temperature = 0.2

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

    #更新配置的方法
    def update_llm_config(self,model: str = None,temperature: float = None):
        if model:
            self.current_llm_model = model
        if temperature is not None:
            #限制温度范围 0.0 - 2.0
            self.current_llm_temperature = max(0.0,min(2.0,temperature))
        print(f"[Config] 配置已更新：Model={self.current_llm_model},Temp={self.current_llm_temperature}")
        return self.get_llm_config()

    #获取当前配置
    def get_llm_config(self):
        return {
            "model":self.current_llm_model,
            "temperature":self.current_llm_temperature
        }

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
        """重建知识库(ETL 流程 支持TXT和PDF)"""
        print(f"[AI Core] 重建中... 读取目录：{os.path.abspath(DATA_PATH)}")

        if not self.embeddings:
            return {"status":"error","message":"模型未加载"}

        if not os.path.exists(DATA_PATH):
            try:
                os.makedirs(DATA_PATH)
            except:
                return {"status":"error","message":"创建data文件夹失败"}

        docs = []

        #遍历目录，区分处理不同格式的文件
        try:
            for filename in os.listdir(DATA_PATH):
                file_path = os.path.join(DATA_PATH, filename)

                if filename.lower().endswith(".txt"):
                    #加载TXT
                    loader = TextLoader(file_path,encoding="utf-8")
                    docs.extend(loader.load())

                elif filename.lower().endswith(".pdf"):
                    #加载PDF
                    loader = PyPDFLoader(file_path)
                    docs.extend(loader.load())
        except Exception as e:
            return {"status":"error","message":f"文件读取失败{e}"}

        if not docs:
            return {"status":"warning","message":"data 目录没有可识别的文件 ( .txt/.pdf)"}

        #2.切分 （pdf通常内容较多，Chunk Size 保持400比较合适）
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
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})

        #生成
        llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.1)

        template = """
                你是一个严格且专业的知识库问答助手，名叫“敏宝守护者”。
            
                🔴 严禁事项：
                1. **严禁**使用你的训练数据（通用常识）来回答问题。
                2. **必须且只能**基于下方的【参考资料】进行回答。
                3. 如果【参考资料】中没有包含问题的答案，请直接回复：“抱歉，我的本地知识库中暂时没有关于这个问题的记录。”，不要编造。
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