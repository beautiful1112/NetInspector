# connect/device_connector.py

import logging
import time
from typing import Dict, Any, Optional
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException


class DeviceConnector:
    def __init__(self, device_info: Dict[str, Any]):
        self.device_info = device_info
        self.connection = None
        self.logger = logging.getLogger('connect.device_connector')
        self.max_retries = 3
        self.retry_interval = 5

    def connect(self) -> None:
        """Create a connection to the device"""
        for attempt in range(self.max_retries):
            try:
                self.connection = ConnectHandler(**self.device_info)
                return
            except NetMikoTimeoutException:
                self.logger.error(f"Connection timeout to {self.device_info['host']}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_interval)
            except NetMikoAuthenticationException:
                self.logger.error(f"Authentication failed for {self.device_info['host']}")
                raise
            except Exception as e:
                self.logger.error(f"Failed to connect to {self.device_info['host']}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_interval)

        raise ConnectionError(f"Failed to connect to {self.device_info['host']} after {self.max_retries} attempts")

    def disconnect(self) -> None:
        """Disconnect from the device"""
        if self.connection:
            try:
                self.connection.disconnect()
            except Exception as e:
                self.logger.error(f"Error disconnecting from {self.device_info['host']}: {str(e)}")
            finally:
                self.connection = None

    def send_command(self, command: str, expect_string: Optional[str] = None) -> str:
        """Send a command to the device and return the output"""
        if not self.connection:
            raise ConnectionError("Not connected to device")

        try:
            # Send the command and return the output
            if expect_string:
                output = self.connection.send_command(
                    command,
                    expect_string=expect_string,
                    strip_prompt=True,
                    strip_command=True
                )
            else:
                output = self.connection.send_command(
                    command,
                    strip_prompt=True,
                    strip_command=True
                )
            return output

        except Exception as e:
            raise Exception(f"{str(e)}")

    def check_connection(self) -> bool:
        """check if the connection is still active"""
        if not self.connection:
            return False
        try:
            self.connection.send_command("\n", expect_string=r"[>#]")
            return True
        except Exception:
            return False