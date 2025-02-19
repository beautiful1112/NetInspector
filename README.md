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

### Key Features
- 🤖 Automated device inspection
- 💾 Configuration backup and management
- 📊 Performance monitoring and analysis
- 🛡️ Security policy inspection and analysis
- 🧠 AI-powered configuration analysis
- 📝 Automated report generation
- 🔄 Real-time monitoring and alerts
- 🔍 Deep security inspection

### Installation
1. Clone the repository
```bash
git clone <repository_url>
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
3. Install dependencies
```bash
pip install -r requirements.txt
```

### Quick Start
1. Set up your device information
```python
# config.yaml
devices:
  - name: "USG-1"
    host: "192.168.1.1"
    type: "huawei_usg"
```

2. Run the inspection script
```bash
python inspection/huawei/usg12004_inspection.py
```

### Project Structure
```
NetInspector/
├── connect/                 # Connection handling
│   └── device_connector.py
├── inspection/             # Inspection modules
│   └── huawei/
│       └── usg12004_inspection.py
├── output/                 # Output directory
│   ├── raw_configs/       # Raw configuration files
│   └── reports/           # Analysis reports
├── utils/                  # Utility functions
│   ├── config_loader.py
│   ├── logger.py
│   └── settings.py
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation
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

### 核心功能
- 🤖 自动化设备巡检
- 💾 配置备份与管理
- 📊 性能监控与分析
- 🛡️ 安全策略检查与分析
- 🧠 AI驱动的配置分析
- 📝 自动化报告生成
- 🔄 实时监控和告警
- 🔍 深度安全检查

### 安装方法
1. 克隆仓库
```bash
git clone <repository_url>
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
3. 安装依赖
```bash
pip install -r requirements.txt
```

### 快速开始
1. 设置设备信息
```python
# config.yaml
devices:
  - name: "USG-1"
    host: "192.168.1.1"
    type: "huawei_usg"
```

2. 运行巡检脚本
```bash
python inspection/huawei/usg12004_inspection.py
```

### 项目结构
```
NetInspector/
├── connect/                 # 连接处理
│   └── device_connector.py
├── inspection/             # 巡检模块
│   └── huawei/
│       └── usg12004_inspection.py
├── output/                 # 输出目录
│   ├── raw_configs/       # 原始配置文件
│   └── reports/           # 分析报告
├── utils/                  # 工具函数
│   ├── config_loader.py
│   ├── logger.py
│   └── settings.py
├── requirements.txt        # 项目依赖
└── README.md              # 项目文档
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
