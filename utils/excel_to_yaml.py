# utils/excel_to_yaml.py

import pandas as pd
import yaml
from typing import Dict, List
import os


def excel_to_yaml(excel_file: str, sheet_name: str = 'Sheet1') -> None:
    """
    Make EXCEL date to YAML

    Args:
        excel_file: Excel file path
        sheet_name: the name of sheet_name, default sheet is the first choice
    """
    # read excel file
    # 确保Excel文件存在
    # 获取当前脚本的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录（假设是当前目录的上一级）
    project_root = os.path.dirname(current_dir)
    # 构建config目录的完整路径
    config_dir = os.path.join(project_root, 'config')

    print(f"当前目录: {current_dir}")
    print(f"项目根目录: {project_root}")
    print(f"配置文件目录: {config_dir}")

    try:
        # 读取Excel文件
        df = pd.read_excel(excel_file, sheet_name='Sheet1')
        # 添加调试信息
        print("DataFrame类型:", type(df))
        print("DataFrame内容:")
        print(df)
        print("DataFrame列名:", df.columns.tolist())
    except Exception as e:
        raise Exception(f"读取Excel文件失败: {str(e)}")

    # 确保DataFrame格式正确
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Excel数据读取错误，没有得到正确的DataFrame对象")

    # 检查必要的列是否存在
    required_columns = ['name', 'ip', 'vendor', 'model']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Excel文件缺少必要的列: {missing_columns}")

    # Devices are processed in groups based on vendors
    devices_by_type = {
        'switch': {'credential_group': 'switch_admin', 'devices': []},
        'firewall': {'credential_group': 'firewall_admin', 'devices': []},
        'wireless': {'credential_group': 'wireless_admin', 'devices': []}
    }

    # Device type mappings
    device_type_mapping = {
        # HUAWEI
        'CE': 'huawei_vrpv8',
        'CE16808': 'huawei_vrpv8',
        'CE6881': 'huawei_vrpv8',
        'S12700': 'huawei',
        'S5735': 'huawei',
        'S5700': 'huawei',
        'S5720': 'huawei',
        'S6720': 'huawei',  #
        'S5700EI': 'huawei',  #
        'S5720EI': 'huawei',  #
        'USG': 'huawei',
        'AC6605': 'huawei',
        # H3C
        'S5560': 'hp_comware',
        'S7510': 'hp_comware',
    }

    # 添加计数器
    processed_count = 0
    unknown_count = 0
    unknown_devices = []

    for index, row in df.iterrows():
        try:
            # 处理IP地址中可能的换行符
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
                print(f"处理第{index + 1}行: {device_info['name']} - {category}")
            else:
                unknown_count += 1
                unknown_devices.append(f"{device_info['name']} ({device_info['model']})")
                print(f"未知设备类型 - 第{index + 1}行: {device_info['name']} - {device_info['model']}")
        except Exception as e:
            print(f"处理第{index + 1}行时出错: {str(e)}")
            continue


    # 保存YAML文件
    for category, data in devices_by_type.items():
        if data['devices']:
            yaml_file = os.path.join(config_dir, f'{category}.yaml')
            try:
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    yaml.safe_dump({category: data}, f, allow_unicode=True, sort_keys=False)
                print(f"成功生成配置文件: {yaml_file}")
                # 验证文件是否真的创建成功
                if os.path.exists(yaml_file):
                    print(f"确认文件存在: {yaml_file}")
                    print(f"文件大小: {os.path.getsize(yaml_file)} 字节")
            except Exception as e:
                print(f"生成{yaml_file}时出错: {str(e)}")

    # 列出config目录中的文件
    try:
        print("\nconfig目录中的文件:")
        for file in os.listdir(config_dir):
            file_path = os.path.join(config_dir, file)
            print(f"- {file} ({os.path.getsize(file_path)} 字节)")
    except Exception as e:
        print(f"列出目录内容时出错: {str(e)}")

    # 打印统计信息
    print(f"\n统计信息:")
    print(f"总行数: {len(df)}")
    print(f"成功处理: {processed_count}")
    print(f"未知类型: {unknown_count}")
    if unknown_devices:
        print("\n未能识别的设备:")
        for device in unknown_devices:
            print(f"- {device}")


def get_device_type(model: str, mapping: Dict[str, str]) -> str:
    """Obtain the device type in Netmiko based on the device model"""
    for key, value in mapping.items():
        if model.startswith(key):
            return value
    return 'unknown'


def get_device_category(model: str) -> str:
    """Determine the device category based on the device model"""
    model = model.upper()
    # 检查完整的型号匹配
    if any(model.startswith(prefix) for prefix in [
        'CE16808', 'CE6881', 'S12700', 'S5735', 'S5560', 'S7510',
        'S5700', 'S5720', 'S6720', # 添加S6720
        'S5700EI', 'S5720EI'  # 添加EI系列
    ]):
        return 'switch'
    elif model.startswith(('USG', 'FW')):
        return 'firewall'
    elif model.startswith(('AC', 'AP')):
        return 'wireless'
    return 'unknown'

# 使用示例
if __name__ == '__main__':
    excel_to_yaml('devices.xlsx')