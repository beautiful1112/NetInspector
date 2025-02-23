# utils/excel_to_yaml.py

import pandas as pd
import yaml
from typing import Dict, List, Optional, Tuple
import os
from utils.settings import BASE_DIR  # 导入BASE_DIR以确保路径正确

def excel_to_yaml(excel_data: bytes, sheet_name: str = 'Sheet1') -> Tuple[Optional[str], Optional[str]]:
    """
    Convert Excel data to YAML and save to config directory.

    Args:
        excel_data: Excel file bytes content
        sheet_name: The name of the Excel sheet, defaults to 'Sheet1'

    Returns:
        Tuple of (yaml_file_path, error_message) where yaml_file_path is the path to the generated YAML file
        or None if failed, and error_message is the error description or None if successful
    """
    try:
        # Create a temporary file to store Excel data
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_file.write(excel_data)
            temp_excel_path = temp_file.name

        # Read Excel file
        df = pd.read_excel(temp_excel_path, sheet_name=sheet_name)
        print("DataFrame类型:", type(df))
        print("DataFrame内容:")
        print(df)
        print("DataFrame列名:", df.columns.tolist())

        # Ensure DataFrame format is correct
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Excel data read error, did not get a valid DataFrame object")

        # Check if necessary columns exist
        required_columns = ['name', 'ip', 'vendor', 'model']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Excel file missing required columns: {missing_columns}")

        # Process devices by type (switch, firewall, wireless)
        devices_by_type = {
            'switch': {'credential_group': 'switch_admin', 'devices': []},
            'firewall': {'credential_group': 'firewall_admin', 'devices': []},
            'wireless': {'credential_group': 'wireless_admin', 'devices': []}
        }

        # Device type mappings for Netmiko
        device_type_mapping = {
            # HUAWEI
            'CE': 'huawei_vrpv8',
            'CE16808': 'huawei_vrpv8',
            'CE6881': 'huawei_vrpv8',
            'S12700': 'huawei',
            'S5735': 'huawei',
            'S5700': 'huawei',
            'S5720': 'huawei',
            'S6720': 'huawei',
            'S5700EI': 'huawei',
            'S5720EI': 'huawei',
            'USG': 'huawei',
            'AC6605': 'huawei',
            # H3C
            'S5560': 'hp_comware',
            'S7510': 'hp_comware',
        }

        # Add counters
        processed_count = 0
        unknown_count = 0
        unknown_devices = []

        for index, row in df.iterrows():
            try:
                # Handle IP address with possible newline characters
                ip = str(row['ip']).split('\n')[0].strip()

                device_info = {
                    'name': str(row['name']).strip(),
                    'ip': ip,
                    'vendor': str(row['vendor']).lower().strip(),
                    'model': str(row['model']).strip(),
                    'type': get_device_type(str(row['model']).strip(), device_type_mapping)
                }

                category = get_device_category(str(row['model']))
                if category in devices_by_type:
                    devices_by_type[category]['devices'].append(device_info)
                    processed_count += 1
                    print(f"Processed row {index + 1}: {device_info['name']} - {category}")
                else:
                    unknown_count += 1
                    unknown_devices.append(f"{device_info['name']} ({device_info['model']})")
                    print(f"Unknown device type - Row {index + 1}: {device_info['name']} - {device_info['model']}")
            except Exception as e:
                print(f"Error processing row {index + 1}: {str(e)}")
                continue

        # Save YAML files to config directory
        config_dir = os.path.join(BASE_DIR, 'config')
        os.makedirs(config_dir, exist_ok=True)

        for category, data in devices_by_type.items():
            if data['devices']:
                yaml_file = os.path.join(config_dir, f'{category}.yaml')
                try:
                    with open(yaml_file, 'w', encoding='utf-8') as f:
                        yaml.safe_dump({category: data}, f, allow_unicode=True, sort_keys=False)
                    print(f"Successfully generated config file: {yaml_file}")
                    # Verify file creation
                    if os.path.exists(yaml_file):
                        print(f"Confirmed file exists: {yaml_file}")
                        print(f"File size: {os.path.getsize(yaml_file)} bytes")
                    return yaml_file, None  # 返回成功生成的YAML文件路径
                except Exception as e:
                    print(f"Error generating {yaml_file}: {str(e)}")
                    return None, f"Error generating {yaml_file}: {str(e)}"

        # Print statistics
        print(f"\nStatistics:")
        print(f"Total rows: {len(df)}")
        print(f"Successfully processed: {processed_count}")
        print(f"Unknown types: {unknown_count}")
        if unknown_devices:
            print("\nUnrecognized devices:")
            for device in unknown_devices:
                print(f"- {device}")

        return None, "No valid devices processed"  # 如果没有有效设备，返回错误信息

    except Exception as e:
        return None, f"Error converting Excel to YAML: {str(e)}"

def get_device_type(model: str, mapping: Dict[str, str]) -> str:
    """Get the device type in Netmiko based on the device model."""
    for key, value in mapping.items():
        if model.startswith(key):
            return value
    return 'unknown'

def get_device_category(model: str) -> str:
    """Determine the device category based on the device model."""
    model = model.upper()
    if any(model.startswith(prefix) for prefix in [
        'CE16808', 'CE6881', 'S12700', 'S5735', 'S5560', 'S7510',
        'S5700', 'S5720', 'S6720', 'S5700EI', 'S5720EI'
    ]):
        return 'switch'
    elif model.startswith(('USG', 'FW')):
        return 'firewall'
    elif model.startswith(('AC', 'AP')):
        return 'wireless'
    return 'unknown'