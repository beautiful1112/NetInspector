from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from network.nornir_manager import NornirManager
from network.napalm_operations import get_interfaces_ip, get_interfaces
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
nornir_manager = NornirManager()

@router.get("/hosts")
async def get_hosts() -> List[str]:
    """Get list of all available hosts"""
    try:
        return nornir_manager.get_hosts()
    except Exception as e:
        logger.error(f"Error getting hosts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interfaces/ip")
async def get_interfaces_ip_info(hostnames: List[str]) -> Dict[str, Any]:
    """Get IP information for all interfaces on specified hosts"""
    try:
        filtered_nr = nornir_manager.filter_hosts(hostnames)
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
        
        return formatted_results
    except Exception as e:
        logger.error(f"Error getting interfaces IP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interfaces")
async def get_interfaces_info(hostnames: List[str]) -> Dict[str, Any]:
    """Get information about all interfaces on specified hosts"""
    try:
        filtered_nr = nornir_manager.filter_hosts(hostnames)
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
        
        return formatted_results
    except Exception as e:
        logger.error(f"Error getting interfaces info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 