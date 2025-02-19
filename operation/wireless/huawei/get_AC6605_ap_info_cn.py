#This script need to be refactored
from netmiko import ConnectHandler
import re
import csv
from datetime import datetime
import pandas as pd


class AC6605Client:
    def __init__(self, host, username, password, port=22):
        self.device = {
            'device_type': 'huawei',
            'host': host,
            'username': username,
            'password': password,
            'port': port,
            'conn_timeout': 20,
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = ConnectHandler(**self.device)
            return True
        except Exception as e:
            print(f"Connect failed: {str(e)}")
            return False

    def get_ap_info(self):
        """
        Get AP information from the AC6605 device
        """
        try:
            # Disable paging
            self.connection.send_command('screen-length 0 temporary')

            # 获取AP基本信息（dis ap all）
            ap_output = self.connection.send_command('dis ap all')
            ap_info = self._parse_ap_all(ap_output)

            # 获取AP版本信息（display ap version all）
            version_output = self.connection.send_command('display ap version all')
            version_info = self._parse_ap_version(version_output)

            # 合并信息：根据 ap_id 作为键进行合并
            merged_info = self._merge_ap_info(ap_info, version_info)
            return merged_info
        except Exception as e:
            print(f"获取AP信息失败: {str(e)}")
            return []

    def _parse_ap_all(self, output):
        """
        解析 "dis ap all" 命令的输出

        输出示例：
          Total AP information:
          fault : fault           [28]
          idle  : idle            [4]
          nor   : normal          [76]
          ExtraInfo : Extra information
          P     : insufficient power supply
          -------------------------------------------------------------------------------------------------------------------------------
          ID    MAC            Name         Group           IP            Type             State  STA Uptime           ExtraInfo
          -------------------------------------------------------------------------------------------------------------------------------
          0     18de-d77d-2ba0 AP203        PSTV            172.18.20.56  AP2030DN         nor    0   279D:11H:50M:43S -
          1     18de-d77d-2a20 AP206        PSTV            172.18.20.59  AP2030DN         nor    0   279D:11H:50M:34S -
          ...
        """
        ap_list = []
        lines = output.splitlines()
        in_table = False
        dashed_count = 0
        for line in lines:
            line_strip = line.strip()
            # 仅含“-”的行作为分隔线
            if re.match(r"^-+$", line_strip):
                dashed_count += 1
                # 当遇到第二道分隔线后，后续都是数据行
                if dashed_count == 2:
                    in_table = True
                continue
            if in_table:
                if not line_strip:
                    continue
                parts = line.split()
                # 至少应包含九个字段：ID, MAC, Name, Group, IP, Type, State, STA, Uptime
                if len(parts) < 9:
                    continue
                # 如果有多余字段，认为第10列为 ExtraInfo
                extra_info = parts[9] if len(parts) >= 10 else ""
                ap_entry = {
                    'ap_id': parts[0],
                    'mac': parts[1],
                    'name': parts[2],
                    'group': parts[3],
                    'ip': parts[4] if parts[4] != '-' else '',
                    'type': parts[5],
                    'state': parts[6],      # 如 nor, idle, fault 等缩写
                    'sta_count': parts[7],
                    'uptime': parts[8],
                    'extra_info': extra_info
                }
                ap_list.append(ap_entry)
        return ap_list

    def _parse_ap_version(self, output):
        """
        解析 "display ap version all" 命令的输出

        输出示例：
          <PSTVHKWAPC01>display ap version all
          Compatible version : V200R009 V200R010 V200R019
          ---------------------------------------------------------------------------------------------------------
          ID     Name         Group           Type             Version            PatchVersion       state
          ---------------------------------------------------------------------------------------------------------
          0      AP203        PSTV            AP2030DN         V200R019C00SPC910  -                  normal
          1      AP206        PSTV            AP2030DN         V200R019C00SPC910  -                  normal
          ...
        """
        version_dict = {}
        lines = output.splitlines()
        in_table = False
        dashed_count = 0
        for line in lines:
            line_strip = line.strip()
            if re.match(r"^-+$", line_strip):
                dashed_count += 1
                if dashed_count == 2:
                    in_table = True
                continue
            if in_table:
                if not line_strip:
                    continue
                parts = line.split()
                # 预期字段：ID, Name, Group, Type, Version, PatchVersion, state
                if len(parts) < 7:
                    continue
                ap_id = parts[0]
                version_info = {
                    'software_version': parts[4] if parts[4] != '-' else '',
                    'patch_version': parts[5] if parts[5] != '-' else '',
                    # 此处的状态为版本输出中的状态，可用于核查
                    'version_state': parts[6]
                }
                version_dict[ap_id] = version_info
        return version_dict

    def _merge_ap_info(self, ap_list, version_dict):
        """
        根据 ap_id 合并基础信息与版本信息
        """
        merged_list = []
        for ap in ap_list:
            ap_id = ap.get('ap_id')
            if ap_id in version_dict:
                ap.update(version_dict[ap_id])
            else:
                ap['software_version'] = ''
                ap['patch_version'] = ''
            merged_list.append(ap)
        return merged_list

    def export_to_csv(self, ap_list, filename=None):
        """
        将合并后的AP信息导出到CSV文件，并利用pandas生成统计信息
        """
        if not filename:
            filename = f'ap_info_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        headers = ['AP ID', 'MAC地址', 'AP名称', 'AP组', 'IP地址', '设备型号',
                   '状态', '用户数', '运行时间', '额外信息', '软件版本', '补丁版本']
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for ap in ap_list:
                    writer.writerow({
                        'AP ID': ap.get('ap_id', ''),
                        'MAC地址': ap.get('mac', ''),
                        'AP名称': ap.get('name', ''),
                        'AP组': ap.get('group', ''),
                        'IP地址': ap.get('ip', ''),
                        '设备型号': ap.get('type', ''),
                        '状态': ap.get('state', ''),
                        '用户数': ap.get('sta_count', ''),
                        '运行时间': ap.get('uptime', ''),
                        '额外信息': ap.get('extra_info', ''),
                        '软件版本': ap.get('software_version', ''),
                        '补丁版本': ap.get('patch_version', '')
                    })
            print(f"数据已导出到: {filename}")

            # 利用pandas生成数据统计
            df = pd.DataFrame(ap_list)
            # 将 sta_count 转为数字，不合法的转换为0
            df['sta_count'] = pd.to_numeric(df['sta_count'], errors='coerce').fillna(0).astype(int)
            stats = {
                '总AP数': len(df),
                '在线AP数': len(df[df['state'] == 'nor']),
                '离线AP数': len(df[df['state'] == 'fault']),
                '空闲AP数': len(df[df['state'] == 'idle']),
                '总客户端数': df['sta_count'].sum(),
                'AP型号统计': df['type'].value_counts().to_dict()
            }
            stats_file = f'ap_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            with open(stats_file, 'w', encoding='utf-8') as f:
                for key, value in stats.items():
                    f.write(f"{key}: {value}\n")
            print(f"统计信息已导出到: {stats_file}")

        except Exception as e:
            print(f"导出失败: {str(e)}")

    def close(self):
        """关闭与AC的连接"""
        if self.connection:
            self.connection.disconnect()


def main():
    # AC设备信息
    ac_host = ""         # AC的IP地址
    ac_username = ""     # 登录用户名
    ac_password = ""     # 登录密码

    # 创建AC客户端实例
    ac = AC6605Client(ac_host, ac_username, ac_password)
    try:
        if ac.connect():
            print("成功连接到AC")
            # 获取并合并AP信息
            ap_list = ac.get_ap_info()
            # 导出合并后的数据及统计信息
            ac.export_to_csv(ap_list)
    except Exception as e:
        print(f"执行出错: {str(e)}")
    finally:
        ac.close()
        print("连接已关闭")


if __name__ == "__main__":
    main()