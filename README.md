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

### Project Structure
```
NetInspector/
├── api/                # FastAPI backend implementation
│   ├── main.py        # Main API endpoints and server configuration
│   └── network_routes.py # Network-specific API routes
├── config/            # Configuration files
│   ├── hosts.yaml     # Device inventory configuration
│   ├── groups.yaml    # Device groups configuration
│   └── defaults.yaml  # Default settings for devices
├── frontend/          # React frontend application
│   └── netinspector-frontend/ # Frontend source code
├── inspection/        # Core inspection logic
│   ├── generic_inspector.py # Main inspection implementation
│   └── __init__.py
├── operation/         # Operation-related code
│   ├── ai_operator.py # AI operations implementation
│   └── __init__.py
├── templates/         # Template files
│   ├── commands/     # Command templates for different devices
│   └── prompts/      # AI prompt templates
├── utils/            # Utility functions and helpers
│   ├── settings.yaml # Application settings
│   └── logger.py     # Logging configuration
├── network/          # Network-specific implementations
├── tools/            # Utility tools and scripts
├── tests/            # Test cases and test utilities
├── output/           # Output files
│   ├── raw_configs/  # Raw device configurations
│   └── reports/      # Inspection reports
├── logs/             # Application logs
└── requirements.txt  # Python dependencies
```

#### AI Assistant Features
- 🤖 Natural Language Interface
  - Communicate with network devices using everyday language
  - Execute commands through natural language processing

#### Backend Components
1. **API Layer (`api/`)**
   - FastAPI-based REST API
   - Network device management endpoints
   - Configuration management endpoints
   - AI operation endpoints

2. **Inspection Engine (`inspection/`)**
   - Device configuration inspection
   - Security policy analysis
   - Performance monitoring
   - Report generation

3. **AI Operations (`operation/`)**
   - Natural language processing
   - AI-powered analysis
   - Automated operations
   - Intelligent recommendations

4. **Configuration Management (`config/`)**
   - Device inventory
   - Group management
   - Default settings
   - Template management

#### Frontend Components
1. **User Interface (`frontend/`)**
   - React-based web application
   - Ant Design components
   - Real-time monitoring dashboard
   - Configuration management interface

2. **Templates (`templates/`)**
   - Command templates for different devices
   - AI prompt templates
   - Report templates

### Features

#### Network Operations
- 🤖 Automated device inspection
- 💾 Configuration backup and management
- 📊 Performance monitoring and analysis
- 🛡️ Security policy inspection
- 🔄 Real-time monitoring
- 🔍 Deep security inspection

#### AI Capabilities
- 🧠 Natural language interface
- 📝 Intelligent report generation
- 🔧 Automated troubleshooting
- 📈 Smart analysis and recommendations

#### Configuration Management
- 📋 Template-based configuration
- 🔄 Batch operations
- ✅ Configuration validation
- 📦 Version control

### Technology Stack

#### Backend
- Python 3.12
- FastAPI
- Nornir (Network Automation)
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

### Configuration
- Configure device credentials in `config/credential.yaml`
- Customize inspection parameters in `templates/commands/`
- Customize AI prompts in `templates/prompts/`
- Configure application settings in `utils/settings.yaml`
- Manage device inventory in `config/hosts.yaml`

### Output and Logs
- Raw device configurations: `output/raw_configs/`
- Inspection reports: `output/reports/`
- Application logs: `logs/`

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

### 项目结构
```
NetInspector/
├── api/                # FastAPI后端实现
│   ├── main.py        # 主API端点和服务器配置
│   └── network_routes.py # 网络特定API路由
├── config/            # 配置文件
│   ├── hosts.yaml     # 设备清单配置
│   ├── groups.yaml    # 设备组配置
│   └── defaults.yaml  # 设备默认设置
├── frontend/          # React前端应用
│   └── netinspector-frontend/ # 前端源代码
├── inspection/        # 核心巡检逻辑
│   ├── generic_inspector.py # 主要巡检实现
│   └── __init__.py
├── operation/         # 操作相关代码
│   ├── ai_operator.py # AI操作实现
│   └── __init__.py
├── templates/         # 模板文件
│   ├── commands/     # 不同设备的命令模板
│   └── prompts/      # AI提示模板
├── utils/            # 工具函数和辅助程序
│   ├── settings.yaml # 应用设置
│   └── logger.py     # 日志配置
├── network/          # 网络特定实现
├── tools/            # 工具和脚本
├── tests/            # 测试用例和测试工具
├── output/           # 输出文件
│   ├── raw_configs/  # 设备原始配置
│   └── reports/      # 巡检报告
├── logs/             # 应用日志
└── requirements.txt  # Python依赖
```

### 核心组件

#### 后端组件
1. **API层 (`api/`)**
   - 基于FastAPI的REST API
   - 网络设备管理端点
   - 配置管理端点
   - AI操作端点

2. **巡检引擎 (`inspection/`)**
   - 设备配置巡检
   - 安全策略分析
   - 性能监控
   - 报告生成

3. **AI操作 (`operation/`)**
   - 自然语言处理
   - AI驱动分析
   - 自动化操作
   - 智能建议

4. **配置管理 (`config/`)**
   - 设备清单
   - 组管理
   - 默认设置
   - 模板管理

#### 前端组件
1. **用户界面 (`frontend/`)**
   - 基于React的Web应用
   - Ant Design组件
   - 实时监控仪表板
   - 配置管理界面

2. **模板 (`templates/`)**
   - 不同设备的命令模板
   - AI提示模板
   - 报告模板

### 功能特性

#### 网络操作
- 🤖 自动化设备巡检
- 💾 配置备份与管理
- 📊 性能监控与分析
- 🛡️ 安全策略检查
- 🔄 实时监控
- 🔍 深度安全检查

#### AI能力
- 🧠 自然语言界面
- 📝 智能报告生成
- 🔧 自动化故障排除
- 📈 智能分析和建议

#### 配置管理
- 📋 基于模板的配置
- 🔄 批量操作
- ✅ 配置验证
- 📦 版本控制

### 技术栈

#### 后端
- Python 3.12
- FastAPI
- Nornir (网络自动化)
- OpenAI API集成
- SQLite数据库

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

### 配置说明
- 在 `config/credential.yaml` 中配置设备认证信息
- 在 `templates/commands/` 中自定义巡检参数
- 在 `templates/prompts/` 中自定义AI提示
- 在 `utils/settings.yaml` 中配置应用设置
- 在 `config/hosts.yaml` 中管理设备清单

### 输出和日志
- 设备原始配置：`output/raw_configs/`
- 巡检报告：`output/reports/`
- 应用日志：`logs/`

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
