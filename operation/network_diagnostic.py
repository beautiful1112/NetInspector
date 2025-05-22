from typing import Dict, Any, List, TypedDict, Annotated, Sequence, Type
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from tools.network_tools import get_available_tools
from .ai_operator import AIOperator
import json
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Define the state type for our diagnostic workflow
class NetworkState(TypedDict):
    """State for the network diagnostic workflow"""
    messages: Annotated[Sequence[HumanMessage | AIMessage], "The messages in the conversation"]
    current_step: Annotated[str, "The current step in the diagnostic process"]
    diagnostic_data: Annotated[Dict[str, Any], "The collected diagnostic data"]
    next_steps: Annotated[List[str], "The next steps to take"]
    conclusion: Annotated[str, "The final conclusion of the diagnosis"]

class BaseDiagnosticAgent(ABC):
    """Base class for network diagnostic agents"""
    
    def __init__(self, llm=None):
        self.ai_operator = AIOperator(llm=llm)
        self.tools = get_available_tools()
        self.workflow = self.create_diagnostic_graph()
    
    @abstractmethod
    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get the prompt template for this diagnostic agent"""
        pass
    
    @abstractmethod
    def create_diagnostic_graph(self) -> StateGraph:
        """Create the diagnostic workflow graph"""
        pass
    
    def diagnose_issue(self, issue_description: str) -> Dict[str, Any]:
        """Start the diagnostic process for a network issue"""
        try:
            # Initialize the state
            initial_state = NetworkState(
                messages=[HumanMessage(content=issue_description)],
                current_step="collect_initial_info",
                diagnostic_data={},
                next_steps=[],
                conclusion=""
            )
            
            # Run the workflow
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "diagnostic_data": final_state["diagnostic_data"],
                "conclusion": final_state["conclusion"]
            }
        except Exception as e:
            logger.error(f"Error in diagnostic process: {str(e)}")
            return {
                "error": str(e),
                "diagnostic_data": {},
                "conclusion": "Diagnostic process failed"
            }

class RoutingProtocolDiagnosticAgent(BaseDiagnosticAgent):
    """Diagnostic agent for routing protocol issues (BGP/OSPF)"""
    
    def get_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are a network diagnostic expert specializing in routing protocol issues. Your task is to diagnose network issues by:
1. Analyzing the current state and collected data
2. Deciding which tools to use next
3. Interpreting the results
4. Making decisions about the next steps
5. Providing a final conclusion

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
}

For routing protocol issues, follow this diagnostic approach:
1. First check the basic connectivity between devices
2. Then examine the routing protocol neighbor states
3. Analyze the routing protocol configurations
4. Check for any interface or link issues
5. Verify routing table entries
6. Look for any error messages or logs"""),
            MessagesPlaceholder(variable_name="messages"),
        ])
    
    def create_diagnostic_graph(self) -> StateGraph:
        workflow = StateGraph(NetworkState)
        
        def collect_initial_info(state: NetworkState) -> NetworkState:
            try:
                issue_description = state["messages"][-1].content
                response = self.ai_operator.llm.invoke(self.get_prompt_template().format_messages(
                    tools=json.dumps([tool.name for tool in self.tools]),
                    current_state=json.dumps(state["diagnostic_data"]),
                    messages=state["messages"]
                ))
                
                decision = json.loads(response.content)
                tool = next(t for t in self.tools if t.name == decision["tool_to_use"])
                tool_input = json.loads(decision["tool_input"])
                result = tool.run(tool_input)
                
                state["diagnostic_data"].update({
                    "initial_analysis": decision["reasoning"],
                    "tool_results": {decision["tool_to_use"]: result},
                    "issue_type": "routing_protocol"
                })
                
                state["messages"].append(AIMessage(content=f"Initial analysis: {decision['reasoning']}\nTool results: {result}"))
                return state
            except Exception as e:
                logger.error(f"Error in collect_initial_info: {str(e)}")
                state["diagnostic_data"]["error"] = str(e)
                return state
        
        def analyze_connectivity(state: NetworkState) -> NetworkState:
            """Analyze network connectivity"""
            try:
                # Use LLM to analyze connectivity based on collected data
                response = self.ai_operator.llm.invoke(self.get_prompt_template().format_messages(
                    tools=json.dumps([tool.name for tool in self.tools]),
                    current_state=json.dumps(state["diagnostic_data"]),
                    messages=state["messages"]
                ))
                
                # Parse the response
                decision = json.loads(response.content)
                
                # Execute the selected tool (likely ping or traceroute)
                tool = next(t for t in self.tools if t.name == decision["tool_to_use"])
                tool_input = json.loads(decision["tool_input"])
                result = tool.run(tool_input)
                
                # Update state
                state["diagnostic_data"].update({
                    "connectivity_analysis": decision["reasoning"],
                    "tool_results": {**state["diagnostic_data"].get("tool_results", {}), 
                                   decision["tool_to_use"]: result}
                })
                
                # Add AI response to messages
                state["messages"].append(AIMessage(content=f"Connectivity analysis: {decision['reasoning']}\nTool results: {result}"))
                
                return state
            except Exception as e:
                logger.error(f"Error in analyze_connectivity: {str(e)}")
                state["diagnostic_data"]["error"] = str(e)
                return state
        
        def check_routing_protocol(state: NetworkState) -> NetworkState:
            """Check routing protocol status and configuration"""
            try:
                # Use LLM to analyze routing protocol based on collected data
                response = self.ai_operator.llm.invoke(self.get_prompt_template().format_messages(
                    tools=json.dumps([tool.name for tool in self.tools]),
                    current_state=json.dumps(state["diagnostic_data"]),
                    messages=state["messages"]
                ))
                
                # Parse the response
                decision = json.loads(response.content)
                
                # Execute the selected tool (likely get_bgp_neighbors, get_ospf_neighbors, etc.)
                tool = next(t for t in self.tools if t.name == decision["tool_to_use"])
                tool_input = json.loads(decision["tool_input"])
                result = tool.run(tool_input)
                
                # Update state
                state["diagnostic_data"].update({
                    "routing_protocol_analysis": decision["reasoning"],
                    "tool_results": {**state["diagnostic_data"].get("tool_results", {}), 
                                   decision["tool_to_use"]: result}
                })
                
                # Add AI response to messages
                state["messages"].append(AIMessage(content=f"Routing protocol analysis: {decision['reasoning']}\nTool results: {result}"))
                
                return state
            except Exception as e:
                logger.error(f"Error in check_routing_protocol: {str(e)}")
                state["diagnostic_data"]["error"] = str(e)
                return state
        
        def analyze_routing(state: NetworkState) -> NetworkState:
            """Analyze routing issues"""
            try:
                # Use LLM to analyze routing based on collected data
                response = self.ai_operator.llm.invoke(self.get_prompt_template().format_messages(
                    tools=json.dumps([tool.name for tool in self.tools]),
                    current_state=json.dumps(state["diagnostic_data"]),
                    messages=state["messages"]
                ))
                
                # Parse the response
                decision = json.loads(response.content)
                
                # Execute the selected tool (likely get_routes, get_bgp_neighbors, or get_ospf_neighbors)
                tool = next(t for t in self.tools if t.name == decision["tool_to_use"])
                tool_input = json.loads(decision["tool_input"])
                result = tool.run(tool_input)
                
                # Update state
                state["diagnostic_data"].update({
                    "routing_analysis": decision["reasoning"],
                    "tool_results": {**state["diagnostic_data"].get("tool_results", {}), 
                                   decision["tool_to_use"]: result}
                })
                
                # Add AI response to messages
                state["messages"].append(AIMessage(content=f"Routing analysis: {decision['reasoning']}\nTool results: {result}"))
                
                return state
            except Exception as e:
                logger.error(f"Error in analyze_routing: {str(e)}")
                state["diagnostic_data"]["error"] = str(e)
                return state
        
        def generate_conclusion(state: NetworkState) -> NetworkState:
            """Generate the final diagnostic conclusion"""
            try:
                # Use LLM to generate conclusion based on all collected data
                response = self.ai_operator.llm.invoke(self.get_prompt_template().format_messages(
                    tools=json.dumps([tool.name for tool in self.tools]),
                    current_state=json.dumps(state["diagnostic_data"]),
                    messages=state["messages"]
                ))
                
                # Parse the response
                decision = json.loads(response.content)
                
                # Update state with conclusion
                state["conclusion"] = decision["reasoning"]
                
                # Add AI response to messages
                state["messages"].append(AIMessage(content=f"Final conclusion: {decision['reasoning']}"))
                
                return state
            except Exception as e:
                logger.error(f"Error in generate_conclusion: {str(e)}")
                state["diagnostic_data"]["error"] = str(e)
                state["conclusion"] = "Failed to generate conclusion"
                return state
        
        # Add nodes to the graph
        workflow.add_node("collect_initial_info", collect_initial_info)
        workflow.add_node("analyze_connectivity", analyze_connectivity)
        workflow.add_node("check_routing_protocol", check_routing_protocol)
        workflow.add_node("analyze_routing", analyze_routing)
        workflow.add_node("generate_conclusion", generate_conclusion)
        
        # Define the edges
        workflow.add_edge("collect_initial_info", "analyze_connectivity")
        workflow.add_edge("analyze_connectivity", "check_routing_protocol")
        workflow.add_edge("check_routing_protocol", "analyze_routing")
        workflow.add_edge("analyze_routing", "generate_conclusion")
        workflow.add_edge("generate_conclusion", END)
        
        # Set the entry point
        workflow.set_entry_point("collect_initial_info")
        
        return workflow

class ConnectivityDiagnosticAgent(BaseDiagnosticAgent):
    """Diagnostic agent for basic connectivity issues"""
    
    def get_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are a network diagnostic expert specializing in connectivity issues. Your task is to diagnose network issues by:
1. Analyzing the current state and collected data
2. Deciding which tools to use next
3. Interpreting the results
4. Making decisions about the next steps
5. Providing a final conclusion

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
}

For connectivity issues, follow this diagnostic approach:
1. Check physical connectivity
2. Verify interface status
3. Check IP addressing
4. Test basic connectivity (ping)
5. Check routing
6. Verify ACLs and security policies"""),
            MessagesPlaceholder(variable_name="messages"),
        ])
    
    def create_diagnostic_graph(self) -> StateGraph:
        # Implementation similar to RoutingProtocolDiagnosticAgent but with different nodes
        pass

class PerformanceDiagnosticAgent(BaseDiagnosticAgent):
    """Diagnostic agent for network performance issues"""
    
    def get_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are a network diagnostic expert specializing in performance issues. Your task is to diagnose network issues by:
1. Analyzing the current state and collected data
2. Deciding which tools to use next
3. Interpreting the results
4. Making decisions about the next steps
5. Providing a final conclusion

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
}

For performance issues, follow this diagnostic approach:
1. Check CPU and memory usage
2. Analyze interface statistics
3. Check for errors and drops
4. Monitor queue depths
5. Analyze routing table size
6. Check for resource exhaustion"""),
            MessagesPlaceholder(variable_name="messages"),
        ])
    
    def create_diagnostic_graph(self) -> StateGraph:
        # Implementation similar to RoutingProtocolDiagnosticAgent but with different nodes
        pass

class NetworkDiagnosticOperator:
    """Network diagnostic operator using specialized agents"""
    
    def __init__(self, llm=None):
        self.agents = {
            "routing": RoutingProtocolDiagnosticAgent(llm=llm),
            "connectivity": ConnectivityDiagnosticAgent(llm=llm),
            "performance": PerformanceDiagnosticAgent(llm=llm)
        }
    
    def diagnose_issue(self, issue_description: str) -> Dict[str, Any]:
        """Start the diagnostic process for a network issue"""
        try:
            # Determine which agent to use based on the issue description
            agent = self._select_agent(issue_description)
            
            # Run the diagnostic process
            return agent.diagnose_issue(issue_description)
        except Exception as e:
            logger.error(f"Error in diagnostic process: {str(e)}")
            return {
                "error": str(e),
                "diagnostic_data": {},
                "conclusion": "Diagnostic process failed"
            }
    
    def _select_agent(self, issue_description: str) -> BaseDiagnosticAgent:
        """Select the appropriate diagnostic agent based on the issue description"""
        description = issue_description.lower()
        
        if any(proto in description for proto in ["bgp", "ospf", "routing", "route"]):
            return self.agents["routing"]
        elif any(term in description for term in ["performance", "slow", "latency", "cpu", "memory"]):
            return self.agents["performance"]
        else:
            return self.agents["connectivity"] 