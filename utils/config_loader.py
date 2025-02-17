# utils/config_loader.py

import os
import yaml
from typing import Dict, Any, List


class ConfigLoader:

    """load configuration from YAML files"""

    @staticmethod
    def get_devices(device_type: str) -> List[Dict[str, Any]]:
        """
        get device list

        Args:
            device_type: the class of device (firewall/switch等)

        Returns:
            list of devices
        """
        try:
            # get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)

            # build the full path of the configuration file
            device_config_path = os.path.join(base_dir, 'config', f'{device_type}.yaml')

            # load the device configuration
            with open(device_config_path, 'r', encoding='utf-8') as f:
                device_config = yaml.safe_load(f)

            return device_config[device_type]['devices']

        except Exception as e:
            raise Exception(f"load config of devices failed: {str(e)}")

    @staticmethod
    def get_device_info(ip: str, device_type: str) -> Dict[str, Any]:
        """
        get device connection information

        Args:
            ip: IP
            device_type: the classof device (firewall/switch等)

        Returns:
            dict of device connection information
        """
        try:
            # get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)

            # build the full path of the configuration file
            device_config_path = os.path.join(base_dir, 'config', f'{device_type}.yaml')
            credential_config_path = os.path.join(base_dir, 'config', 'credential.yaml')

            # load the device configuration
            with open(device_config_path, 'r', encoding='utf-8') as f:
                device_config = yaml.safe_load(f)

            # load the credential configuration
            with open(credential_config_path, 'r', encoding='utf-8') as f:
                credential_config = yaml.safe_load(f)

            # look for the device configuration
            device = None
            for dev in device_config[device_type]['devices']:
                if dev['ip'] == ip:
                    device = dev
                    break

            if not device:
                raise ValueError(f"NO {device_type} configuration with IP {ip} found")

            # look for the credential group
            credential_group = device_config[device_type]['credential_group']


            if credential_group not in credential_config['credential']:
                raise ValueError(f"未找到认证组{credential_group}的配置")

            credentials = credential_config['credential'][credential_group]

            # build the device information
            device_info = {
                'device_type': device['type'],
                'host': device['ip'],
                'username': credentials['username'],
                'password': credentials['password'],
                'port': 22  # 默认SSH端口
            }

            return device_info

        except FileNotFoundError as e:
            raise Exception(f"Load configuration failed: {str(e)}")
        except yaml.YAMLError as e:
            raise Exception(f"Failed to parse the yaml: {str(e)}")
        except Exception as e:
            raise Exception(f"Get config failed: {str(e)}")