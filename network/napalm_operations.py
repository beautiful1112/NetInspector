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