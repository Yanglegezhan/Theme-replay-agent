"""Configuration manager for loading and accessing configuration."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigManager:
    """Manages configuration loading and access."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to config file. If None, looks for config.yaml in config/ directory.
        """
        if config_path is None:
            # Default to config/config.yaml relative to project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "config.yaml"
            
            # If config.yaml doesn't exist, use example config
            if not config_path.exists():
                config_path = project_root / "config" / "config.example.yaml"
        
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'llm.api_key')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.get('llm', {})
    
    def get_data_source_config(self) -> Dict[str, Any]:
        """Get data source configuration."""
        return self.get('data_source', {})
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis parameters configuration."""
        return self.get('analysis', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get('logging', {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration."""
        return self.get('output', {})
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get full configuration dictionary."""
        return self._config
