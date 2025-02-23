# api/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel  # 添加这个导入
from operation.ai_operator import run_ai_operation
from inspection.generic_inspector import GenericInspector
from utils.config_loader import ConfigLoader
from utils.settings import OUTPUT_DIRS, BASE_DIR
from utils.excel_to_yaml import excel_to_yaml
import os
import shutil
import json
import yaml
from typing import Dict, List, Optional
from datetime import datetime
from utils.logger import get_logger

# Configure logging

logger = get_logger(__name__)

app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost:5173",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AICommandRequest(BaseModel):
    command: str


class InspectionRequest(BaseModel):
    deviceYaml: str
    credentialYaml: str
    commandJson: str
    promptTxt: str

# File upload endpoints
@app.post("/api/upload/excel")
async def upload_excel(file: UploadFile = File(...)):
    try:
        file_path = os.path.join("config", file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return JSONResponse(content={"message": f"Excel file {file.filename} uploaded successfully", "path": file_path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/excel-to-yaml")  # 新增接口
async def upload_excel_to_yaml(file: UploadFile = File(...)):
    """
    Upload an Excel file and convert it to YAML files, saving to config directory.

    Args:
        file: Excel file to upload

    Returns:
        JSON response with success message or error
    """
    try:
        # Read file content as bytes
        excel_data = await file.read()
        yaml_file_path, error_message = excel_to_yaml(excel_data)
        if error_message:
            raise HTTPException(status_code=400, detail=error_message)
        return JSONResponse(content={"message": f"Excel converted to YAML successfully, files saved at {yaml_file_path}", "path": yaml_file_path})
    except Exception as e:
        logger.error(f"Error converting Excel to YAML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload/credential")
async def upload_credential(file: UploadFile = File(...)):
    try:
        # 验证文件类型
        if not file.filename.endswith(('.yaml', '.yml')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only YAML files are allowed."
            )

        # 确保目录存在
        upload_dir = os.path.join("config")
        os.makedirs(upload_dir, exist_ok=True)

        # 生成安全的文件名
        file_path = os.path.join(upload_dir, file.filename)

        # 保存文件
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save file")

        return JSONResponse(
            content={
                "message": f"YAML credential file {file.filename} uploaded successfully",
                "path": file_path
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/commands")
async def upload_commands(file: UploadFile = File(...)):
    try:
        file_path = os.path.join("templates/commands", file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return JSONResponse(content={"message": f"JSON commands file {file.filename} uploaded successfully", "path": file_path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/prompt")
async def upload_prompt(file: UploadFile = File(...)):
    try:
        file_path = os.path.join("templates/prompts", file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return JSONResponse(content={"message": f"TXT prompt file {file.filename} uploaded successfully", "path": file_path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Inspection endpoint
@app.post("/api/inspection/start")
async def start_inspection(request: InspectionRequest):
    """启动设备检查流程"""
    logger.info("=" * 50)
    logger.info("收到设备检查请求")
    logger.info(f"请求参数: {request.dict()}")
    logger.info("=" * 50)

    try:
        # 提取设备类型（从deviceYaml文件名）
        device_type = request.deviceYaml.split('/')[-1].replace('.yaml', '')
        logger.info(f"设备类型: {device_type}")

        # 获取设备列表
        try:
            devices = ConfigLoader.get_devices(device_type)
            if not devices:
                logger.error(f"未找到设备类型 {device_type} 的配置")
                raise HTTPException(
                    status_code=404,
                    detail=f"未找到设备类型: {device_type}"
                )
            logger.info(f"找到 {len(devices)} 个设备配置")

        except Exception as e:
            logger.error(f"获取设备列表失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"获取设备列表失败: {str(e)}"
            )

        # 检查所需文件是否存在
        required_files = {
            'commands': os.path.join(BASE_DIR, request.commandJson),
            'prompt': os.path.join(BASE_DIR, request.promptTxt)
        }

        for file_type, file_path in required_files.items():
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                raise HTTPException(
                    status_code=404,
                    detail=f"找不到{file_type}文件: {file_path}"
                )

        # 获取第一个设备的详细信息
        try:
            first_device = devices[0]
            device_info = ConfigLoader.get_device_info(first_device['ip'], device_type)
            logger.info(f"已获取设备信息: {first_device['ip']}")

        except Exception as e:
            logger.error(f"获取设备信息失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"获取设备信息失败: {str(e)}"
            )

        # 准备检查配置
        config = {
            "commands_file": request.commandJson,
            "prompt_file": request.promptTxt
        }

        try:
            # 创建检查器实例
            inspector = GenericInspector(device_info, config)
            logger.info("检查器初始化成功")

            # 执行检查
            raw_config_path, report_path = inspector.run()
            logger.info("检查完成")
            logger.info(f"原始配置保存路径: {raw_config_path}")
            logger.info(f"报告保存路径: {report_path}")

            # 获取最新日志
            log_file = os.path.join(BASE_DIR, "logs", f"generic_inspector_{datetime.now().strftime('%Y%m%d')}.log")
            recent_logs = []
            if os.path.exists(log_file):
                with open(log_file, "r", encoding='utf-8') as f:
                    # 获取最后20行有意义的日志（非空行）
                    logs = f.readlines()
                    recent_logs = [log.strip() for log in logs[-30:] if log.strip()][-20:]

            # 返回结果
            return JSONResponse(
                content={
                    "status": "success",
                    "message": "设备检查完成",
                    "deviceInfo": {
                        "type": device_type,
                        "ip": first_device['ip']
                    },
                    "paths": {
                        "rawConfig": raw_config_path,
                        "report": report_path
                    },
                    "logs": recent_logs
                },
                status_code=200
            )

        except Exception as e:
            logger.error(f"设备检查过程失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"设备检查失败: {str(e)}"
            )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"未预期的错误: {str(e)}"
        )
# AI operation endpoint
@app.post("/api/ai_operation/execute")
def execute_ai_command(payload: AICommandRequest):
    try:
        result = run_ai_operation(payload.command)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint to list files in directories
@app.get("/api/files/list")
async def list_files(directory: str):
    """
    List files in the specified directory.

    Args:
        directory: Directory name (e.g., 'config', 'templates/commands', 'templates/prompts')

    Returns:
        List of file names with paths
    """
    try:
        base_path = os.path.join(BASE_DIR, directory)
        logger.info(f"Attempting to list files in directory: {base_path}")
        if not os.path.exists(base_path):
            raise HTTPException(status_code=404, detail=f"Directory {directory} not found")

        files = []
        for filename in os.listdir(base_path):
            full_path = os.path.join(directory, filename).replace("\\", "/")  # 替换为Unix风格路径
            if os.path.isfile(os.path.join(base_path, filename)):
                files.append({
                    "name": filename,
                    "path": full_path
                })
        logger.info(f"Found files: {files}")
        return JSONResponse(
            content={"files": files},
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}  # 禁用缓存
        )
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)