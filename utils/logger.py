# utils/logger.py

import logging
import os
from datetime import datetime
from typing import Dict, Any

# 日志配置
LOG_SETTINGS: Dict[str, Any] = {
    'log_dir': 'logs',
    'log_level': logging.INFO,
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}


def get_logger(name: str) -> logging.Logger:
    """
    获取一个logger实例

    Args:
        name: logger名称

    Returns:
        logging.Logger实例
    """
    return setup_logger(name)


def setup_logger(name: str) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: logger名称

    Returns:
        配置好的logging.Logger实例
    """
    # 确保日志目录存在
    log_dir = LOG_SETTINGS['log_dir']
    os.makedirs(log_dir, exist_ok=True)

    # 创建日志文件名（包含日期）
    log_file = os.path.join(
        log_dir,
        f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    )

    # 创建日志记录器
    logger = logging.getLogger(name)

    # 如果logger已经有处理器，则不重复添加
    if not logger.handlers:
        logger.setLevel(LOG_SETTINGS['log_level'])

        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(LOG_SETTINGS['log_format']))

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_SETTINGS['log_format']))

        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger