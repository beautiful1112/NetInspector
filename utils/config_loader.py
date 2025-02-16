# utils/config_loader.py

import os
import yaml
from typing import Dict, Any, List


class ConfigLoader:

    """配置加载器"""

    @staticmethod
    def get_devices(device_type: str) -> List[Dict[str, Any]]:
        """
        获取指定类型的所有设备列表

        Args:
            device_type: 设备类型(firewall/switch等)

        Returns:
            设备列表
        """
        try:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)

            # 构建配置文件的完整路径
            device_config_path = os.path.join(base_dir, 'config', f'{device_type}.yaml')

            # 加载设备配置
            with open(device_config_path, 'r', encoding='utf-8') as f:
                device_config = yaml.safe_load(f)

            return device_config[device_type]['devices']

        except Exception as e:
            raise Exception(f"获取设备列表失败: {str(e)}")

    @staticmethod
    def get_device_info(ip: str, device_type: str) -> Dict[str, Any]:
        """
        获取设备信息

        Args:
            ip: 设备IP
            device_type: 设备类型(firewall/switch等)

        Returns:
            设备连接信息字典
        """
        try:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)

            # 构建配置文件的完整路径
            device_config_path = os.path.join(base_dir, 'config', f'{device_type}.yaml')
            credential_config_path = os.path.join(base_dir, 'config', 'credential.yaml')

            # 加载设备配置
            with open(device_config_path, 'r', encoding='utf-8') as f:
                device_config = yaml.safe_load(f)

            # 加载认证配置
            with open(credential_config_path, 'r', encoding='utf-8') as f:
                credential_config = yaml.safe_load(f)

            # 查找匹配的设备
            device = None
            for dev in device_config[device_type]['devices']:
                if dev['ip'] == ip:
                    device = dev
                    break

            if not device:
                raise ValueError(f"未找到IP为{ip}的{device_type}设备配置")

            # 获取认证信息
            credential_group = device_config[device_type]['credential_group']

            # 修改这里：在 credential 键下查找认证组
            if credential_group not in credential_config['credential']:
                raise ValueError(f"未找到认证组{credential_group}的配置")

            credentials = credential_config['credential'][credential_group]

            # 组装设备连接信息
            device_info = {
                'device_type': device['type'],
                'host': device['ip'],
                'username': credentials['username'],
                'password': credentials['password'],
                'port': 22  # 默认SSH端口
            }

            return device_info

        except FileNotFoundError as e:
            raise Exception(f"加载设备配置文件失败: {str(e)}")
        except yaml.YAMLError as e:
            raise Exception(f"解析YAML配置文件失败: {str(e)}")
        except Exception as e:
            raise Exception(f"获取设备信息失败: {str(e)}")