from typing import List, Dict, Any
from langchain.tools import BaseTool
from pydantic import Field
import json
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class NetworkAPIClient:
    """Client for handling network API requests with retry mechanism"""
    def __init__(self):
        # API base URL configuration
        self.base_url = "http://localhost:8000"
        
        # Configure session with retry mechanism
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,                  # Number of retries
            backoff_factor=1,         # Time factor between retries
            status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
        )
        
        # Apply retry strategy to both HTTP and HTTPS
        self.session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

class GetHostsTool(BaseTool):
    name: str = "get_hosts"
    description: str = """
    Get a list of all available network devices.
    Input can be any string, it will be ignored.
    Returns a list of all configured hosts with their basic information.
    Example: "list all hosts"
    """
    api_client: NetworkAPIClient = Field(default_factory=NetworkAPIClient)
    
    def _run(self, query: str) -> str:
        try:
            response = self.api_client.session.get(f"{self.api_client.base_url}/hosts")
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in GetHostsTool: {str(e)}")
            return json.dumps({"error": f"API request failed: {str(e)}"})

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
    api_client: NetworkAPIClient = Field(default_factory=NetworkAPIClient)
    
    def _run(self, hostnames_json: str) -> str:
        try:
            hostnames = json.loads(hostnames_json)
            if not isinstance(hostnames, list):
                raise ValueError("Input must be a JSON array of hostnames")

            response = self.api_client.session.post(
                f"{self.api_client.base_url}/interfaces/ip",
                json=hostnames
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in GetInterfacesIPTool: {str(e)}")
            return json.dumps({"error": f"API request failed: {str(e)}"})
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON input: {str(e)}")
            return json.dumps({"error": "Invalid JSON input format"})

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
    api_client: NetworkAPIClient = Field(default_factory=NetworkAPIClient)
    
    def _run(self, hostnames_json: str) -> str:
        try:
            hostnames = json.loads(hostnames_json)
            if not isinstance(hostnames, list):
                raise ValueError("Input must be a JSON array of hostnames")

            response = self.api_client.session.post(
                f"{self.api_client.base_url}/interfaces",
                json=hostnames
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in GetInterfacesDetailTool: {str(e)}")
            return json.dumps({"error": f"API request failed: {str(e)}"})
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON input: {str(e)}")
            return json.dumps({"error": "Invalid JSON input format"})

    async def _arun(self, hostnames_json: str) -> str:
        raise NotImplementedError("Async version not implemented") 