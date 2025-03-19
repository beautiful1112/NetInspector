# utils/logger.py
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
import yaml

def load_settings():
    """Load settings from YAML file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    settings_file = os.path.join(project_root, "utils", "settings.yaml")
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        # 如果无法加载设置，使用默认值
        return {
            'logging': {
                'log_dir': 'logs',
                'log_level': 'DEBUG',
                'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'enable_console': True
            },
            'langchain': {
                'debug': True,
                'verbose': True
            },
            'directories': {
                'raw_configs': 'output/raw_configs',
                'reports': 'output/reports'
            }
        }

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    settings = load_settings()
    
    # 直接从 logging 配置中获取值
    log_dir = settings['logging']['log_dir']
    log_level = settings['logging']['log_level']
    log_format = settings['logging']['log_format']
    enable_console = settings['logging'].get('enable_console', True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Ensure log directory exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    log_dir = os.path.join(project_root, log_dir)
    os.makedirs(log_dir, exist_ok=True)

    # 防止重复添加 handlers
    if not logger.handlers:
        # Create file handler
        log_file = os.path.join(log_dir, f"{name}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Add console handler if enabled
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    return logger