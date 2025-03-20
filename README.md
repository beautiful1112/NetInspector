# NetInspector | 网眼

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> AI-Powered Network Automation Tool | AI网络自动化工具

NetInspector 是一个智能网络自动化工具，集成了AI技术，用于网络设备巡检、配置管理和安全分析。本工具支持多种网络设备，提供自动化巡检、策略分析、智能报告等功能，帮助网络管理员提高工作效率和网络安全性。

[English](#english) | [中文](#chinese)

<a name="english"></a>
## English

### Description
NetInspector is an intelligent network automation tool designed for network device inspection and configuration management. Powered by AI technology, it currently supports Huawei USG firewalls and can be extended to support other network devices. The tool helps network administrators improve efficiency and network security through automated inspection, policy analysis, and intelligent reporting.

### AI Operations
NetInspector now includes an AI-powered network operations assistant that helps network administrators manage and monitor their network devices through natural language interactions.

#### AI Assistant Features
- 🤖 Natural Language Interface
  - Communicate with network devices using everyday language
  - Execute commands through natural language processing

- 🔍 Device Information Retrieval
  - List all available network devices
  - Get detailed interface information
  - Get IP address configurations

- 📊 Network Analysis
  - Analyze device configurations
  - Monitor interface status
  - Check connectivity issues

- 🛠️ Automated Operations
  - Execute network commands through natural language
  - Batch configuration management
  - Configuration validation

#### Example Usage
```bash
# Natural language commands examples

"List all available network devices"
"Show me the IP addresses of switch01's interfaces"
"Get detailed information about switch01's interfaces"
```

### Key Features
- 🤖 Automated device inspection
- 💾 Configuration backup and management
- 📊 Performance monitoring and analysis
- 🛡️ Security policy inspection and analysis
- 🧠 AI-powered configuration analysis
- 📝 Automated report generation
- 🔄 Real-time monitoring and alerts
- 🔍 Deep security inspection
- 🌐 Web-based management interface

### Technology Stack
#### Backend
- Python 3.12
- FastAPI
- Nornir (Network Automation Framework)
- OpenAI API Integration
- SQLite Database

#### Frontend
- React 18
- Ant Design 5.0
- Axios
- Vite

### Installation
1. Clone the repository
```bash
git clone https://github.com/beautiful1112/NetInspector.git
cd NetInspector
```

2. Configure environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

3. Install backend dependencies
```bash
pip install -r requirements.txt
```

4. Install frontend dependencies
```bash
cd frontend/netinspector-frontend
npm install
```

5. Configure settings
- Copy `utils/settings.yaml.example` to `utils/settings.yaml`
- Update AI API configuration and other necessary settings

6. Start services
```bash
# Start backend service
python -m uvicorn api.main:app --reload

# Start frontend service (new terminal)
cd frontend/netinspector-frontend
npm run dev
```

### Project Structure
```
NetInspector/
├── api/                # API implementation
├── config/             # Configuration files
├── frontend/          # Frontend code
│   └── netinspector-frontend/
├── inspection/        # Inspection logic
├── operation/        # Operation related code
├── templates/        # Template files
│   ├── commands/    # Command templates
│   └── prompts/     # AI prompts
├── utils/            # Utility functions
└── README.md
```

### Configuration
- Configure your credentials in `credential.yaml`
- Customize inspection parameters in `commands.yaml` in the templates folder
- Customize prompt messages in `prompt.yaml` in the templates folder
- Customize settings of log and API key in settings.py in the utils folder
- Customize device information in `config.yaml` in the config folder

### Output Files
- Raw device configurations: `output/raw_configs/`
- Inspection reports: `output/reports/`
- Log files: `logs/`

### Dependencies
- Python 3.8+
- Required packages listed in requirements.txt
- Network device access credentials
- Node.js 16+ (for frontend)

### Contributing
We welcome contributions! Please follow these steps:
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Support
For support and questions:
- Open an issue
- Contact: winecrazy1112@gmail.com


---

<a name="chinese"></a>
## 中文

### 描述
NetInspector（网眼）是一个集成AI技术的智能网络自动化工具，专注于网络设备巡检和配置管理。目前支持华为USG防火墙，并可扩展支持其他网络设备。该工具通过自动化巡检、策略分析和智能报告功能，帮助网络管理员提升工作效率和网络安全性。

### AI 运维
NetInspector现已包含AI驱动的网络运维助手，通过自然语言交互帮助网络管理员管理和监控网络设备。

#### AI助手功能
- 🤖 自然语言交互
  - 使用日常语言与网络设备进行交互
  - 通过自然语言处理执行命令

- 🔍 设备信息获取
  - 列出所有可用的网络设备
  - 获取详细的接口信息
  - 获取IP地址配置

- 📊 网络分析
  - 分析设备配置
  - 监控接口状态
  - 检查连接问题

- 🛠️ 自动化操作
  - 通过自然语言执行网络命令
  - 批量配置管理
  - 配置验证

#### 使用示例
```bash
# 自然语言命令示例

"列出所有可用的网络设备"
"显示switch01的所有接口IP地址"
"获取switch01的接口详细信息"
```

### 核心功能
- 🤖 自动化设备巡检
- 💾 配置备份与管理
- 📊 性能监控与分析
- 🛡️ 安全策略检查与分析
- 🧠 AI驱动的配置分析
- 📝 自动化报告生成
- 🔄 实时监控和告警
- 🔍 深度安全检查
- 🌐 Web管理界面

### 技术栈
#### 后端
- Python 3.12
- FastAPI
- Nornir (网络自动化框架)
- OpenAI API 集成
- SQLite 数据库

#### 前端
- React 18
- Ant Design 5.0
- Axios
- Vite

### 安装方法
1. 克隆仓库
```bash
git clone https://github.com/beautiful1112/NetInspector.git
cd NetInspector
```

2. 配置环境
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

3. 安装后端依赖
```bash
pip install -r requirements.txt
```

4. 安装前端依赖
```bash
cd frontend/netinspector-frontend
npm install
```

5. 配置设置
- 复制 `utils/settings.yaml.example` 到 `utils/settings.yaml`
- 更新 AI API 配置和其他必要设置

6. 启动服务
```bash
# 启动后端服务
python -m uvicorn api.main:app --reload

# 启动前端服务（新终端）
cd frontend/netinspector-frontend
npm run dev
```

### 项目结构
```
NetInspector/
├── api/                # API实现
├── config/             # 配置文件目录
├── frontend/          # 前端代码
│   └── netinspector-frontend/
├── inspection/        # 巡检逻辑
├── operation/        # 操作相关代码
├── templates/        # 模板文件
│   ├── commands/    # 命令模板
│   └── prompts/     # AI提示模板
├── utils/            # 工具函数
└── README.md
```

### 配置说明
- 在config文件夹中的`credential.yaml`中配置认证信息
- 在templates文件夹中的`commands.yaml`中自定义巡检参数
- 在templates文件夹中的`prompt.yaml`中自定义提示提示词
- 在utils文件夹中的`settings.py`中自定义日志和API密钥设置
- 在config文件夹中的`config.yaml`中自定义设备信息

### 输出文件
- 设备原始配置：`output/raw_configs/`
- 巡检报告：`output/reports/`
- 日志文件：`logs/`

### 依赖项
- Python 3.8+
- requirements.txt 中列出的必需包
- 网络设备访问凭证
- Node.js 16+ (前端开发)

### 贡献指南
我们欢迎贡献！请遵循以下步骤：
1. Fork 仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

### 许可证
本项目采用 MIT 许可证 - 详见 LICENSE 文件

### 支持
获取支持和咨询：
- 提交 Issue
- 联系方式：winecrazy1112@gmail.com
