from typing import List, Dict, Any
from langchain.tools import BaseTool
from network.nornir_manager import NornirManager
from network.napalm_operations import get_interfaces_ip, get_interfaces
from pydantic import Field
import json
import logging

logger = logging.getLogger(__name__)

class GetHostsTool(BaseTool):
    name: str = "get_hosts"
    description: str = """
    Get a list of all available network devices.
    Input can be any string, it will be ignored.
    Returns a list of all configured hosts with their basic information.
    Example: "list all hosts"
    """
    nornir_manager: NornirManager = Field(default_factory=NornirManager)
    
    def _run(self, query: str) -> str:
        try:
            # Get all hosts from Nornir inventory
            hosts_list = []
            
            for name, host in self.nornir_manager.nornir.inventory.hosts.items():
                host_info = {
                    "name": name,
                    "hostname": host.hostname,
                    "platform": getattr(host, 'platform', 'unknown'),
                    "groups": [str(group) for group in host.groups],
                    "data": dict(host.data)
                }
                hosts_list.append(host_info)
            
            return json.dumps(hosts_list, indent=2)
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
    nornir_manager: NornirManager = Field(default_factory=NornirManager)
    
    def _run(self, hostnames_json: str) -> str:
        try:
            # Parse hostnames from JSON string
            hostnames = json.loads(hostnames_json)
            if not isinstance(hostnames, list):
                raise ValueError("Input must be a JSON array of hostnames")

            # Filter hosts and run the task
            filtered_nr = self.nornir_manager.filter_hosts(hostnames)
            result = filtered_nr.run(task=get_interfaces_ip)

            # Format results
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
        # Async implementation would go here
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
    nornir_manager: NornirManager = Field(default_factory=NornirManager)
    
    def _run(self, hostnames_json: str) -> str:
        try:
            # Parse hostnames from JSON string
            hostnames = json.loads(hostnames_json)
            if not isinstance(hostnames, list):
                raise ValueError("Input must be a JSON array of hostnames")

            # Filter hosts and run the task
            filtered_nr = self.nornir_manager.filter_hosts(hostnames)
            result = filtered_nr.run(task=get_interfaces)

            # Format results
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