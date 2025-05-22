from nornir_napalm.plugins.tasks import napalm_get
from nornir.core.task import Result, Task
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def get_interfaces_ip(task: Task) -> Result:
    """Get IP addresses of all interfaces on the device"""
    try:
        logger.info(f"Attempting to get interfaces IP for {task.host.name}")
        logger.debug(f"Host connection details: platform={task.host.platform}, hostname={task.host.hostname}")
        
        result = task.run(
            task=napalm_get,
            getters=["interfaces_ip"]
        )
        
        logger.info(f"Successfully retrieved interfaces IP for {task.host.name}")
        logger.debug(f"Raw result: {result[0].result}")
        
        # Extract interfaces_ip from the result
        interfaces_ip = result[0].result.get("interfaces_ip", {})
        
        # Format the output for better readability
        formatted_output = {}
        for interface, ip_data in interfaces_ip.items():
            formatted_output[interface] = {
                "ipv4": ip_data.get("ipv4", {}),
                "ipv6": ip_data.get("ipv6", {})
            }
        
        return Result(
            host=task.host,
            result=formatted_output
        )
    except Exception as e:
        logger.error(f"Error getting interfaces IP for {task.host.name}: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Full exception details: {repr(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        )

def get_interfaces(task: Task) -> Result:
    """Get information about all interfaces on the device"""
    try:
        result = task.run(
            task=napalm_get,
            getters=["interfaces"]
        )
        
        return Result(
            host=task.host,
            result=result[0].result.get("interfaces", {})
        )
    except Exception as e:
        logger.error(f"Error getting interfaces for {task.host.name}: {str(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        )

def get_config(task: Task) -> Result:
    """Get complete device configuration"""
    try:
        logger.info(f"Attempting to get complete config for {task.host.name}")
        
        result = task.run(
            task=napalm_get,
            getters=["config"]
        )
        
        logger.info(f"Successfully retrieved config for {task.host.name}")
        
        return Result(
            host=task.host,
            result=result[0].result.get("config", {})
        )
    except Exception as e:
        logger.error(f"Error getting config for {task.host.name}: {str(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        )

def get_facts(task: Task) -> Result:
    """Get basic device information (facts)"""
    try:
        logger.info(f"Attempting to get facts for {task.host.name}")
        
        result = task.run(
            task=napalm_get,
            getters=["facts"]
        )
        
        logger.info(f"Successfully retrieved facts for {task.host.name}")
        
        return Result(
            host=task.host,
            result=result[0].result.get("facts", {})
        )
    except Exception as e:
        logger.error(f"Error getting facts for {task.host.name}: {str(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        )

def get_environment(task: Task) -> Result:
    """Get device environment information (CPU, memory, temperature, etc.)"""
    try:
        logger.info(f"Attempting to get environment info for {task.host.name}")
        
        result = task.run(
            task=napalm_get,
            getters=["environment"]
        )
        
        logger.info(f"Successfully retrieved environment info for {task.host.name}")
        
        return Result(
            host=task.host,
            result=result[0].result.get("environment", {})
        )
    except Exception as e:
        logger.error(f"Error getting environment info for {task.host.name}: {str(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        )

def get_routes(task: Task) -> Result:
    """Get routing table information"""
    try:
        logger.info(f"Attempting to get routes for {task.host.name}")
        
        result = task.run(
            task=napalm_get,
            getters=["routes"]
        )
        
        logger.info(f"Successfully retrieved routes for {task.host.name}")
        
        return Result(
            host=task.host,
            result=result[0].result.get("routes", {})
        )
    except Exception as e:
        logger.error(f"Error getting routes for {task.host.name}: {str(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        )

def get_arp_table(task: Task) -> Result:
    """Get ARP table information"""
    try:
        logger.info(f"Attempting to get ARP table for {task.host.name}")
        
        result = task.run(
            task=napalm_get,
            getters=["arp_table"]
        )
        
        logger.info(f"Successfully retrieved ARP table for {task.host.name}")
        
        return Result(
            host=task.host,
            result=result[0].result.get("arp_table", {})
        )
    except Exception as e:
        logger.error(f"Error getting ARP table for {task.host.name}: {str(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        )

def get_mac_address_table(task: Task) -> Result:
    """Get MAC address table information"""
    try:
        logger.info(f"Attempting to get MAC address table for {task.host.name}")
        
        result = task.run(
            task=napalm_get,
            getters=["mac_address_table"]
        )
        
        logger.info(f"Successfully retrieved MAC address table for {task.host.name}")
        
        return Result(
            host=task.host,
            result=result[0].result.get("mac_address_table", {})
        )
    except Exception as e:
        logger.error(f"Error getting MAC address table for {task.host.name}: {str(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        )

def get_bgp_neighbors(task: Task) -> Result:
    """Get BGP neighbors information"""
    try:
        logger.info(f"Attempting to get BGP neighbors for {task.host.name}")
        
        result = task.run(
            task=napalm_get,
            getters=["bgp_neighbors"]
        )
        
        logger.info(f"Successfully retrieved BGP neighbors for {task.host.name}")
        
        return Result(
            host=task.host,
            result=result[0].result.get("bgp_neighbors", {})
        )
    except Exception as e:
        logger.error(f"Error getting BGP neighbors for {task.host.name}: {str(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        )

def get_bgp_config(task: Task) -> Result:
    """Get BGP configuration"""
    try:
        logger.info(f"Attempting to get BGP configuration for {task.host.name}")
        
        result = task.run(
            task=napalm_get,
            getters=["bgp_config"]
        )
        
        logger.info(f"Successfully retrieved BGP configuration for {task.host.name}")
        
        return Result(
            host=task.host,
            result=result[0].result.get("bgp_config", {})
        )
    except Exception as e:
        logger.error(f"Error getting BGP configuration for {task.host.name}: {str(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        )

def get_ospf_neighbors(task: Task) -> Result:
    """Get OSPF neighbors information"""
    try:
        logger.info(f"Attempting to get OSPF neighbors for {task.host.name}")
        
        result = task.run(
            task=napalm_get,
            getters=["ospf_neighbors"]
        )
        
        logger.info(f"Successfully retrieved OSPF neighbors for {task.host.name}")
        
        return Result(
            host=task.host,
            result=result[0].result.get("ospf_neighbors", {})
        )
    except Exception as e:
        logger.error(f"Error getting OSPF neighbors for {task.host.name}: {str(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        )

def get_ospf_config(task: Task) -> Result:
    """Get OSPF configuration"""
    try:
        logger.info(f"Attempting to get OSPF configuration for {task.host.name}")
        
        result = task.run(
            task=napalm_get,
            getters=["ospf_config"]
        )
        
        logger.info(f"Successfully retrieved OSPF configuration for {task.host.name}")
        
        return Result(
            host=task.host,
            result=result[0].result.get("ospf_config", {})
        )
    except Exception as e:
        logger.error(f"Error getting OSPF configuration for {task.host.name}: {str(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        )

def ping_host(task: Task, destination: str, source: str = None, size: int = 56, count: int = 5) -> Result:
    """Execute ping from network device to destination
    
    Args:
        task: Nornir task object
        destination: Destination IP address to ping
        source: Source IP address to use (optional)
        size: Size of ping packet in bytes (default: 56)
        count: Number of ping packets to send (default: 5)
    """
    try:
        logger.info(f"Attempting to ping {destination} from {task.host.name}")
        if source:
            logger.info(f"Using source IP: {source}")
        
        # Get the NAPALM connection
        device = task.host.get_connection("napalm")
        
        # Execute ping command
        ping_result = device.ping(
            destination=destination,
            source=source,
            size=size,
            count=count
        )
        
        logger.info(f"Successfully executed ping from {task.host.name} to {destination}")
        logger.debug(f"Ping result: {ping_result}")
        
        return Result(
            host=task.host,
            result=ping_result
        )
    except Exception as e:
        logger.error(f"Error executing ping from {task.host.name} to {destination}: {str(e)}")
        return Result(
            host=task.host,
            failed=True,
            exception=str(e)
        ) 