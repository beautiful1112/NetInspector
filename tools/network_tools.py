from typing import List, Dict, Any
from langchain.tools import BaseTool
from pydantic import Field
import json
import logging
from network.nornir_manager import NornirManager
from network.napalm_operations import get_interfaces, get_interfaces_ip

logger = logging.getLogger(__name__)

# Create a single shared instance of NornirManager
_shared_nornir_manager = None

def get_nornir_manager():
    global _shared_nornir_manager
    if _shared_nornir_manager is None:
        _shared_nornir_manager = NornirManager()
    return _shared_nornir_manager

class GetHostsTool(BaseTool):
    name: str = "get_hosts"
    description: str = """
    Get a list of all available network devices.
    Input can be any string, it will be ignored.
    Returns a list of all configured hosts with their basic information.
    Example: "list all hosts"
    """
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, query: str) -> str:
        try:
            logger.info("Getting list of hosts from Nornir")
            hosts = self.nornir_manager.get_hosts()
            logger.info(f"Found {len(hosts)} hosts")
            return json.dumps(hosts)
        except Exception as e:
            logger.error(f"Error in GetHostsTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("Async version not implemented")

class GetInterfacesIPTool(BaseTool):
    name: str = "get_interfaces_ip"
    description: str = """
    Get IP addresses of all interfaces on specified network devices.
    Input should be a JSON string containing a list of hostnames.
    Example: '["switch01"]'
    Returns IP addresses (both IPv4 and IPv6) for all interfaces on the specified devices.
    """
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames_json: str) -> str:
        try:
            hostnames = json.loads(hostnames_json)
            if not isinstance(hostnames, list):
                raise ValueError("Input must be a JSON array of hostnames")

            filtered_nr = self.nornir_manager.filter_hosts(hostnames)
            result = filtered_nr.run(task=get_interfaces_ip)
            
            formatted_results = {}
            for hostname, host_result in result.items():
                if host_result.failed:
                    formatted_results[hostname] = {
                        "status": "failed",
                        "error": str(host_result.exception)
                    }
                else:
                    formatted_results[hostname] = {
                        "status": "success",
                        "data": host_result.result
                    }
            
            return json.dumps(formatted_results, indent=2)
        except Exception as e:
            logger.error(f"Error in GetInterfacesIPTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostnames_json: str) -> str:
        raise NotImplementedError("Async version not implemented")

class GetInterfacesDetailTool(BaseTool):
    name: str = "get_interfaces_detail"
    description: str = """
    Get detailed information about all interfaces on specified network devices.
    Input should be a JSON string containing a list of hostnames.
    Example: '["switch01"]'
    Returns detailed interface information including:
    - Interface status (enabled/disabled)
    - Operational status (up/down)
    - Interface description
    - MAC address
    - MTU
    - Speed
    - And other interface-specific details
    """
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames_json: str) -> str:
        try:
            hostnames = json.loads(hostnames_json)
            if not isinstance(hostnames, list):
                raise ValueError("Input must be a JSON array of hostnames")

            filtered_nr = self.nornir_manager.filter_hosts(hostnames)
            result = filtered_nr.run(task=get_interfaces)
            
            formatted_results = {}
            for hostname, host_result in result.items():
                if host_result.failed:
                    formatted_results[hostname] = {
                        "status": "failed",
                        "error": str(host_result.exception)
                    }
                else:
                    formatted_results[hostname] = {
                        "status": "success",
                        "data": host_result.result
                    }
            
            return json.dumps(formatted_results, indent=2)
        except Exception as e:
            logger.error(f"Error in GetInterfacesDetailTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostnames_json: str) -> str:
        raise NotImplementedError("Async version not implemented") 