# utils/config_loader.py
import os
import yaml
import json
from typing import Dict, Any, List

class ConfigLoader:
    """Load configuration from YAML, JSON, and TXT files"""

    @staticmethod
    def get_devices(device_type: str) -> List[Dict[str, Any]]:
        """
        Get device list from YAML file.

        Args:
            device_type: Device category (e.g., firewall, switch)

        Returns:
            List of devices
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)
            device_config_path = os.path.join(base_dir, 'config', f'{device_type}.yaml')
            with open(device_config_path, 'r', encoding='utf-8') as f:
                device_config = yaml.safe_load(f)
            return device_config[device_type]['devices']
        except Exception as e:
            raise Exception(f"Load device config failed: {str(e)}")

    @staticmethod
    def get_device_info(ip: str, device_type: str) -> Dict[str, Any]:
        """
        Get device connection information from YAML files.

        Args:
            ip: Device IP address
            device_type: Device category (e.g., firewall, switch)

        Returns:
            Dictionary of device connection information
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)
            device_config_path = os.path.join(base_dir, 'config', f'{device_type}.yaml')
            credential_config_path = os.path.join(base_dir, 'config', 'credential.yaml')

            with open(device_config_path, 'r', encoding='utf-8') as f:
                device_config = yaml.safe_load(f)
            with open(credential_config_path, 'r', encoding='utf-8') as f:
                credential_config = yaml.safe_load(f)

            device = None
            for dev in device_config[device_type]['devices']:
                if dev['ip'] == ip:
                    device = dev
                    break

            if not device:
                raise ValueError(f"No {device_type} configuration with IP {ip} found")

            credential_group = device_config[device_type]['credential_group']
            if credential_group not in credential_config['credential']:
                raise ValueError(f"No credential group {credential_group} found")

            credentials = credential_config['credential'][credential_group]

            device_info = {
                'device_type': device['type'],
                'host': device['ip'],
                'username': credentials['username'],
                'password': credentials['password'],
                'port': 22  # Default SSH port
            }
            return device_info
        except FileNotFoundError as e:
            raise Exception(f"Load configuration failed: {str(e)}")
        except yaml.YAMLError as e:
            raise Exception(f"Failed to parse YAML: {str(e)}")
        except Exception as e:
            raise Exception(f"Get config failed: {str(e)}")

    @staticmethod
    def load_commands(file_path: str) -> Dict[str, List[str]]:
        """
        Load commands from JSON file.

        Args:
            file_path: Path to the JSON commands file

        Returns:
            Dictionary of command categories and commands
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Load commands failed: {str(e)}")

    @staticmethod
    def load_prompt(file_path: str) -> str:
        """
        Load prompt template from TXT file.

        Args:
            file_path: Path to the TXT prompt file

        Returns:
            Prompt template string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Load prompt failed: {str(e)}")