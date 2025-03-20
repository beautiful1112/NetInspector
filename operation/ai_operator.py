"""
ai_operator.py

该模块实现了基于 AI 的设备操作流程，使用 LangChain 工具链来处理自然语言命令。
主要功能：
1. 通过 AIOperator 类管理与 AI 的交互
2. 集成网络操作工具供 AI 使用
3. 维护对话历史记录
4. 处理自然语言命令并返回结果
"""

from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler
from tools.network_tools import GetInterfacesIPTool, GetHostsTool, GetInterfacesDetailTool
import os
import yaml
import logging

logger = logging.getLogger(__name__)

class ToolCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.tool_outputs = []

    def on_tool_start(self, serialized, input_str, **kwargs):
        self.tool_outputs.append(f"> Using tool: {serialized['name']}")
        self.tool_outputs.append(f"> Input: {input_str}")

    def on_tool_end(self, output, **kwargs):
        self.tool_outputs.append(f"> Tool output: {output}")
        self.tool_outputs.append("---")

class AIOperator:
    def __init__(self):
        # Load settings
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        settings_file = os.path.join(project_root, "utils", "settings.yaml")
        
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = yaml.safe_load(f)
        
        # Initialize callback handler
        self.tool_handler = ToolCallbackHandler()
            
        # Initialize AI model
        self.llm = ChatOpenAI(
            model=settings['ai_config']['model'],
            openai_api_key=settings['ai_config']['api_key'],
            openai_api_base=settings['ai_config']['api_base'],
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        
        # Initialize tools
        self.tools = [
            GetHostsTool(),
            GetInterfacesIPTool(),
            GetInterfacesDetailTool(),
            # Add more tools here
        ]

        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize agent with tool handler
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            callbacks=[self.tool_handler]
        )
    
    def process_command(self, command: str) -> dict:
        """Process a natural language command using the AI agent"""
        try:
            logger.info(f"Processing command: {command}")
            
            # Reset tool outputs
            self.tool_handler.tool_outputs = []
            
            # Get AI response
            response = self.agent.run(input=command)
            
            logger.info(f"AI response: {response}")
            
            # Return both response and tool outputs
            return {
                "response": response,
                "tool_outputs": self.tool_handler.tool_outputs
            }
            
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            raise