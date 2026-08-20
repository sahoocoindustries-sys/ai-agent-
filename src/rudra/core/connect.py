"""
RUDRA Device Connection and Capability Discovery Subsystem (CN - CONNECT).
"""
import sys
import os
import platform
import shutil
import ctypes
from typing import Dict, Any, List
from rudra.core.models import Status


class HostConnection:
    @staticmethod
    def get_host_info() -> Dict[str, Any]:
        """Collect real host device and system context."""
        info = {}
        # OS and Architecture
        info["os_name"] = platform.system()
        info["os_version"] = platform.version()
        info["os_release"] = platform.release()
        info["architecture"] = platform.machine()
        info["hostname"] = platform.node()
        info["python_version"] = platform.python_version()

        # Admin / Elevation Status
        try:
            if sys.platform.startswith("win"):
                is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
            else:
                is_admin = (os.geteuid() == 0)
            info["is_elevated"] = is_admin
            info["elevation_status"] = "OBSERVED"
        except Exception:
            info["is_elevated"] = False
            info["elevation_status"] = "UNAVAILABLE"

        # Memory Info where permitted
        try:
            if hasattr(os, "sysconf"):
                if "SC_PAGE_SIZE" in os.sysconf_names and "SC_PHYS_PAGES" in os.sysconf_names:
                    page_size = os.sysconf("SC_PAGE_SIZE")
                    total_pages = os.sysconf("SC_PHYS_PAGES")
                    total_bytes = page_size * total_pages
                    info["total_ram_gb"] = round(total_bytes / (1024 ** 3), 2)
                    info["ram_status"] = "OBSERVED"
                else:
                    info["ram_status"] = "UNAVAILABLE"
            else:
                info["ram_status"] = "UNAVAILABLE"
        except Exception:
            info["ram_status"] = "UNAVAILABLE"

        # CPU Cores
        try:
            info["cpu_cores"] = os.cpu_count() or 1
            info["cpu_status"] = "OBSERVED"
        except Exception:
            info["cpu_status"] = "UNAVAILABLE"

        return info


class CapabilityRegistry:
    def __init__(self):
        self._capabilities = {
            "HOST_CONNECT": Status.VERIFIED.value,
            "PORTABLE_MODE": Status.VERIFIED.value,
            "CONSENT_MANAGEMENT": Status.VERIFIED.value,
            "SESSION_MANAGEMENT": Status.VERIFIED.value,
            "TOOL_REGISTRATION": Status.VERIFIED.value,
            "EVIDENCE_COLLECTION": Status.VERIFIED.value,
            "VERITAS_VERIFICATION": Status.VERIFIED.value,
            "SYSTEM_DIAGNOSTICS": Status.NOT_IMPLEMENTED.value,
            "SECURITY_SCAN": Status.NOT_IMPLEMENTED.value,
            "SOFTWARE_DOCTOR": Status.NOT_IMPLEMENTED.value,
            "AI_REASONING": Status.NOT_IMPLEMENTED.value,
            "VOICE_INTERFACE": Status.NOT_IMPLEMENTED.value,
            "DEFENSIVE_REMEDIATION": Status.NOT_IMPLEMENTED.value,
            "MOBILE_CONTROL": Status.ACCESS_UNAVAILABLE.value,
        }

    def get_capabilities(self) -> Dict[str, str]:
        return dict(self._capabilities)

    def is_capability_available(self, capability_name: str) -> bool:
        return self._capabilities.get(capability_name) in (Status.VERIFIED.value, Status.SUCCESS.value)
