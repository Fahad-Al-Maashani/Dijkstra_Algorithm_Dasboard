"""
Configuration management for the tax calculator
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class AppConfig:
    """Application configuration manager"""

    DEFAULT_CONFIG = {
        'app': {
            'name': 'Oman Tax Calculator',
            'version': '1.0.0',
            'author': 'Tax Calculator Development Team'
        },
        'ui': {
            'window_width': 800,
            'window_height': 600,
            'theme': 'default',
            'language': 'en'
        },
        'calculation': {
            'default_currency': 'OMR',
            'decimal_places': 2,
            'auto_save': True,
            'backup_calculations': True
        },
        'file_paths': {
            'calculations_dir': 'calculations',
            'exports_dir': 'exports',
            'backups_dir': 'backups'
        },
        'tax_settings': {
            'tax_year': 2028,
            'threshold': 42000.0,
            'rate': 0.05
        }
    }

    def __init__(self, config_file: str = None):
        """Initialize configuration manager"""
        if config_file is None:
            config_dir = Path.home() / '.oman_tax_calculator'
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / 'config.json'

        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    return self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            except (json.JSONDecodeError, IOError):
                pass

        # Return default config if file doesn't exist or is invalid
        return self.DEFAULT_CONFIG.copy()

    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Merge loaded config with default config"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def get_app_info(self) -> Dict[str, str]:
        """Get application information"""
        return self.config['app']

    def get_ui_settings(self) -> Dict[str, Any]:
        """Get UI settings"""
        return self.config['ui']

    def get_calculation_settings(self) -> Dict[str, Any]:
        """Get calculation settings"""
        return self.config['calculation']

    def get_file_paths(self) -> Dict[str, str]:
        """Get file path settings"""
        return self.config['file_paths']

    def get_tax_settings(self) -> Dict[str, Any]:
        """Get tax calculation settings"""
        return self.config['tax_settings']

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()


# Global configuration instance
config = AppConfig()