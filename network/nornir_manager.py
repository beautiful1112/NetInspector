from nornir import InitNornir
from nornir.core.inventory import Host
from typing import List, Dict, Any
import logging
import os
import yaml

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