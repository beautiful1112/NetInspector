# api/main.py
import os
import sys
import re
from pathlib import Path

# Add project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from inspection.generic_inspector import GenericInspector
from utils.logger import get_logger
from nornir import InitNornir
import yaml
from typing import Dict, List
from datetime import datetime
from api.network_routes import router as network_router
from operation.ai_operator import AIOperator
import uvicorn

logger = get_logger(__name__)

app = FastAPI()

# Add CORS middleware with more permissive settings
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8000",  # FastAPI server
    "http://127.0.0.1:5173",  # Alternative Vite dev server
    "http://127.0.0.1:8000",  # Alternative FastAPI server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include network routes
app.include_router(network_router, prefix="/api/network", tags=["network"])

class AICommandRequest(BaseModel):
    command: str


class InspectionRequest(BaseModel):
    deviceYaml: str
    credentialYaml: str
    commandJson: str
    promptTxt: str

# File upload endpoints



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

@app.post("/api/upload-config")
async def upload_config(file: UploadFile = File(...), type: str = Form(...)):
    """Upload configuration file"""
    try:
        # Use relative path for config directory
        config_dir = "config"  # Changed to relative path
        if type == "hosts":
            filename = "hosts.yaml"
        elif type == "groups":
            filename = "groups.yaml"
        elif type == "defaults":
            filename = "defaults.yaml"
        else:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
        file_path = os.path.join(config_dir, filename)

        content = await file.read()
        # Validate YAML format
        yaml.safe_load(content)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Return relative path
        return JSONResponse(
            content={
                "success": True,
                "message": f"{filename} uploaded successfully",
                "path": f"config/{filename}"  # Use forward slashes for consistency
            }
        )
    except yaml.YAMLError:
        raise HTTPException(status_code=400, detail="Invalid YAML format")
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 添加新的设置加载函数
def load_settings():
    """Load settings from YAML file"""
    settings_file = os.path.join(project_root, "utils", "settings.yaml")
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        raise

# Add settings model
class Settings(BaseModel):
    connection: dict
    logging: dict
    langchain: dict
    ai_config: dict
    directories: dict

# Add these new endpoints
@app.get("/api/settings")
async def get_settings():
    """Get current settings from settings.yaml"""
    try:
        settings = load_settings()
        return JSONResponse(
            content=settings,
            headers={"Cache-Control": "no-cache"}
        )
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to load settings: {str(e)}"}
        )

@app.post("/api/settings")
async def save_settings(settings: dict):
    """Save settings to settings.yaml"""
    try:
        settings_file = os.path.join(project_root, "utils", "settings.yaml")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        
        # 保存设置
        with open(settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(settings, f, default_flow_style=False, allow_unicode=True)
        
        return JSONResponse(
            content={"message": "Settings saved successfully"},
            headers={"Cache-Control": "no-cache"}
        )
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to save settings: {str(e)}"}
        )

@app.post("/api/validate-configs")
async def validate_configs():
    """Validate Nornir configuration files"""
    try:
        settings = load_settings()
        config_dir = os.path.join(project_root, "config")
        logs_dir = os.path.join(project_root, settings['logging']['log_dir'])
        
        # 确保目录存在
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)
        
        # 创建或更新 config.yaml
        config_yaml_path = os.path.join(config_dir, "config.yaml")
        
        # 使用正确的日志配置结构
        config_content = {
            "inventory": {
                "plugin": "SimpleInventory",
                "options": {
                    "host_file": "config/hosts.yaml",
                    "group_file": "config/groups.yaml",
                    "defaults_file": "config/defaults.yaml"
                }
            },
            "runner": {
                "plugin": "threaded",
                "options": {
                    "num_workers": 10
                }
            },
            "logging": {
                "enabled": True,
                "level": settings['logging']['log_level'],
                "log_file": os.path.join(settings['logging']['log_dir'], "nornir.log"),
                "format": settings['logging']['log_format']
            }
        }
        
        # 写入配置文件
        with open(config_yaml_path, "w") as f:
            yaml.dump(config_content, f, default_flow_style=False)

        # 验证配置文件是否存在
        required_files = ["hosts.yaml", "groups.yaml", "defaults.yaml"]
        missing_files = []
        for filename in required_files:
            file_path = os.path.join(config_dir, filename)
            if not os.path.exists(file_path):
                missing_files.append(filename)
                logger.warning(f"Missing file: {file_path}")
            else:
                logger.info(f"Found file: {file_path}")
        
        if missing_files:
            return JSONResponse(
                content={
                    "success": False,
                    "error": f"Missing required files: {', '.join(missing_files)}"
                }
            )

        # 尝试初始化 Nornir
        try:
            # 切换到项目根目录
            os.chdir(project_root)
            nr = InitNornir(config_file="config/config.yaml")
            hosts = nr.inventory.hosts
            logger.info(f"Nornir initialization successful, found {len(hosts)} hosts")
            return JSONResponse(
                content={
                    "success": True,
                    "message": f"Configuration valid. Found {len(hosts)} devices."
                }
            )
        except Exception as e:
            logger.error(f"Nornir initialization error: {str(e)}")
            return JSONResponse(
                content={
                    "success": False,
                    "error": f"Invalid configuration: {str(e)}"
                }
            )

    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "error": f"Validation failed: {str(e)}"
            }
        )

@app.post("/api/inspection/start")
async def start_inspection(request: dict):
    """Start inspection for selected hosts"""
    try:
        selected_hosts = request.get("hosts", [])
        command_file = request.get("commandFile")
        prompt_file = request.get("promptFile")
        chunk_size = request.get("chunkSize", 75000)  # Default to 75000 if not provided

        logger.info(f"Starting inspection with hosts: {selected_hosts}")
        logger.info(f"Command file: {command_file}")
        logger.info(f"Prompt file: {prompt_file}")
        logger.info(f"Analysis chunk size: {chunk_size}")

        if not selected_hosts:
            raise HTTPException(status_code=400, detail="No hosts selected")
        
        if not command_file or not prompt_file:
            raise HTTPException(status_code=400, detail="Command file and prompt file must be selected")

        # 确保工作目录正确
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)

        # 确保配置目录存在
        settings = load_settings()
        os.makedirs(os.path.join(project_root, settings['directories']['raw_configs']), exist_ok=True)
        os.makedirs(os.path.join(project_root, settings['directories']['reports']), exist_ok=True)

        # Initialize Nornir with relative paths
        nr = InitNornir(config_file="config/config.yaml")

        # Filter selected hosts
        target_hosts = nr.filter(filter_func=lambda h: h.name in selected_hosts)
        
        if not target_hosts.inventory.hosts:
            raise HTTPException(status_code=404, detail="No matching hosts found")

        # Start inspection for each host
        results = []
        for host_name, host in target_hosts.inventory.hosts.items():
            try:
                device_info = {
                    "host": host_name,
                    "device_type": host.platform
                }
                
                config = {
                    "commands_file": command_file,
                    "prompt_file": prompt_file,
                    "chunk_size": chunk_size  # Pass chunk_size to inspector
                }

                logger.info(f"Starting inspection for host {host_name}")
                logger.info(f"Device info: {device_info}")
                logger.info(f"Config: {config}")

                inspector = GenericInspector(device_info, config)
                raw_config_path, report_path = inspector.run()
                
                results.append({
                    "host": host_name,
                    "status": "success",
                    "raw_config": raw_config_path,
                    "report": report_path
                })
                logger.info(f"Inspection completed for host {host_name}")

            except Exception as e:
                logger.error(f"Inspection failed for host {host_name}: {str(e)}")
                results.append({
                    "host": host_name,
                    "status": "failed",
                    "error": str(e)
                })

        return JSONResponse(
            content={
                "status": "success",
                "message": f"Inspection completed for {len(results)} hosts",
                "results": results
            }
        )
    except Exception as e:
        logger.error(f"Inspection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize AI operator
ai_operator = AIOperator()

# AI operation endpoint
@app.post("/api/ai_operation/execute")
def execute_ai_command(payload: AICommandRequest):
    try:
        result = ai_operator.process_command(payload.command)
        return {"response": result}
    except Exception as e:
        logger.error(f"AI operation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint to list files in directories
@app.get("/api/files/list")
async def list_files(directory: str):
    """List files in the specified directory"""
    try:
        # 使用项目根目录作为基准
        abs_directory = os.path.join(project_root, directory)
        logger.info(f"Scanning directory: {abs_directory}")
        
        # 确保目录存在
        os.makedirs(abs_directory, exist_ok=True)

        files = []
        for filename in os.listdir(abs_directory):
            abs_path = os.path.join(abs_directory, filename)
            if os.path.isfile(abs_path):
                # 返回相对路径
                rel_path = os.path.join(directory, filename).replace("\\", "/")
                files.append({
                    "name": filename,
                    "path": rel_path
                })
                logger.info(f"Found file: {filename} at {rel_path}")
        
        logger.info(f"Total files found: {len(files)}")
        return JSONResponse(
            content={"files": files},
            headers={"Cache-Control": "no-cache"}
        )
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"files": []},
            headers={"Cache-Control": "no-cache"}
        )

@app.get("/api/hosts/list")
async def list_hosts():
    """Get list of available hosts from Nornir inventory"""
    try:
        config_yaml = "config/config.yaml"
        
        if not os.path.exists(config_yaml):
            return JSONResponse(
                content={
                    "hosts": [],
                    "message": "Configuration file not found"
                },
                headers={"Cache-Control": "no-cache"}
            )

        nr = InitNornir(config_file=config_yaml)
        
        hosts_list = []
        for name, host in nr.inventory.hosts.items():
            groups = []
            try:
                groups = [group.name for group in host.groups]
            except Exception as e:
                logger.warning(f"Failed to get groups for host {name}: {str(e)}")

            host_info = {
                "name": name,
                "ip": host.hostname,
                "platform": getattr(host, 'platform', 'unknown'),
                "groups": groups
            }
            hosts_list.append(host_info)
        
        return JSONResponse(
            content={"hosts": hosts_list},
            headers={"Cache-Control": "no-cache"}
        )
    except Exception as e:
        logger.error(f"Error listing hosts: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to fetch hosts list: {str(e)}",
                "hosts": []
            }
        )

# 修改 ensure_directories 函数
def ensure_directories():
    """Ensure all required directories exist"""
    try:
        settings = load_settings()
        
        # 创建日志目录 - 直接从 logging 中获取
        log_dir = os.path.join(project_root, settings['logging']['log_dir'])
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建输出目录
        if 'directories' in settings:
            for dir_path in settings['directories'].values():
                full_path = os.path.join(project_root, dir_path)
                os.makedirs(full_path, exist_ok=True)
                logger.info(f"Created directory: {full_path}")
            
        # 创建配置目录
        config_dir = os.path.join(project_root, "config")
        os.makedirs(config_dir, exist_ok=True)
        
        logger.info("All required directories created successfully")
        
    except Exception as e:
        logger.error(f"Error creating directories: {str(e)}")
        raise

# 在应用启动时确保目录存在
@app.on_event("startup")
async def startup_event():
    """Initialize application"""
    try:
        ensure_directories()
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Application initialization failed: {str(e)}")
        raise

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Handle chat messages"""
    try:
        # Get AI response and tool outputs
        result = ai_operator.process_command(request.message)
        
        # Create terminal output
        terminal_output = [
            f"> User Command: {request.message}",
            f"> AI Processing...",
        ]
        
        # Add tool outputs if available
        if result.get("tool_outputs"):
            terminal_output.extend(result["tool_outputs"])
            
        # Add final response
        ai_response = result.get("response", "No response from AI")
        terminal_output.append(f"> AI Response: {ai_response}")
        
        return {
            "response": ai_response,
            "terminal_output": terminal_output
        }
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        error_output = [
            f"> Error occurred while processing command:",
            f"> {str(e)}"
        ]
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "terminal_output": error_output
            }
        )

@app.get("/api/config/{filename}")
async def get_config_file(filename: str):
    """Get the content of a config YAML file (hosts.yaml, groups.yaml, defaults.yaml)"""
    allowed_files = {"hosts.yaml", "groups.yaml", "defaults.yaml"}
    if filename not in allowed_files:
        raise HTTPException(status_code=400, detail="Invalid config file name")
    file_path = os.path.join(project_root, "config", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="text/yaml", filename=filename)

if __name__ == "__main__":
    # Configure uvicorn with longer timeouts
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        timeout_keep_alive=120,  # Keep connections alive for 120 seconds
        timeout_notify=30,        # Notify about timeout after 30 seconds
        workers=4                 # Use multiple workers for better concurrency
    )