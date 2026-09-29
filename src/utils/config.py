"""
Configuration loader and management for Product Analytics & Experimentation Platform.
"""

from pathlib import Path
from typing import Any, Dict
import yaml


def get_project_root() -> Path:
    """Returns the root directory of the project."""
    return Path(__file__).resolve().parent.parent.parent


def load_config(config_path: str | None = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Optional explicit path to config file.
        
    Returns:
        Dict containing configuration parameters.
    """
    if config_path is None:
        root = get_project_root()
        config_file = root / "config" / "config.yaml"
    else:
        config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found at: {config_file}")

    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Ensure resolved absolute paths
    root = get_project_root()
    if "paths" in config:
        for key, val in config["paths"].items():
            config["paths"][key] = str(root / val)

    return config
