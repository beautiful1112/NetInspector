# inspection/huawei/usg12004_inspection.py

import os
import sys
import time
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from utils.config_loader import ConfigLoader
from utils.settings import BASE_DIR as project_root
from connect.device_connector import DeviceConnector
from utils.logger import get_logger
from utils.settings import AI_SETTINGS, OUTPUT_DIRS


class USG12004Inspector:
    """USG12004 device inspector"""

    def __init__(self, device_info: Dict[str, Any]):
        self.device_info = device_info
        self.logger = get_logger('usg12004_inspector')
        self.device_connector = None

        # Output directories
        self.logger.info(f"Project root: {project_root}")
        self.logger.info(f"Raw configs directory: {os.path.join(project_root, 'output', 'raw_configs')}")
        self.logger.info(f"Reports directory: {os.path.join(project_root, 'output', 'reports')}")

        # Create output directories if not exist
        try:
            os.makedirs(os.path.join(project_root, 'output', 'raw_configs'), exist_ok=True)
            os.makedirs(os.path.join(project_root, 'output', 'reports'), exist_ok=True)
            self.logger.info("Directories created/verified successfully")
        except Exception as e:
            self.logger.error(f"Error creating directories: {str(e)}")
            raise

        # Load commands from JSON file(you can also load another JSON file)
        try:
            commands_file = os.path.join(project_root, 'templates', 'commands', 'usg12004_commands.json')
            with open(commands_file, 'r', encoding='utf-8') as f:
                self.commands = json.load(f)
            self.logger.info(f"Commands loaded from {commands_file}")
        except Exception as e:
            self.logger.error(f"Failed to load commands from JSON: {str(e)}")
            raise

        # 初始化 AI 分析器
        try:
            self.llm = ChatOpenAI(
                openai_api_base=AI_SETTINGS['deepseek']['api_base'],
                openai_api_key=AI_SETTINGS['deepseek']['api_key'],
                model_name=AI_SETTINGS['deepseek']['model'],
                temperature=0,
                streaming=False,
                request_timeout=180,
                max_retries=3,
                model_kwargs={
                    "response_format": {"type": "text"}
                }
            )
            self.logger.info("AI model initialized successfully")
        except Exception as e:
            self.logger.error(f"AI model initialized failed: {str(e)}")
            raise

    def collect_data(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        self.logger.info("=" * 50)
        self.logger.info(f"Starting to collect data of device {self.device_info['host']} ...")
        self.logger.info("=" * 50)
        config_data = {}

        try:
            self.device_connector = DeviceConnector({
                **self.device_info,
                'global_delay_factor': 2,
                'timeout': 60,
                'session_timeout': 60
            })
            self.device_connector.connect()
            self.logger.info(f"Successfully connected to device {self.device_info['host']}")

            for category, cmds in self.commands.items():
                self.logger.info("-" * 40)
                self.logger.info(f"Starting to collect data for category: {category} ...")
                self.logger.info(f"This category includes {len(cmds)} commands")
                config_data[category] = {}

                for cmd in cmds:
                    try:
                        self.logger.info(f"Executing command: {cmd}")
                        start_time = time.time()
                        output = self.device_connector.send_command(cmd)
                        end_time = time.time()

                        line_count = len(output.splitlines())
                        execution_time = round(end_time - start_time, 2)

                        config_data[category][cmd] = {
                            'output': output,
                            'line_count': line_count,
                            'timestamp': datetime.now().isoformat(),
                            'execution_time': execution_time
                        }

                        self.logger.info("Command execution complete:")
                        self.logger.info(f"  - Execution time: {execution_time} seconds")
                        self.logger.info(f"  - Lines collected: {line_count}")

                        if 'display cpu-usage' in cmd:
                            self.logger.info("CPU usage overview:")
                            for line in output.splitlines()[:5]:
                                self.logger.info(f"  {line}")
                        elif 'display memory' in cmd:
                            self.logger.info("Memory usage overview:")
                            for line in output.splitlines():
                                if any(key in line for key in ['Total Physical', 'Memory Using Percentage', 'State']):
                                    self.logger.info(f"  {line}")

                        time.sleep(0.5)

                    except Exception as e:
                        self.logger.error(f"Command execution failed: {cmd}")
                        self.logger.error(f"Error: {str(e)}")
                        config_data[category][cmd] = {
                            'output': f"ERROR: {str(e)}",
                            'line_count': 0,
                            'timestamp': datetime.now().isoformat(),
                            'execution_time': 0
                        }

                self.logger.info(f"Completed collecting data for category: {category}, executed {len(cmds)} commands")

            total_commands = sum(len(cmds) for cmds in self.commands.values())
            total_lines = sum(
                data['line_count']
                for category in config_data.values()
                for data in category.values()
            )

            self.logger.info("=" * 50)
            self.logger.info("Collection summary:")
            self.logger.info(f"- Total commands: {total_commands}")
            self.logger.info(f"- Total lines: {total_lines}")
            self.logger.info(f"- Total categories: {len(self.commands)}")
            self.logger.info("=" * 50)
            return config_data

        except Exception as e:
            self.logger.error(f"Data collection failed: {str(e)}", exc_info=True)
            raise
        finally:
            if self.device_connector:
                try:
                    self.device_connector.disconnect()
                    self.logger.info(f"Disconnected from device {self.device_info['host']}")
                except Exception as e:
                    self.logger.error(f"Error during disconnect: {str(e)}")

    def save_raw_data(self, config_data: Dict[str, Any]) -> str:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            device_ip = self.device_info['host']
            file_path = os.path.join(project_root, 'output', 'raw_configs', f"raw_config_{device_ip}_{timestamp}.txt")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            self.logger.info("Saving raw configuration:")
            self.logger.info(f"Output directory: {os.path.dirname(file_path)}")
            self.logger.info(f"File path: {file_path}")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# HUAWEI USG12004 Original Configuration\n")
                f.write(f"# Device IP: {device_ip}\n")
                f.write(f"# Collected at: {timestamp}\n\n")
                for category, commands in config_data.items():
                    f.write(f"\n{'=' * 20} {category.upper()} {'=' * 20}\n")
                    for cmd, data in commands.items():
                        f.write(f"\n{'-' * 10} {cmd} {'-' * 10}\n")
                        f.write(f"Collected at: {data['timestamp']}\n")
                        f.write(f"Line count: {data['line_count']}\n")
                        f.write(f"Output:\n{data['output']}\n")

            self.logger.info(f"File successfully saved to: {file_path}")
            return file_path

        except Exception as e:
            self.logger.error("Error saving raw data:")
            self.logger.error(f"Exception: {str(e)}", exc_info=True)
            raise

    def analyze_data(self, config_data: Dict[str, Any]) -> str:
        try:
            self.logger.info("Starting analysis of data...")
            formatted_config = self._format_config_data(config_data)
            # 从 TXT 文件加载 prompt 模板
            prompt_file = os.path.join(project_root, 'templates', 'prompts', 'usg12004_prompt.txt')
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_template_str = f.read()
            prompt = PromptTemplate.from_template(prompt_template_str)
            max_length = 80000
            truncated_config = formatted_config[:max_length]
            formatted_prompt = prompt.format(config=truncated_config)

            for attempt in range(3):
                try:
                    if attempt > 0:
                        self.logger.info(f"Retrying in {5 * (attempt + 1)} seconds...")
                        time.sleep(5 * (attempt + 1))
                    self.logger.info(f"Attempt {attempt + 1} to analyze data...")
                    response = self.llm.invoke(formatted_prompt)
                    if isinstance(response, str):
                        content = response
                    else:
                        content = response.content if hasattr(response, 'content') else str(response)
                    if content and len(content) > 50:
                        self.logger.info("Analysis successful")
                        return content
                    else:
                        raise ValueError("AI model returned an empty response")
                except Exception as e:
                    self.logger.error(f"Attempt {attempt + 1} analysis failed: {str(e)}")
                    if attempt == 2:
                        raise
            raise Exception("All attempts to analyze failed")
        except Exception as e:
            self.logger.error(f"Data analysis failed: {str(e)}", exc_info=True)
            raise

    def save_report(self, analysis: str) -> str:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            device_ip = self.device_info['host']
            report_path = os.path.join(project_root, 'output', 'reports', f"report_{device_ip}_{timestamp}.md")
            os.makedirs(os.path.dirname(report_path), exist_ok=True)

            self.logger.info("Saving report:")
            self.logger.info(f"Reports directory: {os.path.dirname(report_path)}")
            self.logger.info(f"Report path: {report_path}")

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"# HUAWEI USG12004 Inspection Analysis Report\n\n")
                f.write(f"## Basic Information\n")
                f.write(f"- Device IP: {device_ip}\n")
                f.write(f"- Analysis Time: {timestamp}\n\n")
                f.write("## Analysis Result\n\n")
                f.write(analysis)

            self.logger.info(f"Report successfully saved to: {report_path}")
            return report_path

        except Exception as e:
            self.logger.error("Error saving report:")
            self.logger.error(f"Exception: {str(e)}", exc_info=True)
            raise

    def run(self) -> Tuple[str, str]:
        try:
            config_data = self.collect_data()
            raw_config_path = self.save_raw_data(config_data)
            self.logger.info(f"Original config saved to: {raw_config_path}")
            analysis_result = self.analyze_data(config_data)
            report_path = self.save_report(analysis_result)
            self.logger.info(f"Report saved to: {report_path}")
            return raw_config_path, report_path
        except Exception as e:
            self.logger.error(f"Inspection failed: {str(e)}", exc_info=True)
            raise

    def _format_config_data(self, config_data: Dict[str, Any]) -> str:
        formatted_config = []
        for category, commands in config_data.items():
            formatted_config.append(f"\n=== {category.upper()} ===")
            for cmd, data in commands.items():
                formatted_config.append(f"\n--- {cmd} ---")
                formatted_config.append(data['output'])
        return "\n".join(formatted_config)


# Async inspection function
async def inspect_device_async(device: dict) -> dict:
    logger = get_logger("async_inspection")
    loop = asyncio.get_running_loop()
    device_ip = device["ip"]
    logger.info(f"Starting to inspect: {device_ip}", extra={'print_console': True})
    try:
        device_info = ConfigLoader.get_device_info(device_ip, 'firewall')
        inspector = USG12004Inspector(device_info)
        raw_config, report = await loop.run_in_executor(None, inspector.run)
        return {
            "ip": device_ip,
            "status": "success",
            "raw_config": raw_config,
            "report": report
        }
    except Exception as e:
        logger.error(f"{device_ip} inspecting failed: {str(e)}", exc_info=True, extra={'print_console': True})
        return {
            "ip": device_ip,
            "status": "failed",
            "error": str(e)
        }


# Async entry point
async def main_async():
    logger = get_logger("main_async")
    devices = ConfigLoader.get_devices('firewall')
    if not devices:
        logger.info("No configuration found!", extra={'print_console': True})
        return

    tasks = [inspect_device_async(device) for device in devices]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = sum(1 for r in results if r["status"] == "failed")

    logger.info("=" * 50, extra={'print_console': True})
    logger.info("Tasks are done！Summary of results:", extra={'print_console': True})
    logger.info("=" * 50, extra={'print_console': True})
    logger.info(f"Total devices: {len(results)}", extra={'print_console': True})
    logger.info(f"Success count: {success_count}", extra={'print_console': True})
    logger.info(f"Failure count: {failed_count}", extra={'print_console': True})

    for result in results:
        if result["status"] == "success":
            logger.info(f"Device {result['ip']}: status: success", extra={'print_console': True})
            logger.info(f"Original config saving path: {result['raw_config']}", extra={'print_console': True})
            logger.info(f"Report saving path: {result['report']}", extra={'print_console': True})
        else:
            logger.info(f"Device {result['ip']}: status: failed", extra={'print_console': True})
            logger.info(f"Error: {result['error']}", extra={'print_console': True})


if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except Exception as e:
        main_logger = get_logger("main")
        main_logger.error(f"Tasks failed: {str(e)}", exc_info=True, extra={'print_console': True})
        sys.exit(1)
    sys.exit(0)