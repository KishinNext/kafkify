import os
from pathlib import Path
from typing import Any, Dict

import yaml
from pydash import objects

ROOT_DIR = Path(__file__).parent.parent.parent.absolute()


def load_configs() -> Dict[str, Any]:
    try:
        environment = os.getenv("ENV", "development")

        with open(
            ROOT_DIR / "config" / f"{environment.lower().strip()}.yaml",
            encoding="utf-8",
        ) as file:
            environment_config = yaml.safe_load(file)

        with open(ROOT_DIR / "config" / "default.yaml", encoding="utf-8") as file:
            default_config = yaml.safe_load(file)

        return {**environment_config, **default_config}

    except FileNotFoundError as e:
        raise FileNotFoundError("Config file not found") from e
    except OSError as e:
        raise OSError("Error reading config file") from e
    except yaml.YAMLError as e:
        raise yaml.YAMLError("Error parsing config file") from e
    except Exception as e:
        raise Exception("Unexpected error loading config") from e


class ConfigManager:
    """
    Singleton class to manage access to the configuration files
    """

    _instance = None
    configs = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.configs = load_configs()
        return cls._instance

    def get_property(self, property_name: str) -> Any:
        try:
            return objects.get(self.configs, property_name)
        except KeyError as e:
            raise KeyError(f"Property {property_name} not found in config") from e


config_manager = ConfigManager()
