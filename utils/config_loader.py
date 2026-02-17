from typing import Any, Dict
from himl import ConfigProcessor


def load_config(env: str, region: str, print_data: bool = False) -> Dict[Any]:
    config_processor = ConfigProcessor()
    path = f"config/env={env}/region={region}"
    filters = ()  # can choose to output only specific keys
    exclude_keys = ()  # can choose to remove specific keys
    output_format = "yaml"  # yaml/json

    return config_processor.process(path=path, filters=filters, exclude_keys=exclude_keys,
                                    output_format=output_format, print_data=print_data)
