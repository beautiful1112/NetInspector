from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import Field, BaseModel
import json
import logging
from network.nornir_manager import NornirManager
from network.napalm_operations import (
    get_interfaces,
    get_interfaces_ip,
    get_config,
    get_facts,
    get_environment,
    get_routes,
    get_arp_table,
    get_mac_address_table
)

logger = logging.getLogger(__name__)

# Create a single shared instance of NornirManager
_shared_nornir_manager = None

def get_nornir_manager():
    global _shared_nornir_manager
    if _shared_nornir_manager is None:
        _shared_nornir_manager = NornirManager()
    return _shared_nornir_manager

# Input schemas for tools
class DummyInput(BaseModel):
    query: str = "all"

class HostnameInput(BaseModel):
    hostname: str

class HostListInput(BaseModel):
    hostnames: List[str]

class PingInput(BaseModel):
    hostname: str
    destination: str
    source: Optional[str] = None
    size: Optional[int] = 56
    count: Optional[int] = 5

# Tools
class GetHostsTool(BaseTool):
    name: str = "get_hosts"
    description: str = "Get a list of all available network devices. Input can be any string."
    args_schema: type = DummyInput
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
    description: str = "Get IP addresses of all interfaces on a specified network device. Input is the hostname."
    args_schema: type = HostnameInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)

    def _run(self, hostname: str) -> str:
        try:
            filtered_nr = self.nornir_manager.filter_hosts([hostname])
            result = filtered_nr.run(task=get_interfaces_ip)
            formatted_results = {}
            for host, host_result in result.items():
                if host_result.failed:
                    formatted_results[host] = {
                        "status": "failed",
                        "error": str(host_result.exception)
                    }
                else:
                    formatted_results[host] = {
                        "status": "success",
                        "data": host_result.result
                    }
            return json.dumps(formatted_results, indent=2)
        except Exception as e:
            logger.error(f"Error in GetInterfacesIPTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostname: str) -> str:
        raise NotImplementedError("Async version not implemented")

class GetInterfacesDetailTool(BaseTool):
    name: str = "get_interfaces_detail"
    description: str = "Get detailed information about all interfaces. Input is a list of hostnames."
    args_schema: type = HostListInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames: List[str]) -> str:
        try:
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

    async def _arun(self, hostnames: List[str]) -> str:
        raise NotImplementedError("Async version not implemented")

class GetConfigTool(BaseTool):
    name: str = "get_config"
    description: str = "Get complete device configuration. Input is a list of hostnames."
    args_schema: type = HostListInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames: List[str]) -> str:
        try:
            result = self.nornir_manager.get_device_config(hostnames)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in GetConfigTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostnames: List[str]) -> str:
        raise NotImplementedError("Async version not implemented")

class GetFactsTool(BaseTool):
    name: str = "get_facts"
    description: str = "Get basic device information (facts). Input is a list of hostnames."
    args_schema: type = HostListInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames: List[str]) -> str:
        try:
            result = self.nornir_manager.get_device_facts(hostnames)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in GetFactsTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostnames: List[str]) -> str:
        raise NotImplementedError("Async version not implemented")

class GetEnvironmentTool(BaseTool):
    name: str = "get_environment"
    description: str = "Get device environment information. Input is a list of hostnames."
    args_schema: type = HostListInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames: List[str]) -> str:
        try:
            result = self.nornir_manager.get_device_environment(hostnames)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in GetEnvironmentTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostnames: List[str]) -> str:
        raise NotImplementedError("Async version not implemented")

class GetRoutesTool(BaseTool):
    name: str = "get_routes"
    description: str = "Get routing table information. Input is a list of hostnames."
    args_schema: type = HostListInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames: List[str]) -> str:
        try:
            result = self.nornir_manager.get_device_routes(hostnames)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in GetRoutesTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostnames: List[str]) -> str:
        raise NotImplementedError("Async version not implemented")

class GetARPTableTool(BaseTool):
    name: str = "get_arp_table"
    description: str = "Get ARP table information. Input is a list of hostnames."
    args_schema: type = HostListInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames: List[str]) -> str:
        try:
            result = self.nornir_manager.get_device_arp_table(hostnames)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in GetARPTableTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostnames: List[str]) -> str:
        raise NotImplementedError("Async version not implemented")

class GetMACTableTool(BaseTool):
    name: str = "get_mac_table"
    description: str = "Get MAC address table information. Input is a list of hostnames."
    args_schema: type = HostListInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames: List[str]) -> str:
        try:
            result = self.nornir_manager.get_device_mac_table(hostnames)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in GetMACTableTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostnames: List[str]) -> str:
        raise NotImplementedError("Async version not implemented")

class GetBGPNeighborsTool(BaseTool):
    name: str = "get_bgp_neighbors"
    description: str = "Get BGP neighbors information. Input is a list of hostnames."
    args_schema: type = HostListInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames: List[str]) -> str:
        try:
            result = self.nornir_manager.get_device_bgp_neighbors(hostnames)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in GetBGPNeighborsTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostnames: List[str]) -> str:
        raise NotImplementedError("Async version not implemented")

class GetBGPConfigTool(BaseTool):
    name: str = "get_bgp_config"
    description: str = "Get BGP configuration. Input is a list of hostnames."
    args_schema: type = HostListInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames: List[str]) -> str:
        try:
            result = self.nornir_manager.get_device_bgp_config(hostnames)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in GetBGPConfigTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostnames: List[str]) -> str:
        raise NotImplementedError("Async version not implemented")

class GetOSPFNeighborsTool(BaseTool):
    name: str = "get_ospf_neighbors"
    description: str = "Get OSPF neighbors information. Input is a list of hostnames."
    args_schema: type = HostListInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames: List[str]) -> str:
        try:
            result = self.nornir_manager.get_device_ospf_neighbors(hostnames)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in GetOSPFNeighborsTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostnames: List[str]) -> str:
        raise NotImplementedError("Async version not implemented")

class GetOSPFConfigTool(BaseTool):
    name: str = "get_ospf_config"
    description: str = "Get OSPF configuration. Input is a list of hostnames."
    args_schema: type = HostListInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostnames: List[str]) -> str:
        try:
            result = self.nornir_manager.get_device_ospf_config(hostnames)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in GetOSPFConfigTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostnames: List[str]) -> str:
        raise NotImplementedError("Async version not implemented")

class PingTool(BaseTool):
    name: str = "ping"
    description: str = (
        "Execute ping from a network device to a destination IP. "
        "Input should be a JSON string with keys: hostname, destination, source (optional), size (optional), count (optional). "
        "Example: '{\"hostname\": \"switch01\", \"destination\": \"192.168.1.1\"}'"
    )
    args_schema: type = PingInput
    nornir_manager: NornirManager = Field(default_factory=get_nornir_manager)
    
    def _run(self, hostname: str, destination: str, source: Optional[str] = None, size: int = 56, count: int = 5) -> str:
        try:
            result = self.nornir_manager.ping(
                hostname=hostname,
                destination=destination,
                source=source,
                size=size,
                count=count
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in PingTool: {str(e)}")
            return json.dumps({"error": str(e)})

    async def _arun(self, hostname: str, destination: str, source: Optional[str] = None, size: int = 56, count: int = 5) -> str:
        raise NotImplementedError("Async version not implemented")

def get_all_tools() -> List[BaseTool]:
    """Get all available network tools"""
    return [
        GetHostsTool(),
        GetInterfacesIPTool(),
        GetInterfacesDetailTool(),
        GetConfigTool(),
        GetFactsTool(),
        GetEnvironmentTool(),
        GetRoutesTool(),
        GetARPTableTool(),
        GetMACTableTool(),
        GetBGPNeighborsTool(),
        GetBGPConfigTool(),
        GetOSPFNeighborsTool(),
        GetOSPFConfigTool(),
        PingTool()
    ] 