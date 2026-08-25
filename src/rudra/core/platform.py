"""
RUDRA Operating System and Platform Abstraction Layer.
"""
import sys
import platform
from typing import Dict, Any


class PlatformAbstraction:
    @staticmethod
    def get_platform_info() -> Dict[str, Any]:
        return {
            "system": sys.platform,
            "os_name": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "is_windows": sys.platform.startswith("win"),
            "is_linux": sys.platform.startswith("linux"),
            "is_darwin": sys.platform == "darwin",
        }
