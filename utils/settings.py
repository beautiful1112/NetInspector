# settings.py

# 日志配置
# utils/settings.py
import os

# 获取当前文件的目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录 (当前目录的父目录)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 构建输出目录的完整路径
OUTPUT_DIRS = {
    'raw_configs': os.path.join(BASE_DIR, 'output', 'raw_configs'),
    'reports': os.path.join(BASE_DIR, 'output', 'reports')
}

# 确保输出目录存在
for dir_path in OUTPUT_DIRS.values():
    os.makedirs(dir_path, exist_ok=True)


# 设备连接配置
CONNECT_TIMEOUT = 60
COMMAND_TIMEOUT = 120
RETRY_TIMES = 3
RETRY_INTERVAL = 10

# 终端输出配置
ENABLE_CONSOLE_OUTPUT = True

# LangChain配置
LANGCHAIN_VERBOSE = True
LANGCHAIN_DEBUG = False

# OpenAI配置

# AI API 配置
AI_SETTINGS = {
    'deepseek': {
        'api_base': 'your-api-base',
        'api_key': 'your-api-key',
        'model': 'your-model'
    }
}

# 日志配置
LOG_SETTINGS = {
    'log_dir': 'logs',
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# 输出目录配置
OUTPUT_DIRS = {
    'raw_configs': 'raw_configs',
    'reports': 'reports'
}


