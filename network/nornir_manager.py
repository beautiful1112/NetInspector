from nornir import InitNornir
from nornir.core.inventory import Host
from typing import List, Dict, Any
import logging
import os
import yaml
from .napalm_operations import (
    get_interfaces_ip,
    get_interfaces,
    get_config,
    get_facts,
    get_environment,
    get_routes,
    get_arp_table,
    get_mac_address_table,
    get_bgp_neighbors,
    get_bgp_config,
    get_ospf_neighbors,
    get_ospf_config,
    ping_host
)

logger = logging.getLogger(__name__)

class NornirManager:
    def __init__(self):
        self.nornir = None
        self.settings = self._load_settings()
        
        # Configure logging
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'nornir.log')),
                logging.StreamHandler()
            ]
        )
        
        self._initialize_nornir()

    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from YAML file"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        settings_file = os.path.join(project_root, "utils", "settings.yaml")
        
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = yaml.safe_load(f)
            logger.debug(f"Loaded settings: {settings}")
            return settings

    def _initialize_nornir(self):
        """Initialize Nornir with configuration"""
        try:
            # Get absolute paths for config files
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            host_file = os.path.join(project_root, "config", "hosts.yaml")
            group_file = os.path.join(project_root, "config", "groups.yaml")
            defaults_file = os.path.join(project_root, "config", "defaults.yaml")

            logger.info(f"Initializing Nornir with config files:")
            logger.info(f"  - Hosts: {host_file}")
            logger.info(f"  - Groups: {group_file}")
            logger.info(f"  - Defaults: {defaults_file}")

            self.nornir = InitNornir(
                runner={
                    "plugin": "threaded",
                    "options": {
                        "num_workers": 100,
                    },
                },
                inventory={
                    "plugin": "SimpleInventory",
                    "options": {
                        "host_file": host_file,
                        "group_file": group_file,
                        "defaults_file": defaults_file,
                    },
                },
            )
            logger.info("Nornir initialized successfully")
            logger.debug(f"Inventory hosts: {list(self.nornir.inventory.hosts.keys())}")
        except Exception as e:
            logger.error(f"Failed to initialize Nornir: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Full exception details: {repr(e)}")
            raise

    def get_hosts(self) -> List[str]:
        """Get list of all host names"""
        return list(self.nornir.inventory.hosts.keys())

    def filter_hosts(self, hostnames: List[str]):
        """Filter Nornir inventory to only include specified hosts"""
        logger.info(f"Filtering hosts: {hostnames}")
        filtered = self.nornir.filter(filter_func=lambda h: h.name in hostnames)
        logger.debug(f"Filtered inventory hosts: {list(filtered.inventory.hosts.keys())}")
        return filtered

    def get_host_info(self, hostname: str) -> Dict[str, Any]:
        """Get detailed information about a specific host"""
        host: Host = self.nornir.inventory.hosts.get(hostname)
        if not host:
            logger.warning(f"Host not found: {hostname}")
            return {}
        info = {
            "name": host.name,
            "hostname": host.hostname,
            "platform": host.platform,
            "groups": list(host.groups.keys()),
            "data": host.data
        }
        logger.debug(f"Host info for {hostname}: {info}")
        return info

    def get_device_config(self, hostnames: List[str]) -> Dict[str, Any]:
        """Get complete configuration for specified devices"""
        try:
            filtered = self.filter_hosts(hostnames)
            result = filtered.run(task=get_config)
            return {host: data[0].result for host, data in result.items()}
        except Exception as e:
            logger.error(f"Error getting device config: {str(e)}")
            return {}

    def get_device_facts(self, hostnames: List[str]) -> Dict[str, Any]:
        """Get basic device information for specified devices"""
        try:
            filtered = self.filter_hosts(hostnames)
            result = filtered.run(task=get_facts)
            return {host: data[0].result for host, data in result.items()}
        except Exception as e:
            logger.error(f"Error getting device facts: {str(e)}")
            return {}

    def get_device_environment(self, hostnames: List[str]) -> Dict[str, Any]:
        """Get environment information for specified devices"""
        try:
            filtered = self.filter_hosts(hostnames)
            result = filtered.run(task=get_environment)
            return {host: data[0].result for host, data in result.items()}
        except Exception as e:
            logger.error(f"Error getting device environment: {str(e)}")
            return {}

    def get_device_routes(self, hostnames: List[str]) -> Dict[str, Any]:
        """Get routing table information for specified devices"""
        try:
            filtered = self.filter_hosts(hostnames)
            result = filtered.run(task=get_routes)
            return {host: data[0].result for host, data in result.items()}
        except Exception as e:
            logger.error(f"Error getting device routes: {str(e)}")
            return {}

    def get_device_arp_table(self, hostnames: List[str]) -> Dict[str, Any]:
        """Get ARP table information for specified devices"""
        try:
            filtered = self.filter_hosts(hostnames)
            result = filtered.run(task=get_arp_table)
            return {host: data[0].result for host, data in result.items()}
        except Exception as e:
            logger.error(f"Error getting device ARP table: {str(e)}")
            return {}

    def get_device_mac_table(self, hostnames: List[str]) -> Dict[str, Any]:
        """Get MAC address table information for specified devices"""
        try:
            filtered = self.filter_hosts(hostnames)
            result = filtered.run(task=get_mac_address_table)
            return {host: data[0].result for host, data in result.items()}
        except Exception as e:
            logger.error(f"Error getting device MAC table: {str(e)}")
            return {}

    def get_device_bgp_neighbors(self, hostnames: List[str]) -> Dict[str, Any]:
        """Get BGP neighbors information for specified devices"""
        try:
            filtered = self.filter_hosts(hostnames)
            result = filtered.run(task=get_bgp_neighbors)
            return {host: data[0].result for host, data in result.items()}
        except Exception as e:
            logger.error(f"Error getting device BGP neighbors: {str(e)}")
            return {}

    def get_device_bgp_config(self, hostnames: List[str]) -> Dict[str, Any]:
        """Get BGP configuration for specified devices"""
        try:
            filtered = self.filter_hosts(hostnames)
            result = filtered.run(task=get_bgp_config)
            return {host: data[0].result for host, data in result.items()}
        except Exception as e:
            logger.error(f"Error getting device BGP config: {str(e)}")
            return {}

    def get_device_ospf_neighbors(self, hostnames: List[str]) -> Dict[str, Any]:
        """Get OSPF neighbors information for specified devices"""
        try:
            filtered = self.filter_hosts(hostnames)
            result = filtered.run(task=get_ospf_neighbors)
            return {host: data[0].result for host, data in result.items()}
        except Exception as e:
            logger.error(f"Error getting device OSPF neighbors: {str(e)}")
            return {}

    def get_device_ospf_config(self, hostnames: List[str]) -> Dict[str, Any]:
        """Get OSPF configuration for specified devices"""
        try:
            filtered = self.filter_hosts(hostnames)
            result = filtered.run(task=get_ospf_config)
            return {host: data[0].result for host, data in result.items()}
        except Exception as e:
            logger.error(f"Error getting device OSPF config: {str(e)}")
            return {}

    def ping_from_device(self, hostname: str, destination: str, source: str = None, size: int = 56, count: int = 5) -> Dict[str, Any]:
        """Execute ping from specified device to destination
        
        Args:
            hostname: Name of the device to execute ping from
            destination: Destination IP address to ping
            source: Source IP address to use (optional)
            size: Size of ping packet in bytes (default: 56)
            count: Number of ping packets to send (default: 5)
        """
        try:
            filtered = self.filter_hosts([hostname])
            result = filtered.run(
                task=ping_host,
                destination=destination,
                source=source,
                size=size,
                count=count
            )
            return {host: data[0].result for host, data in result.items()}
        except Exception as e:
            logger.error(f"Error executing ping from {hostname} to {destination}: {str(e)}")
            return {} 