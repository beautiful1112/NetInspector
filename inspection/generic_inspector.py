import os
import time
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Tuple, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from utils.settings import BASE_DIR, AI_SETTINGS
from connect.device_connector import DeviceConnector
from utils.logger import get_logger
from utils.config_loader import ConfigLoader

class GenericInspector:
    """
    Generic device inspector.
    Uses configuration files (JSON for commands, TXT for prompts) to perform inspections
    on different devices. All specific parameters are passed via external config files.
    """

    def __init__(self, device_info: Dict[str, Any], config: Dict[str, str]):
        self.device_info = device_info
        self.logger = get_logger('generic_inspector')
        self.device_connector = None
        self.config = config

        # 输出环境信息
        self.logger.info("=" * 50)
        self.logger.info("初始化设备检查器...")
        self.logger.info(f"项目根目录: {BASE_DIR}")
        self.logger.info(f"设备信息: {self.device_info['host']}")
        self.logger.info("=" * 50)

        # 确保输出目录存在
        try:
            raw_config_dir = os.path.join(BASE_DIR, 'output', 'raw_configs')
            report_dir = os.path.join(BASE_DIR, 'output', 'reports')
            os.makedirs(raw_config_dir, exist_ok=True)
            os.makedirs(report_dir, exist_ok=True)
            self.logger.info("输出目录验证成功:")
            self.logger.info(f"- 原始配置目录: {raw_config_dir}")
            self.logger.info(f"- 报告目录: {report_dir}")
        except Exception as e:
            self.logger.error(f"创建输出目录失败: {str(e)}")
            raise

        # 加载命令配置
        try:
            commands_file = os.path.join(BASE_DIR,
                                       self.config.get("commands_file", "templates/commands/default_commands.json"))
            self.logger.info(f"正在加载命令配置: {commands_file}")
            with open(commands_file, "r", encoding="utf-8") as f:
                self.commands = json.load(f)
            self.logger.info(f"成功加载命令配置，包含 {len(self.commands)} 个类别")
            for category, cmds in self.commands.items():
                self.logger.info(f"- {category}: {len(cmds)} 个命令")
        except Exception as e:
            self.logger.error(f"加载命令配置失败: {str(e)}")
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
                model_kwargs={"response_format": {"type": "text"}}
            )
            self.logger.info("AI 分析器初始化成功")
        except Exception as e:
            self.logger.error(f"AI 分析器初始化失败: {str(e)}")
            raise

        # 加载提示模板
        try:
            prompt_file = os.path.join(BASE_DIR,
                                     self.config.get("prompt_file", "templates/prompts/default_prompt.txt"))
            self.logger.info(f"正在加载提示模板: {prompt_file}")
            with open(prompt_file, "r", encoding="utf-8") as f:
                self.prompt_template_str = f.read()
            self.logger.info("提示模板加载成功")
        except Exception as e:
            self.logger.error(f"加载提示模板失败: {str(e)}")
            raise

    def collect_data(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """收集设备配置数据"""
        self.logger.info("=" * 50)
        self.logger.info(f"开始收集设备 {self.device_info['host']} 的数据...")
        self.logger.info("=" * 50)
        config_data = {}

        try:
            # 初始化设备连接，添加额外的连接参数
            self.device_connector = DeviceConnector({
                **self.device_info,
                'global_delay_factor': 2,
                'timeout': 60,
                'session_timeout': 60
            })
            self.device_connector.connect()
            self.logger.info(f"成功连接到设备 {self.device_info['host']}")

            # 按类别执行命令
            for category, cmds in self.commands.items():
                self.logger.info("-" * 40)
                self.logger.info(f"开始收集 {category} 类数据...")
                self.logger.info(f"该类别包含 {len(cmds)} 个命令")
                config_data[category] = {}

                for cmd in cmds:
                    try:
                        self.logger.info(f"执行命令: {cmd}")
                        start_time = time.time()
                        output = self.device_connector.send_command(cmd)
                        end_time = time.time()

                        # 计算执行统计信息
                        line_count = len(output.splitlines())
                        execution_time = round(end_time - start_time, 2)

                        config_data[category][cmd] = {
                            'output': output,
                            'line_count': line_count,
                            'timestamp': datetime.now().isoformat(),
                            'execution_time': execution_time
                        }

                        # 输出执行结果统计
                        self.logger.info("命令执行完成:")
                        self.logger.info(f"  - 耗时: {execution_time}秒")
                        self.logger.info(f"  - 采集数据: {line_count}行")

                        # 对特定命令输出概览信息
                        if 'display cpu-usage' in cmd.lower():
                            self.logger.info("CPU使用率概览:")
                            for line in output.splitlines()[:5]:
                                self.logger.info(f"  {line}")
                        elif 'display memory' in cmd.lower():
                            self.logger.info("内存使用率概览:")
                            for line in output.splitlines():
                                if any(key in line.lower() for key in ['total', 'using', 'state']):
                                    self.logger.info(f"  {line}")

                        # 命令间隔
                        time.sleep(0.5)

                    except Exception as e:
                        self.logger.error(f"命令执行失败: {cmd}")
                        self.logger.error(f"错误详情: {str(e)}")
                        config_data[category][cmd] = {
                            'output': f"ERROR: {str(e)}",
                            'line_count': 0,
                            'timestamp': datetime.now().isoformat(),
                            'execution_time': 0
                        }

                self.logger.info(f"完成 {category} 类数据收集，共执行 {len(cmds)} 个命令")

            # 输出总体统计信息
            total_commands = sum(len(cmds) for cmds in self.commands.values())
            total_lines = sum(
                data['line_count']
                for category in config_data.values()
                for data in category.values()
            )

            self.logger.info("=" * 50)
            self.logger.info("数据收集完成统计:")
            self.logger.info(f"- 总命令数: {total_commands}")
            self.logger.info(f"- 总数据行数: {total_lines}")
            self.logger.info(f"- 数据类别: {len(self.commands)}种")
            self.logger.info("=" * 50)
            return config_data

        except Exception as e:
            self.logger.error(f"数据收集失败: {str(e)}", exc_info=True)
            raise
        finally:
            if self.device_connector:
                try:
                    self.device_connector.disconnect()
                    self.logger.info(f"已断开与设备 {self.device_info['host']} 的连接")
                except Exception as e:
                    self.logger.error(f"断开连接时发生错误: {str(e)}")

    def _format_config_data(self, config_data: Dict[str, Any]) -> str:
        """格式化配置数据用于AI分析"""
        try:
            formatted_config = []
            for category, commands in config_data.items():
                formatted_config.append(f"\n=== {category.upper()} ===")
                for cmd, data in commands.items():
                    formatted_config.append(f"\n--- {cmd} ---")
                    if isinstance(data, dict) and 'output' in data:
                        formatted_config.append(str(data['output']))
                    else:
                        self.logger.warning(f"命令 {cmd} (类别 {category}) 的数据格式无效")

            result = "\n".join(formatted_config)
            self.logger.info(f"格式化配置数据完成，总长度: {len(result)} 字符")
            return result
        except Exception as e:
            self.logger.error(f"格式化配置数据失败: {str(e)}")
            raise

    def _split_config_into_chunks(self, config: str, max_chunk_size: int = 75000) -> List[str]:
        """将配置数据分割成更小的块以便进行AI分析"""
        lines = config.splitlines(keepends=True)
        chunks = []
        current_chunk = ""

        for line in lines:
            # 处理超长行
            if len(line) >= max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                for i in range(0, len(line), max_chunk_size):
                    chunks.append(line[i:i + max_chunk_size])
                continue

            # 正常行处理
            if len(current_chunk) + len(line) > max_chunk_size:
                chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += line

        if current_chunk:
            chunks.append(current_chunk)

        # 合并小块
        merged_chunks = []
        for chunk in chunks:
            if merged_chunks and len(chunk) < max_chunk_size * 0.2 and \
                    len(merged_chunks[-1]) + len(chunk) <= max_chunk_size:
                merged_chunks[-1] += chunk
            else:
                merged_chunks.append(chunk)

        # 记录分块信息
        for i, chunk in enumerate(merged_chunks, start=1):
            self.logger.info(f"分块 {i}/{len(merged_chunks)} 大小: {len(chunk)} 字符")

        return merged_chunks

    def _create_chunk_prompt(self, chunk: str, chunk_num: int, total_chunks: int) -> str:
        """为每个配置块创建分析提示"""
        if total_chunks > 1:
            return f"""这是配置的第 {chunk_num}/{total_chunks} 部分。
            请分析这部分配置，重点关注以下方面：
            1. 安全配置问题
            2. 性能隐患
            3. 配置规范性
            4. 潜在风险

            如果发现问题，请详细说明问题及改进建议。
            即使是部分配置，也请具体分析，不要简单回复"等待完整配置"。

            配置内容如下：

            {chunk}
            """
        return self.prompt_template_str.format(config=chunk)

    def _merge_analysis_results(self, results: List[str], total_chunks: int) -> str:
        """合并多个分析结果为完整报告"""
        try:
            # 定义报告章节
            sections = {
                "配置概览": [],
                "安全风险评估": [],
                "性能分析": [],
                "合规性检查": [],
                "改进建议": [],
                "其他发现": []
            }

            # 解析每个分析结果
            for result in results:
                current_section = "其他发现"
                lines = result.strip().split('\n')

                for line in lines:
                    # 检查章节标题
                    if line.startswith('##'):
                        section_name = line.strip('#').strip()
                        if section_name in sections:
                            current_section = section_name
                        continue

                    # 添加内容到当前章节
                    if line.strip():
                        if current_section not in sections:
                            current_section = "其他发现"
                        sections[current_section].append(line.strip())

            # 生成最终报告
            final_report = []
            for section, content in sections.items():
                if content:
                    final_report.append(f"\n## {section}\n")
                    # 去重并保持顺序
                    unique_content = []
                    for line in content:
                        if line not in unique_content:
                            unique_content.append(line)
                    final_report.extend(unique_content)

            report = "\n".join(final_report)
            self.logger.info(f"成功合并 {len(results)} 个分析结果")
            self.logger.info(f"最终报告长度: {len(report)} 字符")

            return report

        except Exception as e:
            self.logger.error(f"合并分析结果失败: {str(e)}")
            raise

    def analyze_data(self, config_data: Dict[str, Any]) -> str:
        """分析配置数据"""
        try:
            self.logger.info("开始分析设备数据...")
            formatted_config = self._format_config_data(config_data)
            total_length = len(formatted_config)
            self.logger.info(f"配置总长度: {total_length} 字符")

            # 分块处理
            chunks = self._split_config_into_chunks(formatted_config)
            total_chunks = len(chunks)
            self.logger.info(f"配置数据分为 {total_chunks} 个部分")

            analysis_results = []
            for i, chunk in enumerate(chunks, 1):
                self.logger.info(f"分析第 {i}/{total_chunks} 部分 (大小: {len(chunk)} 字符)")
                chunk_prompt = self._create_chunk_prompt(chunk, i, total_chunks)

                # 重试机制
                for attempt in range(3):
                    try:
                        if attempt > 0:
                            self.logger.info(f"第 {i} 部分第 {attempt + 1} 次重试")
                            time.sleep(5 * (attempt + 1))

                        response = self.llm.invoke(chunk_prompt)
                        content = response.content if hasattr(response, 'content') else str(response)

                        if content and len(content.strip()) > 100:
                            self.logger.info(f"第 {i}/{total_chunks} 部分分析完成 (响应长度: {len(content)})")
                            analysis_results.append(content)
                            break
                        else:
                            raise ValueError(f"AI响应内容过短或无效: {content[:100]}...")

                    except Exception as e:
                        self.logger.error(f"第 {i} 部分第 {attempt + 1} 次分析失败: {str(e)}")
                        if attempt == 2:  # 最后一次重试失败
                            raise

            if not analysis_results:
                raise ValueError("未能获得任何有效的分析结果")

            final_analysis = self._merge_analysis_results(analysis_results, total_chunks)
            self.logger.info(f"分析完成，最终报告长度: {len(final_analysis)} 字符")
            return final_analysis

        except Exception as e:
            self.logger.error(f"数据分析失败: {str(e)}", exc_info=True)
            raise

    def save_raw_data(self, config_data: Dict[str, Any]) -> str:
            """保存原始配置数据"""
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                device_ip = self.device_info['host']
                file_path = os.path.join(BASE_DIR, 'output', 'raw_configs',
                                         f"raw_config_{device_ip}_{timestamp}.txt")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                self.logger.info("正在保存原始配置:")
                self.logger.info(f"输出目录: {os.path.dirname(file_path)}")
                self.logger.info(f"文件路径: {file_path}")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# 设备配置数据\n")
                    f.write(f"# 设备IP: {device_ip}\n")
                    f.write(f"# 采集时间: {timestamp}\n\n")

                    for category, commands in config_data.items():
                        f.write(f"\n{'=' * 20} {category.upper()} {'=' * 20}\n")
                        for cmd, data in commands.items():
                            f.write(f"\n{'-' * 10} {cmd} {'-' * 10}\n")
                            f.write(f"采集时间: {data['timestamp']}\n")
                            f.write(f"数据行数: {data['line_count']}\n")
                            f.write(f"执行耗时: {data['execution_time']}秒\n")
                            f.write(f"命令输出:\n{data['output']}\n")

                self.logger.info(f"原始配置成功保存至: {file_path}")
                return file_path

            except Exception as e:
                self.logger.error("保存原始配置失败:")
                self.logger.error(f"错误详情: {str(e)}", exc_info=True)
                raise

    def save_report(self, analysis: str) -> str:
            """保存分析报告"""
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                device_ip = self.device_info['host']
                report_path = os.path.join(BASE_DIR, 'output', 'reports', f"report_{device_ip}_{timestamp}.md")
                os.makedirs(os.path.dirname(report_path), exist_ok=True)

                self.logger.info("正在保存分析报告:")
                self.logger.info(f"报告目录: {os.path.dirname(report_path)}")
                self.logger.info(f"报告路径: {report_path}")

                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(f"# 设备配置分析报告\n\n")
                    f.write(f"## 基本信息\n")
                    f.write(f"- 设备IP: {device_ip}\n")
                    f.write(f"- 设备类型: {self.device_info.get('device_type', 'Unknown')}\n")
                    f.write(f"- 分析时间: {timestamp}\n\n")
                    f.write("## 分析结果\n\n")
                    f.write(analysis)

                self.logger.info(f"分析报告成功保存至: {report_path}")
                return report_path

            except Exception as e:
                self.logger.error("保存分析报告失败:")
                self.logger.error(f"错误详情: {str(e)}", exc_info=True)
                raise

    def run(self) -> Tuple[str, str]:
            """执行完整的检查流程"""
            try:
                self.logger.info("=" * 50)
                self.logger.info("开始执行设备检查流程...")
                self.logger.info("=" * 50)

                # 收集数据
                config_data = self.collect_data()
                raw_config_path = self.save_raw_data(config_data)
                self.logger.info(f"原始配置保存路径: {raw_config_path}")

                # 分析数据
                analysis_result = self.analyze_data(config_data)
                report_path = self.save_report(analysis_result)
                self.logger.info(f"分析报告保存路径: {report_path}")

                return raw_config_path, report_path

            except Exception as e:
                self.logger.error(f"设备检查失败: {str(e)}", exc_info=True)
                raise

    # 异步检查单个设备
async def inspect_device_async(device: dict) -> dict:
        """异步执行单个设备的检查"""
        logger = get_logger("async_inspection")
        loop = asyncio.get_running_loop()
        device_ip = device["ip"]
        device_type = device.get("type", "generic")

        logger.info(f"开始检查设备: {device_ip}", extra={'print_console': True})

        try:
            # 获取设备信息
            device_info = ConfigLoader.get_device_info(device_ip, device_type)

            # 准备配置
            config = {
                "commands_file": f"templates/commands/{device_type}_commands.json",
                "prompt_file": f"templates/prompts/{device_type}_prompt.txt"
            }

            # 创建检查器实例
            inspector = GenericInspector(device_info, config)

            # 在执行器中运行检查
            raw_config, report = await loop.run_in_executor(None, inspector.run)

            return {
                "ip": device_ip,
                "type": device_type,
                "status": "success",
                "raw_config": raw_config,
                "report": report
            }

        except Exception as e:
            logger.error(f"设备 {device_ip} 检查失败: {str(e)}", exc_info=True, extra={'print_console': True})
            return {
                "ip": device_ip,
                "type": device_type,
                "status": "failed",
                "error": str(e)
            }

    # 异步批量检查入口
async def batch_inspection_async(device_type: str) -> List[Dict]:
        """异步执行批量设备检查"""
        logger = get_logger("batch_inspection")

        try:
            # 获取设备列表
            devices = ConfigLoader.get_devices(device_type)
            if not devices:
                logger.info(f"未找到 {device_type} 类型的设备配置！", extra={'print_console': True})
                return []

            # 创建异步任务
            tasks = [inspect_device_async(device) for device in devices]
            results = await asyncio.gather(*tasks, return_exceptions=False)

            # 统计结果
            success_count = sum(1 for r in results if r["status"] == "success")
            failed_count = sum(1 for r in results if r["status"] == "failed")

            # 输出汇总信息
            logger.info("=" * 50, extra={'print_console': True})
            logger.info("检查任务完成！结果汇总：", extra={'print_console': True})
            logger.info("=" * 50, extra={'print_console': True})
            logger.info(f"总设备数: {len(results)}", extra={'print_console': True})
            logger.info(f"成功数量: {success_count}", extra={'print_console': True})
            logger.info(f"失败数量: {failed_count}", extra={'print_console': True})

            # 输出详细结果
            for result in results:
                if result["status"] == "success":
                    logger.info(f"设备 {result['ip']}:", extra={'print_console': True})
                    logger.info(f"- 状态: 成功", extra={'print_console': True})
                    logger.info(f"- 原始配置: {result['raw_config']}", extra={'print_console': True})
                    logger.info(f"- 分析报告: {result['report']}", extra={'print_console': True})
                else:
                    logger.info(f"设备 {result['ip']}:", extra={'print_console': True})
                    logger.info(f"- 状态: 失败", extra={'print_console': True})
                    logger.info(f"- 错误信息: {result['error']}", extra={'print_console': True})

            return results

        except Exception as e:
            logger.error(f"批量检查任务执行失败: {str(e)}", exc_info=True, extra={'print_console': True})
            raise