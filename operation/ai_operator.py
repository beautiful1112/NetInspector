"""
ai_operator.py

该模块实现了基于 AI 的设备操作流程：
1. 根据用户输入构造 prompt，并调用 AI 返回一个 JSON 格式的结果，
   其中包含：
      - "device": 目标设备名称（例如 "huawei-usg-01"）
      - "response": AI 给出的操作说明
      - "commands": 待在设备上执行的命令列表
2. 通过返回的设备名称，利用 ConfigLoader 获取设备配置信息。
3. 使用 DeviceConnector 连接目标设备，并执行 AI 返回的命令。
4. 如果执行过程中有命令出错，则构造重试 prompt，调用 AI 获取修正后的命令再次执行。
"""

import json
import time
from fastapi import HTTPException
from langchain.llms import OpenAI
from utils import settings
from utils.logger import get_logger
from utils.config_loader import ConfigLoader
from connect.device_connector import DeviceConnector

logger = get_logger(__name__)


def build_prompt(user_input: str) -> str:
    """
    根据用户输入构造 prompt，要求 AI 返回一个 JSON 对象，
    JSON 中应包含：
      - "device": 目标设备名称（如 "huawei-usg-01"）
      - "response": 针对此次操作的说明
      - "commands": 用于获取设备信息的命令列表
    """
    template = (
        "You are an intelligent network operator. The user provided the following instruction: '{instruction}'.\n"
        "Based on your analysis, please output a JSON object with the following keys:\n"
        "  - 'device': the target device name (e.g., 'huawei-usg-01') as defined in the device configuration.\n"
        "  - 'response': a natural language explanation of the diagnostic actions.\n"
        "  - 'commands': an array of shell commands that should be executed on the device to obtain the requested information.\n"
        "Ensure the JSON is properly formatted."
    )
    return template.format(instruction=user_input)


def invoke_ai(prompt: str) -> dict:
    """
    调用 AI 模型（使用 LangChain 的 OpenAI 包装器）并解析返回结果，将其转换为 JSON 对象。
    """
    ai_settings = settings.AI_SETTINGS.get('deepseek', {})
    openai_api_key = ai_settings.get('api_key')
    try:
        llm = OpenAI(api_key=openai_api_key, model=ai_settings.get('model'))
        ai_output = llm(prompt)
        result = json.loads(ai_output)
        return result
    except Exception as e:
        logger.error("Error invoking AI: %s", str(e), extra={"print_console": True})
        raise HTTPException(status_code=500, detail="AI response parsing failed.")


def run_ai_operation(user_input: str) -> dict:
    """
    根据用户输入执行完整的 AI 操作流程：
      1. 构造 prompt 并调用 AI 模型获取结果；
      2. 解析返回结果中的设备名称、操作说明及命令列表；
      3. 利用 ConfigLoader 查找设备配置信息；
      4. 使用 DeviceConnector 连接设备并执行命令；
      5. 若执行命令出错，则构造重试 prompt，请求 AI 返回修正后的命令，再次执行。
    """
    # 构造 prompt 并调用 AI
    prompt = build_prompt(user_input)
    ai_result = invoke_ai(prompt)
    response_text = ai_result.get("response", "")
    target_device_name = ai_result.get("device")
    commands = ai_result.get("commands", [])

    if not target_device_name:
        raise HTTPException(status_code=400, detail="Target device not specified by AI.")

    # 从 firewall.yaml 中获取设备列表，匹配目标设备
    devices = ConfigLoader.get_devices("firewall")
    target_device = None
    for dev in devices:
        if dev.get("name") == target_device_name:
            target_device = dev
            break

    if not target_device:
        raise HTTPException(status_code=404, detail=f"Device '{target_device_name}' not found in configuration.")

    # 根据设备 IP 获取连接所需信息
    try:
        device_info = ConfigLoader.get_device_info(target_device.get("ip"), "firewall")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    command_outputs = []
    connector = DeviceConnector(device_info)
    try:
        connector.connect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection to device {target_device_name} failed: {str(e)}")

    # 执行 AI 返回的每条命令
    for command in commands:
        try:
            if not connector.check_connection():
                connector.connect()
            output = connector.send_command(command)
            command_outputs.append({"command": command, "output": output})
        except Exception as e:
            logger.error("Error executing command '%s': %s", command, str(e), extra={"print_console": True})
            # 构造重试 prompt，请求修正后的命令
            retry_prompt = (
                prompt +
                f"\nNote: The previous command '{command}' failed with error: {str(e)}. Please provide a corrected command."
            )
            try:
                ai_retry_result = invoke_ai(retry_prompt)
                corrected_commands = ai_retry_result.get("commands", [])
                if corrected_commands:
                    corrected_command = corrected_commands[0]
                    try:
                        output = connector.send_command(corrected_command)
                        command_outputs.append({
                            "command": corrected_command,
                            "output": output,
                            "correction": True
                        })
                    except Exception as retry_e:
                        command_outputs.append({
                            "command": command,
                            "output": f"Failed after retry: {str(retry_e)}",
                            "error": str(retry_e)
                        })
                else:
                    command_outputs.append({
                        "command": command,
                        "output": "No corrected command provided by AI."
                    })
            except Exception as ai_retry_e:
                command_outputs.append({
                    "command": command,
                    "output": f"Retry failed: {str(ai_retry_e)}",
                    "error": str(ai_retry_e)
                })
    connector.disconnect()

    return {
        "response": response_text,
        "device": target_device_name,
        "commands_executed": command_outputs
    }


if __name__ == "__main__":
    # 此处仅用于命令行测试，实际部署时由 API 传入用户指令
    import sys
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = "我想要你登录huawei-usg-01进去，并获取一下设备的CPU信息和接口信息"
    result = run_ai_operation(user_input)
    print(json.dumps(result, indent=2, ensure_ascii=False))