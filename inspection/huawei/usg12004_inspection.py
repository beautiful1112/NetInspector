# inspection/huawei/usg12004_inspection.py

import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple
import time
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from utils.config_loader import ConfigLoader
from utils.settings import BASE_DIR as project_root
from connect.device_connector import DeviceConnector
from utils.logger import setup_logger
from utils.settings import AI_SETTINGS, OUTPUT_DIRS



class USG12004Inspector:
    """USG12004 firewall inspector class"""

    def __init__(self, device_info: Dict[str, Any]):
        self.device_info = device_info
        self.logger = logging.getLogger('usg12004_inspector')
        self.device_connector = None

        # Print output directories
        print(f"\nProject root: {project_root}")
        print(f"Raw configs directory: {os.path.join(project_root, 'output', 'raw_configs')}")
        print(f"Reports directory: {os.path.join(project_root, 'output', 'reports')}")

        # Ensure output directories exist
        try:
            os.makedirs(os.path.join(project_root, 'output', 'raw_configs'), exist_ok=True)
            os.makedirs(os.path.join(project_root, 'output', 'reports'), exist_ok=True)
            print("\nDirectories created/verified successfully")
        except Exception as e:
            print(f"\nError creating directories: {str(e)}")
            raise

        # Define commands to collect data
        self.commands: Dict[str, List[str]] = {
            'basic': [
                'screen-length 0 temporary',
                'display current-configuration all',
                'display version'
            ],
            'security': [
                'display security risk',
                'display security-policy rule all',
                'display security-policy statistics'
            ],
            'network': [
                'display interface brief',
                'display ip routing-table',
                'display nat-policy rule all',
                'display nat statistics'
            ],
            'monitoring': [
                'display logbuffer',
                'display cpu-usage',
                'display memory'
            ]
        }

        # Initialize AI model
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
            print("Initialized AI model successfully")
        except Exception as e:
            self.logger.error(f"AI model failed to initialize : {str(e)}")
            raise

    def collect_data(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """收集设备数据"""
        print("\n" + "="*50)
        print(f"Start to collect date of {self.device_info['host']} ")
        print("="*50)
        config_data = {}

        try:
            self.device_connector = DeviceConnector(
                {
                    **self.device_info,
                    'global_delay_factor': 2,
                    'timeout': 60,
                    'session_timeout': 60
                }
            )
            self.device_connector.connect()
            print(f"Successfully connect to {self.device_info['host']}")

            for category, cmds in self.commands.items():
                print("\n" + "-"*40)
                print(f"Start to collect date from the class of {category} ")
                print(f"{len(cmds)} commands to execute")
                config_data[category] = {}

                for cmd in cmds:
                    try:
                        print(f"\nrun: {cmd}")
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

                        print(f"execution is completed:")
                        print(f"  -Taking time: {execution_time}seconds")
                        print(f"  -Collecting the rows of date: {line_count}")

                        if 'display cpu-usage' in cmd:
                            print("\nCPU using:")
                            for line in output.splitlines()[:5]:
                                print(f"  {line}")
                        elif 'display memory' in cmd:
                            print("\nMemory using:")
                            lines = output.splitlines()
                            for line in lines:
                                if any(key in line for key in ['Total Physical', 'Memory Using Percentage', 'State']):
                                    print(f"  {line}")

                        time.sleep(0.5)

                    except Exception as e:
                        self.logger.error(f"Command execution failed: {cmd}")
                        self.logger.error(f"Error details: {str(e)}")
                        config_data[category][cmd] = {
                            'output': f"ERROR: {str(e)}",
                            'line_count': 0,
                            'timestamp': datetime.now().isoformat(),
                            'execution_time': 0
                        }

                print(f"\n{category} types of date have been collected，a total of {len(cmds)} commands were executed")

            total_commands = sum(len(cmds) for cmds in self.commands.values())
            total_lines = sum(
                data['line_count']
                for category in config_data.values()
                for data in category.values()
            )

            print("\n" + "="*50)
            print("Date collection completion statistics:")
            print(f"- Sum of commands: {total_commands}")
            print(f"- Sum rows of date: {total_lines}")
            print(f"- Classes of date: {len(self.commands)}")
            print("="*50 + "\n")

            return config_data

        except Exception as e:
            self.logger.error(f"Date collection failed: {str(e)}")
            self.logger.error("Error details:", exc_info=True)
            raise
        finally:
            if self.device_connector:
                try:
                    self.device_connector.disconnect()
                    print(f"Disconnected from {self.device_info['host']}")
                except Exception as e:
                    self.logger.error(f"An error occurred while disconnecting: {str(e)}")

    def save_raw_data(self, config_data: Dict[str, Any]) -> str:
        """Save raw configuration data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            device_ip = self.device_info['host']

            # Ensure correct report directory pathes are used
            file_path = os.path.join(project_root, 'output', 'raw_configs', f"raw_config_{device_ip}_{timestamp}.txt")

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            print(f"\nSaving configuration:")
            print(f"Output directory: {os.path.dirname(file_path)}")
            print(f"File path: {file_path}")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# Original configuration of HUAWEI USG 12004 firewall\n")
                f.write(f"# Device IP: {device_ip}\n")
                f.write(f"# Collection time: {timestamp}\n\n")

                for category, commands in config_data.items():
                    f.write(f"\n{'=' * 20} {category.upper()} {'=' * 20}\n")
                    for cmd, data in commands.items():
                        f.write(f"\n{'-' * 10} {cmd} {'-' * 10}\n")
                        f.write(f"Collection time: {data['timestamp']}\n")
                        f.write(f"Rows of date: {data['line_count']}\n")
                        f.write(f"Output:\n{data['output']}\n")

            print(f"File successfully saved to: {file_path}")
            return file_path

        except Exception as e:
            print(f"\nError details:")
            print(f"Exception type: {type(e)}")
            print(f"Exception message: {str(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            raise

    def analyze_data(self, config_data: Dict[str, Any]) -> str:
        """分析设备数据"""
        try:
            print("\nStart analyzing date...")
            formatted_config = self._format_config_data(config_data)

            prompt = PromptTemplate.from_template("""As a senior network engineer, please analyze the following Huawei firewall configuration:

{config}

Please provide a comprehensive analysis report with the following structure:

1. Configuration Overview
   - Device Information (Model, OS version, Uptime)
   - System Configuration Scale
   - Interface Summary
   - Routing Overview
   - High Availability Status

2. Security Risk Assessment
   - High-Risk Configuration Items
   - Security Policy Analysis
     * Rule base complexity
     * Shadow rules identification
     * Unused rules detection
     * Object group utilization
   - NAT Configuration Audit
     * NAT policy consistency
     * Address translation efficiency
     * NAT rule optimization
   - Access Control Evaluation
     * Zone security settings
     * Interface security policies
     * VPN configuration review

3. Performance Analysis
   - Resource Utilization
     * CPU and memory usage
     * Session table utilization
     * Interface bandwidth usage
   - Performance Bottleneck Identification
     * Configuration-related bottlenecks
     * Hardware resource constraints
     * Throughput limitations
   - Optimization Opportunities
     * Rule base optimization
     * Session management
     * Resource allocation

4. Compliance Assessment
   - Logging and Audit Configuration
     * Syslog settings
     * Security event logging
     * Traffic monitoring
   - Security Baseline Compliance
     * Industry standard alignment
     * Best practice conformity
     * Security hardening status
   - Authentication and Access Control
     * Password policies
     * Administrative access methods
     * AAA configuration

5. Improvement Recommendations
   - Critical Priority Items
     * Security vulnerabilities
     * Performance impacts
     * Immediate risks
   - Medium Priority Optimizations
     * Configuration efficiency
     * Resource optimization
     * Policy improvements
   - Low Priority Suggestions
     * Best practice alignment
     * Documentation updates
     * Future-proofing recommendations

Please include specific configuration examples and technical justifications for each identified issue, and ensure recommendations are actionable and aligned with industry best practices.""")

            # ensure the prompt is not too long
            max_length = 30000
            truncated_config = formatted_config[:max_length]
            formatted_prompt = prompt.format(config=truncated_config)

            for attempt in range(3):
                try:
                    if attempt > 0:
                        print(f"waiting for {5 * (attempt + 1)} seconds and try again...")
                        time.sleep(5 * (attempt + 1))

                    print(f"{attempt + 1}th attempt to analyze...")
                    response = self.llm.invoke(formatted_prompt)

                    if isinstance(response, str):
                        content = response
                    else:
                        content = response.content if hasattr(response, 'content') else str(response)

                    if content and len(content) > 50:
                        print("Analysis completed successfully")
                        return content
                    else:
                        raise ValueError("Analysis response is empty or too short")

                except Exception as e:
                    print(f"{attempt + 1}th attempt to analyze failed: {str(e)}")
                    if attempt == 2:
                        raise

            raise Exception("All attempts to analyze failed")

        except Exception as e:
            self.logger.error(f"Date analyze failed: {str(e)}")
            raise

    def save_report(self, analysis: str) -> str:
        """Save analysis report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            device_ip = self.device_info['host']

            # Ensure correct report directory path is used
            report_path = os.path.join(project_root, 'output', 'reports', f"report_{device_ip}_{timestamp}.md")

            # Ensure directory exists
            os.makedirs(os.path.dirname(report_path), exist_ok=True)

            print(f"\nSaving report:")
            print(f"Reports directory: {os.path.dirname(report_path)}")
            print(f"Report path: {report_path}")

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"# HUAWEI USG12004 Firewall Inspection analysis\n\n")
                f.write(f"## Basic infomation\n")
                f.write(f"- Device IP: {device_ip}\n")
                f.write(f"- Analysis time: {timestamp}\n\n")
                f.write("## The result\n\n")
                f.write(analysis)

            print(f"Report successfully saved to: {report_path}")
            return report_path

        except Exception as e:
            print(f"\nError saving report:")
            print(f"Exception: {str(e)}")
            raise

    def run(self) -> Tuple[str, str]:
        """Run the inspection process"""
        try:
            # Collect data
            config_data = self.collect_data()

            # Save raw data
            raw_config_path = self.save_raw_data(config_data)
            print(f"Original saving path: {raw_config_path}")

            # Analyze data
            analysis_result = self.analyze_data(config_data)

            # Save report
            report_path = self.save_report(analysis_result)
            print(f"Analyzing report saving path: {report_path}")

            return raw_config_path, report_path

        except Exception as e:
            self.logger.error(f"Inspecting failed: {str(e)}")
            raise

    def _format_config_data(self, config_data: Dict[str, Any]) -> str:
        """Format configuration data for analysis"""
        formatted_config = []
        for category, commands in config_data.items():
            formatted_config.append(f"\n=== {category.upper()} ===")
            for cmd, data in commands.items():
                formatted_config.append(f"\n--- {cmd} ---")
                formatted_config.append(data['output'])
        return "\n".join(formatted_config)


def main():
    logger = setup_logger('usg12004_inspection')
    try:
        # Load device configurations
        devices = ConfigLoader.get_devices('firewall')

        if not devices:
            logger.error("Failed to load device configurations")
            return 1

        results = []
        for device in devices:
            try:
                device_ip = device['ip']
                logger.info(f"\nStart to inspect device: {device_ip}")

                # Load device info
                device_info = ConfigLoader.get_device_info(device_ip, 'firewall')
                print(f"Loading device info: {device_info}")

                inspector = USG12004Inspector(device_info)
                raw_config_path, report_path = inspector.run()

                results.append({
                    'ip': device_ip,
                    'status': 'success',
                    'raw_config': raw_config_path,
                    'report': report_path
                })

            except Exception as e:
                logger.error(f"{device_ip} inspecting failed: {str(e)}")
                results.append({
                    'ip': device_ip,
                    'status': 'failed',
                    'error': str(e)
                })

        # 打印巡检结果汇总
        print("\n" + "=" * 50)
        print("Tasks are completed！Summary of results：")
        print("=" * 50)

        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = sum(1 for r in results if r['status'] == 'failed')

        print(f"\nSum of devices: {len(results)}")
        print(f"Num of success: {success_count}")
        print(f"Num of failed: {failed_count}\n")

        for result in results:
            print(f"\nDevice {result['ip']}:")
            if result['status'] == 'success':
                print("status: success")
                print(f"raw config: {result['raw_config']}")
                print(f"report: {result['report']}")
            else:
                print("status: failed")
                print(f"Error: {result['error']}")

        return 0 if failed_count == 0 else 1

    except Exception as e:
        logger.error(f"Tasks are failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())