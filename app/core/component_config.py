from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

from dynaconf import Dynaconf


class ComponentConfig:
    """Handles loading and accessing component configurations."""

    def __init__(self) -> None:
        """Initialize the ComponentConfig with a directory for components."""
        self.components_dir = Path("app/prompts/components")
        self._component_settings = {}
        self._load_components()

    def _load_components(self) -> None:
        """Load all component configurations from individual TOML files."""
        for toml_file in self.components_dir.glob("*.toml"):
            component_name = toml_file.stem
            self._component_settings[component_name] = Dynaconf(
                settings_files=[str(toml_file)],
                environments=True
            )

    def get_component_description(self, component_name: str) -> Dict[str, str]:
        """Get component description by name.

        Args:
            component_name (str): The name of the component.

        Returns:
            Dict[str, str]: A dictionary with component details.

        Raises:
            KeyError: If the component is not found in configurations.
        """
        if component_name not in self._component_settings:
            raise KeyError(f"Component {component_name} not found in configurations")
        
        settings = self._component_settings[component_name]
        return {
            "identification": settings.identification,
            "visual_representation": settings.visual_representation
        }

    @property
    def component_descriptions(self) -> Dict[str, Dict[str, str]]:
        """Get all component descriptions.

        Returns:
            Dict[str, Dict[str, str]]: A dictionary of all component descriptions.
        """
        return {
            name: self.get_component_description(name)
            for name in self._component_settings.keys()
        }


@lru_cache()
def get_component_config() -> ComponentConfig:
    """Get component config singleton.

    Returns:
        ComponentConfig: The singleton instance of ComponentConfig.
    """
    return ComponentConfig() 