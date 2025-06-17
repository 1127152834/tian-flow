# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Branding configuration for the application.

Provides centralized brand name and related configuration.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from functools import lru_cache

from src.config import load_yaml_config


@dataclass
class BrandingConfig:
    """Configuration for application branding"""
    name: str = "Olight"
    display_name: str = "Olight"
    description: str = "Your personal Deep Research assistant"
    tagline: str = "Deep Research at Your Fingertips"
    website: Optional[str] = None


def _get_config_file_path() -> str:
    """Get the path to the configuration file."""
    return str((Path(__file__).parent.parent.parent / "conf.yaml").resolve())


@lru_cache(maxsize=1)
def load_branding_config() -> BrandingConfig:
    """
    Load branding configuration from YAML file and environment variables.
    
    Environment variables take precedence over YAML configuration.
    
    Returns:
        BrandingConfig object with branding settings
    """
    try:
        # Load YAML configuration
        yaml_config = load_yaml_config(_get_config_file_path())
        branding_yaml = yaml_config.get("BRANDING", {})
        
        # Get environment variables
        branding_env = {
            "name": os.getenv("BRAND_NAME"),
            "display_name": os.getenv("BRAND_DISPLAY_NAME"),
            "description": os.getenv("BRAND_DESCRIPTION"),
            "tagline": os.getenv("BRAND_TAGLINE"),
            "website": os.getenv("BRAND_WEBSITE"),
        }
        
        # Remove None values from environment config
        branding_env = {k: v for k, v in branding_env.items() if v is not None}
        
        # Merge configurations (env takes precedence)
        branding_config = {**branding_yaml, **branding_env}
        
        # Create BrandingConfig with defaults
        return BrandingConfig(
            name=branding_config.get("name", "Olight"),
            display_name=branding_config.get("display_name", "Olight"),
            description=branding_config.get("description", "Your personal Deep Research assistant"),
            tagline=branding_config.get("tagline", "Deep Research at Your Fingertips"),
            website=branding_config.get("website"),
        )
        
    except Exception as e:
        print(f"Warning: Failed to load branding configuration: {e}")
        # Return default configuration
        return BrandingConfig()


# Global branding configuration instance
BRANDING = load_branding_config()
