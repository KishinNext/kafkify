import json
from typing import Any, Union


def default_deserializer(value: Union[bytes, None]) -> Any:
    """
    Deserilize bytes to appropriate Python types. Handles JSON, strings, and binary data.
    """
    if value is None or value == b"":
        return None

    try:
        decoded_str = value.decode("utf-8")
    except UnicodeDecodeError:
        return value

    try:
        return json.loads(decoded_str)
    except json.JSONDecodeError:
        return decoded_str
