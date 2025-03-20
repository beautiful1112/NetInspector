import os
import time
import json
from datetime import datetime
from typing import Dict, Any, Tuple, List
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from utils.logger import get_logger
from utils.config_loader import ConfigLoader
import yaml

class GenericInspector:
    """
    Generic device inspector.
    Uses configuration files (JSON for commands, TXT for prompts) to perform inspections
    on different devices. All specific parameters are passed via external config files.
    """

    def __init__(self, device_info: Dict[str, Any], config: Dict[str, str]):
        self.device_info = device_info
        self.logger = get_logger('generic_inspector')
        self.config = config
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Set default chunk size for AI analysis
        self.chunk_size = config.get('chunk_size', 75000)

        # 记录初始化信息
        self.logger.info(f"Initializing inspector for device: {device_info}")
        self.logger.info(f"Config: {config}")
        self.logger.info(f"Project root: {self.project_root}")
        self.logger.info(f"Analysis chunk size: {self.chunk_size}")

        # 加载设置
        try:
            with open(os.path.join(self.project_root, "utils", "settings.yaml"), 'r', encoding='utf-8') as f:
                self.settings = yaml.safe_load(f)
            self.logger.info("Settings loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load settings: {str(e)}")
            raise

        # Initialize Nornir
        try:
            self.nr = InitNornir(
                config_file=os.path.join(self.project_root, "config", "config.yaml")
            )
            self.logger.info("Nornir initialization successful")
        except Exception as e:
            self.logger.error(f"Nornir initialization failed: {str(e)}")
            raise

        # Output environment information
        self.logger.info("=" * 50)
        self.logger.info("Initializing device inspector...")
        self.logger.info(f"Project root directory: {self.project_root}")
        self.logger.info(f"Device information: {self.device_info['host']}")
        self.logger.info("=" * 50)

        # Ensure output directories exist
        try:
            raw_config_dir = os.path.join(self.project_root, self.settings['directories']['raw_configs'])
            report_dir = os.path.join(self.project_root, self.settings['directories']['reports'])
            os.makedirs(raw_config_dir, exist_ok=True)
            os.makedirs(report_dir, exist_ok=True)
            self.logger.info("Output directory validation successful:")
            self.logger.info(f"- Raw config directory: {raw_config_dir}")
            self.logger.info(f"- Report directory: {report_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create output directories: {str(e)}")
            raise

        # Load command configuration
        try:
            commands_file = os.path.join(self.project_root, self.config["commands_file"])
            self.logger.info(f"Loading command configuration from: {commands_file}")
            
            if not os.path.exists(commands_file):
                raise FileNotFoundError(f"Commands file not found: {commands_file}")
            
            with open(commands_file, "r", encoding="utf-8") as f:
                self.commands = json.load(f)
            self.logger.info(f"Successfully loaded command configuration")
        except Exception as e:
            self.logger.error(f"Failed to load command configuration: {str(e)}")
            raise

        # Initialize AI analyzer
        try:
            ai_config = self.settings['ai_config']
            self.llm = ChatOpenAI(
                base_url=ai_config['api_base'],
                api_key=ai_config['api_key'],
                model=ai_config['model'],
                temperature=0,
                request_timeout=180,
                max_retries=3,
                model_kwargs={"response_format": {"type": "text"}}
            )
            self.logger.info("AI analyzer initialization successful")
        except Exception as e:
            self.logger.error(f"AI analyzer initialization failed: {str(e)}")
            raise

        # Load prompt template
        try:
            prompt_file = os.path.join(self.project_root, self.config["prompt_file"])
            self.logger.info(f"Loading prompt template from: {prompt_file}")
            
            if not os.path.exists(prompt_file):
                raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
            
            with open(prompt_file, "r", encoding="utf-8") as f:
                self.prompt_template_str = f.read()
            self.logger.info("Successfully loaded prompt template")
        except Exception as e:
            self.logger.error(f"Failed to load prompt template: {str(e)}")
            raise

    def execute_commands(self, task: Task, commands: List[str]) -> Result:
        """Execute commands using Nornir task"""
        results = {}
        for cmd in commands:
            try:
                result = task.run(
                    task=netmiko_send_command,
                    command_string=cmd,
                    enable=True
                )
                output = result[0].result
                results[cmd] = {
                    'output': output,
                    'line_count': len(output.splitlines()),
                    'timestamp': datetime.now().isoformat(),
                    'execution_time': result[0].elapsed_time
                }
                self.logger.info(f"Command executed successfully: {cmd}")
            except Exception as e:
                self.logger.error(f"Command execution failed: {cmd}")
                self.logger.error(f"Error details: {str(e)}")
                results[cmd] = {
                    'output': f"ERROR: {str(e)}",
                    'line_count': 0,
                    'timestamp': datetime.now().isoformat(),
                    'execution_time': 0
                }
        return Result(
            host=task.host,
            result=results
        )

    def collect_data(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Collect device configuration data using Nornir"""
        self.logger.info("=" * 50)
        self.logger.info(f"Starting data collection for device {self.device_info['host']}...")
        self.logger.info("=" * 50)

        try:
            # Filter target device
            target = self.nr.filter(name=self.device_info['host'])
            config_data = {}

            # Execute commands by category
            for category, cmds in self.commands.items():
                self.logger.info("-" * 40)
                self.logger.info(f"Starting collection of {category} data...")
                self.logger.info(f"Category contains {len(cmds)} commands")

                # Execute commands and get results
                result = target.run(
                    task=self.execute_commands,
                    commands=cmds
                )
                
                # Process results
                for host, host_data in result.items():
                    if host_data.failed:
                        self.logger.error(f"Device {host} command execution failed")
                        continue
                    config_data[category] = host_data.result

            # Output statistics
            total_commands = sum(len(cmds) for cmds in self.commands.values())
            total_lines = sum(
                data['line_count']
                for category in config_data.values()
                for data in category.values()
            )

            self.logger.info("=" * 50)
            self.logger.info("Data collection completed statistics:")
            self.logger.info(f"- Total commands: {total_commands}")
            self.logger.info(f"- Total data lines: {total_lines}")
            self.logger.info(f"- Data categories: {len(self.commands)}")
            self.logger.info("=" * 50)

            return config_data

        except Exception as e:
            self.logger.error(f"Data collection failed: {str(e)}", exc_info=True)
            raise

    def _format_config_data(self, config_data: Dict[str, Any]) -> str:
        """Format configuration data for AI analysis"""
        try:
            formatted_config = []
            for category, commands in config_data.items():
                formatted_config.append(f"\n=== {category.upper()} ===")
                for cmd, data in commands.items():
                    formatted_config.append(f"\n--- {cmd} ---")
                    if isinstance(data, dict) and 'output' in data:
                        formatted_config.append(str(data['output']))
                    else:
                        self.logger.warning(f"Command {cmd} (category {category}) data format invalid")

            result = "\n".join(formatted_config)
            self.logger.info(f"Configuration data formatting completed, total length: {len(result)} characters")
            return result
        except Exception as e:
            self.logger.error(f"Configuration data formatting failed: {str(e)}")
            raise

    def _split_config_into_chunks(self, config: str) -> List[str]:
        """Split configuration data into smaller chunks for AI analysis"""
        lines = config.splitlines(keepends=True)
        chunks = []
        current_chunk = ""

        for line in lines:
            # Handle long lines
            if len(line) >= self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                for i in range(0, len(line), self.chunk_size):
                    chunks.append(line[i:i + self.chunk_size])
                continue

            # Normal line processing
            if len(current_chunk) + len(line) > self.chunk_size:
                chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += line

        if current_chunk:
            chunks.append(current_chunk)

        # Merge small chunks
        merged_chunks = []
        for chunk in chunks:
            if merged_chunks and len(chunk) < self.chunk_size * 0.2 and \
                    len(merged_chunks[-1]) + len(chunk) <= self.chunk_size:
                merged_chunks[-1] += chunk
            else:
                merged_chunks.append(chunk)

        # Record chunking information
        for i, chunk in enumerate(merged_chunks, start=1):
            self.logger.info(f"Chunk {i}/{len(merged_chunks)} size: {len(chunk)} characters")

        return merged_chunks

    def _create_chunk_prompt(self, chunk: str, chunk_num: int, total_chunks: int) -> str:
        """Create analysis prompt for each configuration chunk"""
        if total_chunks > 1:
            return f"""This is the {chunk_num}/{total_chunks} part of the configuration.
            Please analyze this part of the configuration, focusing on the following aspects:
            1. Security configuration issues
            2. Performance issues
            3. Configuration compliance
            4. Potential risks

            If you find issues, please provide detailed explanations and improvement suggestions.
            Even if it's only part of the configuration, please analyze it specifically, don't just reply "waiting for complete configuration".

            Configuration content below:

            {chunk}
            """
        return self.prompt_template_str.format(config=chunk)

    def _merge_analysis_results(self, results: List[str], total_chunks: int) -> str:
        """Merge multiple analysis results into a complete report"""
        try:
            # Define report sections
            sections = {
                "Configuration Overview": [],
                "Security Risk Assessment": [],
                "Performance Analysis": [],
                "Compliance Check": [],
                "Improvement Suggestions": [],
                "Other Findings": []
            }

            # Parse each analysis result
            for result in results:
                current_section = "Other Findings"
                lines = result.strip().split('\n')

                for line in lines:
                    # Check section title
                    if line.startswith('##'):
                        section_name = line.strip('#').strip()
                        if section_name in sections:
                            current_section = section_name
                        continue

                    # Add content to current section
                    if line.strip():
                        if current_section not in sections:
                            current_section = "Other Findings"
                        sections[current_section].append(line.strip())

            # Generate final report
            final_report = []
            for section, content in sections.items():
                if content:
                    final_report.append(f"\n## {section}\n")
                    # Remove duplicates and maintain order
                    unique_content = []
                    for line in content:
                        if line not in unique_content:
                            unique_content.append(line)
                    final_report.extend(unique_content)

            report = "\n".join(final_report)
            self.logger.info(f"Successfully merged {len(results)} analysis results")
            self.logger.info(f"Final report length: {len(report)} characters")

            return report

        except Exception as e:
            self.logger.error(f"Failed to merge analysis results: {str(e)}")
            raise

    def analyze_data(self, config_data: Dict[str, Any]) -> str:
        """Analyze configuration data"""
        try:
            self.logger.info("Starting data analysis for device...")
            formatted_config = self._format_config_data(config_data)
            total_length = len(formatted_config)
            self.logger.info(f"Configuration total length: {total_length} characters")

            # Chunk processing
            chunks = self._split_config_into_chunks(formatted_config)
            total_chunks = len(chunks)
            self.logger.info(f"Configuration data divided into {total_chunks} parts")

            analysis_results = []
            for i, chunk in enumerate(chunks, 1):
                self.logger.info(f"Analyzing {i}/{total_chunks} part (size: {len(chunk)} characters)")
                chunk_prompt = self._create_chunk_prompt(chunk, i, total_chunks)

                # Retry mechanism
                for attempt in range(3):
                    try:
                        if attempt > 0:
                            self.logger.info(f"{i} part {attempt + 1}th retry")
                            time.sleep(5 * (attempt + 1))

                        response = self.llm.invoke(chunk_prompt)
                        content = response.content if hasattr(response, 'content') else str(response)

                        if content and len(content.strip()) > 100:
                            self.logger.info(f"{i}/{total_chunks} part analysis completed (response length: {len(content)})")
                            analysis_results.append(content)
                            break
                        else:
                            raise ValueError(f"AI response too short or invalid: {content[:100]}...")

                    except Exception as e:
                        self.logger.error(f"{i} part {attempt + 1}th analysis failed: {str(e)}")
                        if attempt == 2:  # Last retry failed
                            raise

            if not analysis_results:
                raise ValueError("No valid analysis results obtained")

            final_analysis = self._merge_analysis_results(analysis_results, total_chunks)
            self.logger.info(f"Analysis completed, final report length: {len(final_analysis)} characters")
            return final_analysis

        except Exception as e:
            self.logger.error(f"Data analysis failed: {str(e)}", exc_info=True)
            raise

    def save_raw_data(self, config_data: Dict[str, Any]) -> str:
        """Save raw configuration data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            device_ip = self.device_info['host']
            file_path = os.path.join(self.project_root, 
                                   self.settings['directories']['raw_configs'],
                                   f"raw_config_{device_ip}_{timestamp}.txt")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            self.logger.info("Saving raw configuration:")
            self.logger.info(f"Output directory: {os.path.dirname(file_path)}")
            self.logger.info(f"File path: {file_path}")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# Device Configuration Data\n")
                f.write(f"# Device IP: {device_ip}\n")
                f.write(f"# Collection Time: {timestamp}\n\n")

                for category, commands in config_data.items():
                    f.write(f"\n{'=' * 20} {category.upper()} {'=' * 20}\n")
                    for cmd, data in commands.items():
                        f.write(f"\n{'-' * 10} {cmd} {'-' * 10}\n")
                        f.write(f"Collection Time: {data['timestamp']}\n")
                        f.write(f"Data Lines: {data['line_count']}\n")
                        f.write(f"Execution Time: {data['execution_time']} seconds\n")
                        f.write(f"Command Output:\n{data['output']}\n")

            self.logger.info(f"Raw configuration saved to: {file_path}")
            return file_path

        except Exception as e:
            self.logger.error("Failed to save raw configuration:")
            self.logger.error(f"Error details: {str(e)}", exc_info=True)
            raise

    def save_report(self, analysis: str) -> str:
        """Save analysis report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            device_ip = self.device_info['host']
            report_path = os.path.join(self.project_root, 
                                     self.settings['directories']['reports'],
                                     f"report_{device_ip}_{timestamp}.md")
            os.makedirs(os.path.dirname(report_path), exist_ok=True)

            self.logger.info("Saving analysis report:")
            self.logger.info(f"Report directory: {os.path.dirname(report_path)}")
            self.logger.info(f"Report path: {report_path}")

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"# Device Configuration Analysis Report\n\n")
                f.write(f"## Basic Information\n")
                f.write(f"- Device IP: {device_ip}\n")
                f.write(f"- Device Type: {self.device_info.get('device_type', 'Unknown')}\n")
                f.write(f"- Analysis Time: {timestamp}\n\n")
                f.write("## Analysis Results\n\n")
                f.write(analysis)

            self.logger.info(f"Analysis report saved to: {report_path}")
            return report_path

        except Exception as e:
            self.logger.error("Failed to save analysis report:")
            self.logger.error(f"Error details: {str(e)}", exc_info=True)
            raise

    def run(self) -> Tuple[str, str]:
        """Execute complete inspection process"""
        try:
            self.logger.info("=" * 50)
            self.logger.info("Starting device inspection process...")
            self.logger.info("=" * 50)

            # Collect data
            config_data = self.collect_data()
            raw_config_path = self.save_raw_data(config_data)
            self.logger.info(f"Raw configuration save path: {raw_config_path}")

            # Analyze data
            analysis_result = self.analyze_data(config_data)
            report_path = self.save_report(analysis_result)
            self.logger.info(f"Analysis report save path: {report_path}")

            return raw_config_path, report_path

        except Exception as e:
            self.logger.error(f"Device inspection failed: {str(e)}", exc_info=True)
            raise

    # Asynchronous inspection of a single device
async def inspect_device_async(device: dict) -> dict:
    """Asynchronous execution of single device inspection"""
    logger = get_logger("async_inspection")
    loop = asyncio.get_running_loop()
    device_ip = device["ip"]
    device_type = device.get("type", "generic")

    logger.info(f"Starting device inspection: {device_ip}", extra={'print_console': True})

    try:
        # Get device information
        device_info = ConfigLoader.get_device_info(device_ip, device_type)

        # Prepare configuration
        config = {
            "commands_file": f"templates/commands/{device_type}_commands.json",
            "prompt_file": f"templates/prompts/{device_type}_prompt.txt"
        }

        # Create inspector instance
        inspector = GenericInspector(device_info, config)

        # Run inspection in executor
        raw_config, report = await loop.run_in_executor(None, inspector.run)

        return {
            "ip": device_ip,
            "type": device_type,
            "status": "success",
            "raw_config": raw_config,
            "report": report
        }

    except Exception as e:
        logger.error(f"Device {device_ip} inspection failed: {str(e)}", exc_info=True, extra={'print_console': True})
        return {
            "ip": device_ip,
            "type": device_type,
            "status": "failed",
            "error": str(e)
        }

    # Asynchronous batch inspection entry
async def batch_inspection_async(device_type: str) -> List[Dict]:
    """Asynchronous execution of batch device inspection"""
    logger = get_logger("batch_inspection")

    try:
        # Get device list
        devices = ConfigLoader.get_devices(device_type)
        if not devices:
            logger.info(f"No {device_type} type device configuration found!", extra={'print_console': True})
            return []

        # Create asynchronous tasks
        tasks = [inspect_device_async(device) for device in devices]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        # Statistics
        success_count = sum(1 for r in results if r["status"] == "success")
        failed_count = sum(1 for r in results if r["status"] == "failed")

        # Output summary information
        logger.info("=" * 50, extra={'print_console': True})
        logger.info("Inspection task completed! Result summary:", extra={'print_console': True})
        logger.info("=" * 50, extra={'print_console': True})
        logger.info(f"Total device count: {len(results)}", extra={'print_console': True})
        logger.info(f"Success count: {success_count}", extra={'print_console': True})
        logger.info(f"Failed count: {failed_count}", extra={'print_console': True})

        # Output detailed results
        for result in results:
            if result["status"] == "success":
                logger.info(f"Device {result['ip']}:", extra={'print_console': True})
                logger.info(f"- Status: Success", extra={'print_console': True})
                logger.info(f"- Raw configuration: {result['raw_config']}", extra={'print_console': True})
                logger.info(f"- Analysis report: {result['report']}", extra={'print_console': True})
            else:
                logger.info(f"Device {result['ip']}:", extra={'print_console': True})
                logger.info(f"- Status: Failed", extra={'print_console': True})
                logger.info(f"- Error information: {result['error']}", extra={'print_console': True})

        return results

    except Exception as e:
        logger.error(f"Batch inspection task execution failed: {str(e)}", exc_info=True, extra={'print_console': True})
        raise