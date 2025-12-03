import os
import sys
import platform
from importlib.util import find_spec


# --- 颜色输出工具 ---
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'


def print_ok(msg): print(f"{Colors.GREEN}[OK] {msg}{Colors.RESET}")


def print_err(msg): print(f"{Colors.RED}[ERROR] {msg}{Colors.RESET}")


def print_warn(msg): print(f"{Colors.YELLOW}[WARN] {msg}{Colors.RESET}")


def check_file_exists(path, description):
    if os.path.exists(path):
        print_ok(f"找到文件/目录: {path} ({description})")
        return True
    else:
        print_err(f"缺失文件/目录: {path} ({description})")
        return False


def check_module(module_name):
    if find_spec(module_name):
        print_ok(f"依赖库已安装: {module_name}")
        return True
    else:
        print_err(f"缺少依赖库: {module_name} (请运行 pip install {module_name})")
        return False


# ==========================================
# 1. 基础环境检查
# ==========================================
print("\n🔍 --- 1. 基础环境检查 ---")
print(f"当前工作目录: {os.getcwd()}")
print(f"Python 版本: {sys.version.split()[0]}")
print(f"操作系统: {platform.system()} {platform.release()}")

# ==========================================
# 2. 文件结构检查
# ==========================================
print("\n🔍 --- 2. 目录结构检查 ---")
required_files = [
    (".env", "配置文件"),
    ("data", "知识库目录"),
    ("backend", "后端代码目录"),
    ("backend/main.py", "后端入口"),
    ("backend/core.py", "核心逻辑"),
    ("backend/database.py", "数据库连接"),
    ("backend/models.py", "数据模型"),
    ("backend/routers", "路由目录"),
    ("backend/routers/admin.py", "管理接口"),
    ("backend/routers/__init__.py", "路由包标识 (双下划线)"),
]

all_files_exist = True
for path, desc in required_files:
    if not check_file_exists(path, desc):
        all_files_exist = False

if not all_files_exist:
    print_warn("⚠️ 部分关键文件缺失，请参考文档补充。")

# ==========================================
# 3. 环境变量与配置检查
# ==========================================
print("\n🔍 --- 3. 配置检查 (.env) ---")
try:
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.startswith("sk-"):
        print_ok("API Key 格式看起来正确")
    else:
        print_err("API Key 未找到或格式错误 (请检查 .env)")

    if os.getenv("HF_ENDPOINT"):
        print_ok("HF_ENDPOINT 已配置 (国内加速生效)")
    else:
        print_warn("未配置 HF_ENDPOINT，下载模型可能会慢")

except ImportError:
    print_err("缺少 python-dotenv 库，无法读取配置")

# ==========================================
# 4. 代码导入测试 (模拟启动)
# ==========================================
print("\n🔍 --- 4. 模拟导入测试 ---")
# 将 backend 加入路径，模拟在 backend 目录下运行
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

try:
    print("正在尝试导入 backend.main...")
    import backend.main

    print_ok("main.py 导入成功 (无语法错误)")
except ImportError as e:
    print_err(f"main.py 导入失败: {e}")
    print_warn("👉 提示：如果报错 'No module named backend'，请确保你在 backend 目录下运行 uvicorn")
except Exception as e:
    print_err(f"main.py 代码有错误: {e}")

try:
    print("正在尝试导入 backend.core...")
    import backend.core

    print_ok("core.py 导入成功")
except Exception as e:
    print_err(f"core.py 导入失败: {e}")

# ==========================================
# 总结
# ==========================================
print("\n📋 --- 诊断结束 ---")
