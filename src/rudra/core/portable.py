"""
RUDRA USB Portability Subsystem (UP - PORT).
"""
import os
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


class PortableRuntime:
    def __init__(self, custom_root: Optional[Path] = None):
        if custom_root:
            self.root_path = Path(custom_root).resolve()
        elif "RUDRA_ROOT" in os.environ:
            self.root_path = Path(os.environ["RUDRA_ROOT"]).resolve()
        else:
            # Default to current working directory or executable directory
            self.root_path = Path(os.getcwd()).resolve()

        self.config_dir = self.root_path / "config"
        self.data_dir = self.root_path / "data"
        self.logs_dir = self.root_path / "logs"
        self.reports_dir = self.root_path / "reports"
        self.sessions_dir = self.root_path / "sessions"

    def initialize_structure(self) -> Dict[str, str]:
        """Ensure portable directories exist without system installation."""
        dirs = {
            "root": self.root_path,
            "config": self.config_dir,
            "data": self.data_dir,
            "logs": self.logs_dir,
            "reports": self.reports_dir,
            "sessions": self.sessions_dir,
        }
        status_map = {}
        for name, path in dirs.items():
            path.mkdir(parents=True, exist_ok=True)
            status_map[name] = str(path)
        return status_map

    def get_storage_capacity(self) -> Dict[str, Any]:
        """Check portable storage drive capacity without fake data."""
        try:
            total, used, free = shutil.disk_usage(self.root_path)
            return {
                "status": "OBSERVED",
                "root_path": str(self.root_path),
                "total_bytes": total,
                "used_bytes": used,
                "free_bytes": free,
                "total_gb": round(total / (1024 ** 3), 2),
                "free_gb": round(free / (1024 ** 3), 2),
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "root_path": str(self.root_path),
                "error": str(e),
            }

    def validate_environment(self) -> Dict[str, Any]:
        """Validate portable environment health and write permissions."""
        write_test_file = self.data_dir / ".write_test"
        writable = False
        try:
            self.initialize_structure()
            with open(write_test_file, "w") as f:
                f.write("rudra_write_test")
            if write_test_file.exists():
                os.remove(write_test_file)
                writable = True
        except Exception:
            writable = False

        return {
            "python_executable": sys.executable,
            "is_writable": writable,
            "root_path": str(self.root_path),
            "initialized": writable,
        }
