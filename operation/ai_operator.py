"""
ai_operator.py

This module implements the device operation process based on AI, using the LangChain toolchain to handle natural language commands.
Main functions:
1. Manage interactions with AI through the AIOperator class
2. Integrate network operation tools for AI use
3. Maintain conversation history
4. Process natural language commands and return results
"""

from langchain_openai import ChatOpenAI
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.tools import BaseTool
from tools.network_tools import get_all_tools
import os
import yaml
import logging
import json
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools.render import format_tool_to_openai_function
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

logger = logging.getLogger(__name__)

# Tool categories for better organization
TOOL_CATEGORIES = {
    "Device Information": [
        "get_hosts",
        "get_facts",
        "get_environment",
        "get_config"
    ],
    "Interface Management": [
        "get_interfaces_ip",
        "get_interfaces_detail"
    ],
    "Routing Information": [
        "get_routes",
        "get_bgp_neighbors",
        "get_bgp_config",
        "get_ospf_neighbors",
        "get_ospf_config"
    ],
    "Layer 2 Information": [
        "get_arp_table",
        "get_mac_table"
    ],
    "Connectivity Testing": [
        "ping"
    ]
}

# Enhanced system prompt for better tool selection
SYSTEM_PROMPT = """You are an expert network automation assistant. Your task is to help users manage and troubleshoot their network infrastructure.

Available tools are organized into the following categories:

1. Device Information:
   - get_hosts: List all available network devices
   - get_facts: Get basic device information (model, OS version, etc.)
   - get_environment: Get device environment data (temperature, power, etc.)
   - get_config: Get complete device configuration

2. Interface Management:
   - get_interfaces_ip: Get IP addresses of all interfaces
   - get_interfaces_detail: Get detailed interface information

3. Routing Information:
   - get_routes: Get routing table information
   - get_bgp_neighbors: Get BGP neighbor information
   - get_bgp_config: Get BGP configuration
   - get_ospf_neighbors: Get OSPF neighbor information
   - get_ospf_config: Get OSPF configuration

4. Layer 2 Information:
   - get_arp_table: Get ARP table information
   - get_mac_table: Get MAC address table information

5. Connectivity Testing:
   - ping: Test connectivity between devices

When selecting tools:
1. First, identify the category of operation needed
2. Choose the most specific tool for the task
3. Consider dependencies between tools (e.g., get_hosts before other operations)
4. Use multiple tools in sequence if needed for complete information

Always provide clear reasoning for your tool selection and explain the expected outcome."""

class ToolCallbackHandler:
    def __init__(self):
        self.tool_outputs = []
    def on_tool_start(self, serialized, input_str, **kwargs):
        self.tool_outputs.append(f"> Using tool: {serialized['name']}")
        self.tool_outputs.append(f"> Input: {input_str}")
    def on_tool_end(self, output, **kwargs):
        self.tool_outputs.append(f"> Tool output: {output}")
        self.tool_outputs.append("---")

class AIOperator:
    """AI operator for network operations"""
    def __init__(self, llm=None):
        # Load settings
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        settings_file = os.path.join(project_root, "utils", "settings.yaml")
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = yaml.safe_load(f)
        # Initialize callback handler
        self.tool_handler = ToolCallbackHandler()
        # Initialize AI model
        if llm is None:
            self.llm = ChatOpenAI(
                model=settings['ai_config']['model'],
                openai_api_key=settings['ai_config']['api_key'],
                openai_api_base=settings['ai_config']['api_base'],
                streaming=True,
                callbacks=[StreamingStdOutCallbackHandler()],
                temperature=0
            )
        else:
            self.llm = llm
        # Initialize tools
        self.tools = get_all_tools()
        # Create the chat agent (single-step tool-calling)
        self.chat_agent = self._create_chat_agent()

    def _create_chat_agent(self) -> AgentExecutor:
        """Create a single-step chat agent for tool-calling (no chat_history)."""
        # Create a prompt template that includes tool categories and selection guidance
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3  # Limit iterations to prevent infinite loops
        )

    def process_command(self, command: str) -> Dict[str, Any]:
        """Process a network operation command using the plan → execute → summarize pipeline, with debug logging."""
        import logging
        try:
            logger.info(f"Received command: {command}")
            # Step 1: Let the LLM plan which tool to use and with what arguments
            enhanced_command = self._enhance_command_with_context(command)
            plan_prompt = f"""You are an expert network automation assistant. The user asked: '{enhanced_command}'.\nChoose the best tool from the following list and provide the tool name and arguments in JSON format.\n\nAvailable tools:\n{[tool.name for tool in self.tools]}\n\nRespond in this JSON format:\n{{\n  \"tool_name\": \"<tool_name>\",\n  \"tool_args\": {{ ... }}\n}}"""
            logger.info(f"Sending plan prompt to LLM: {plan_prompt}")
            plan_response = self.llm.invoke([HumanMessage(content=plan_prompt)])
            logger.info(f"LLM plan response: {plan_response.content}")
            plan_json = self._safe_json_parse(plan_response.content)
            if not plan_json or 'tool_name' not in plan_json or 'tool_args' not in plan_json:
                logger.error(f"AI could not determine the tool or arguments. Raw plan: {plan_response.content}")
                return {"response": f"AI could not determine the tool or arguments. Raw plan: {plan_response.content}"}
            tool_name = plan_json['tool_name']
            tool_args = plan_json['tool_args']
            logger.info(f"Selected tool: {tool_name} with args: {tool_args}")
            # Step 2: Actually execute the tool
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if not tool:
                logger.error(f"Tool '{tool_name}' not found.")
                return {"response": f"Tool '{tool_name}' not found."}
            try:
                tool_args = self._fix_tool_args(tool, tool_args)
                logger.info(f"Running tool {tool_name} with args {tool_args}")
                tool_result = tool.run(tool_args)
                logger.info(f"Tool {tool_name} result: {tool_result}")
            except Exception as tool_exc:
                logger.error(f"Error running tool '{tool_name}': {tool_exc}")
                return {"response": f"Error running tool '{tool_name}': {tool_exc}"}
            # Step 3: Summarize the tool output for the user
            summary_prompt = f"The user asked: '{command}'. Here is the raw output from the tool '{tool_name}':\n{tool_result}\nSummarize this output in a user-friendly way."
            logger.info(f"Sending summary prompt to LLM: {summary_prompt}")
            summary_response = self.llm.invoke([HumanMessage(content=summary_prompt)])
            logger.info(f"LLM summary response: {summary_response.content}")
            return {
                "response": summary_response.content,
                "tool_used": tool_name,
                "tool_args": tool_args,
                "tool_output": tool_result
            }
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return {
                "response": f"Error: {str(e)}"
            }

    def _enhance_command_with_context(self, command: str) -> str:
        """Add context to the command to help with tool selection."""
        # Identify the category of the command
        category = self._identify_command_category(command)
        if category:
            return f"Category: {category}\nCommand: {command}"
        return command

    def _identify_command_category(self, command: str) -> str:
        """Identify the most likely category for the command."""
        command_lower = command.lower()
        
        # Simple keyword-based categorization
        if any(word in command_lower for word in ["interface", "ip address", "vlan"]):
            return "Interface Management"
        elif any(word in command_lower for word in ["route", "bgp", "ospf", "routing"]):
            return "Routing Information"
        elif any(word in command_lower for word in ["mac", "arp", "layer 2"]):
            return "Layer 2 Information"
        elif any(word in command_lower for word in ["ping", "connectivity", "reachable"]):
            return "Connectivity Testing"
        elif any(word in command_lower for word in ["config", "show", "display", "information"]):
            return "Device Information"
        
        return ""

    def analyze_network_issue(self, issue_description: str) -> Dict[str, Any]:
        """Analyze a network issue using the diagnostic workflow (multi-step)."""
        try:
            from .network_diagnostic import NetworkDiagnosticOperator
            diagnostic_operator = NetworkDiagnosticOperator(llm=self.llm)
            return diagnostic_operator.diagnose_issue(issue_description)
        except Exception as e:
            logger.error(f"Error in analyze_network_issue: {str(e)}")
            return {
                "error": str(e),
                "diagnostic_data": {},
                "conclusion": "Analysis failed"
            }

    def get_next_step(self, current_state: Dict[str, Any], messages: List[HumanMessage | AIMessage]) -> Dict[str, Any]:
        """Get the next step in the diagnostic process"""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a network diagnostic expert. Your task is to:
1. Analyze the current state and collected data
2. Decide which tools to use next
3. Interpret the results
4. Make decisions about the next steps
5. Provide a final conclusion

Available tools:
{tools}

Current state:
{current_state}

Previous messages:
{messages}

Based on the current state and available tools, what should be the next step in the diagnostic process?
Provide your response in JSON format with the following structure:
{
    "next_step": "step_name",
    "tool_to_use": "tool_name",
    "tool_input": "tool_input_json",
    "reasoning": "explanation of your decision"
}"""),
                MessagesPlaceholder(variable_name="messages"),
            ])
            
            # Get response from LLM
            response = self.llm.invoke(prompt.format_messages(
                tools=json.dumps([tool.name for tool in self.tools]),
                current_state=json.dumps(current_state),
                messages=messages
            ))
            
            # Parse response
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Error in get_next_step: {str(e)}")
            return {
                "error": str(e),
                "next_step": "error",
                "tool_to_use": None,
                "tool_input": None,
                "reasoning": "Failed to get next step"
            }
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a network tool"""
        try:
            # Find the tool
            tool = next(t for t in self.tools if t.name == tool_name)
            
            # Execute the tool
            return tool.run(tool_input)
        except Exception as e:
            logger.error(f"Error in execute_tool: {str(e)}")
            return {
                "error": str(e),
                "result": None
            }
    
    def generate_conclusion(self, diagnostic_data: Dict[str, Any], messages: List[HumanMessage | AIMessage]) -> str:
        """Generate a conclusion based on the diagnostic data"""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a network diagnostic expert. Your task is to generate a conclusion based on the diagnostic data.

Diagnostic data:
{diagnostic_data}

Previous messages:
{messages}

Provide a clear and concise conclusion that:
1. Summarizes the findings
2. Identifies the root cause
3. Suggests potential solutions
4. Provides recommendations for prevention"""),
                MessagesPlaceholder(variable_name="messages"),
            ])
            
            # Get response from LLM
            response = self.llm.invoke(prompt.format_messages(
                diagnostic_data=json.dumps(diagnostic_data),
                messages=messages
            ))
            
            return response.content
        except Exception as e:
            logger.error(f"Error in generate_conclusion: {str(e)}")
            return "Failed to generate conclusion"

    def _safe_json_parse(self, text: str):
        """Safely parse a JSON string, return None if parsing fails."""
        import json
        try:
            return json.loads(text)
        except Exception:
            # Try to extract JSON from text if extra text is present
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    return None
            return None

    def _fix_tool_args(self, tool, tool_args):
        # If the tool expects 'hostnames', map any common synonyms to it
        if hasattr(tool, 'args_schema'):
            schema_fields = getattr(tool.args_schema, '__fields__', {})
            if 'hostnames' in schema_fields:
                # List of possible synonyms the LLM might use
                possible_keys = ['hostnames', 'hostname', 'host', 'device', 'node', 'switch', 'router']
                for key in possible_keys:
                    if key in tool_args:
                        # Always convert to a list for 'hostnames'
                        value = tool_args.pop(key)
                        tool_args['hostnames'] = value if isinstance(value, list) else [value]
                        break
        return tool_args