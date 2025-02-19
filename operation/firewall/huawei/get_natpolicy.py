#This script need to be refactored to get the NAT policy configuration from the Huawei firewall.

from netmiko import ConnectHandler
import re
import pandas as pd
from datetime import datetime


def connect_to_device(device_ip, username, password):
    """connect to the device"""
    device = {
        'device_type': 'huawei',
        'host': device_ip,
        'username': username,
        'password': password,
        'port': 22,
    }

    try:
        connection = ConnectHandler(**device)
        return connection
    except Exception as e:
        print(f"Connecting failed: {str(e)}")
        return None


def parse_nat_server(text):
    """parse the NAT server configuration"""
    servers = []

    # Use regular expression to extract each server block
    server_blocks = re.finditer(r'server name\s*:\s*(\S+).*?(?=server name|$)', text, re.DOTALL)

    for block in server_blocks:
        block_text = block.group(0)
        server_dict = {}

        # Define the fields and their regular expressions
        fields = {
            'server_name': r'server name\s*:\s*(\S+)',
            'global_start_addr': r'global-start-addr\s*:\s*(\S+)',
            'global_end_addr': r'global-end-addr\s*:\s*(\S+)',
            'inside_start_addr': r'inside-start-addr\s*:\s*(\S+)',
            'inside_end_addr': r'inside-end-addr\s*:\s*(\S+)',
            'global_start_port': r'global-start-port\s*:\s*(\S+)',
            'global_end_port': r'global-end-port\s*:\s*(\S+)',
            'inside_start_port': r'inside-start-port\s*:\s*(\S+)',
            'inside_end_port': r'inside-end-port\s*:\s*(\S+)',
            'globalvpn': r'globalvpn\s*:\s*(\S+)',
            'insidevpn': r'insidevpn\s*:\s*(\S+)',
            'vsys': r'vsys\s*:\s*(\S+)',
            'zone': r'zone\s*:\s*(\S+)',
            'protocol': r'protocol\s*:\s*(\S+)',
            'vrrp': r'vrrp\s*:\s*(\S+)',
            'no_reverse': r'no-reverse\s*:\s*(\S+)',
            'nat_disable': r'nat-disable\s*:\s*(\S+)',
            'route': r'route\s*:\s*(\S+)',
            'description': r'description\s*:\s*(\S+)',
            'tunnel_id': r'tunnel-id\s*:\s*(\S+)',
            'cpe_addr': r'CPE-addr\s*:\s*(\S+)'
        }

        # Extract the values for each field
        for field, pattern in fields.items():
            match = re.search(pattern, block_text)
            server_dict[field] = match.group(1) if match else '---'

        servers.append(server_dict)

    return servers


def main():
    # device information
    device_ip = ""
    username = ""
    password = ""

    # connect to the device
    connection = connect_to_device(device_ip, username, password)
    if not connection:
        return

    try:
        # send command to the device
        output = connection.send_command("display nat server")

        # parse the NAT server configuration
        servers = parse_nat_server(output)

        # Create DataFrame
        df = pd.DataFrame(servers)

        # Display all columns
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_rows', None)

        # Display the NAT server configuration
        print("\nNAT Server Configuration Table:")
        print(df)

        # Export the configuration to an Excel file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"nat_servers_{timestamp}.xlsx"
        df.to_excel(excel_filename, index=False)
        print(f"\nConfiguration exported to {excel_filename}")

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        # disconnect from the device
        connection.disconnect()


if __name__ == "__main__":
    main()