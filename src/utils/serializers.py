import json
from typing import Any


def default_serializer(value: Any) -> bytes:
    """
    Serialize a value to bytes using appropriate encoding based on type.
    Converts various Python types to their byte representation. Handles dictionaries
    (JSON), strings, bytes, None, numbers, and other types by converting them to
    strings and encoding as UTF-8.

    Args:
        value: The value to be serialized. Can be a dict, str, bytes, int, float, None, or any other type.

    Returns:
        The serialized value as bytes. Empty bytes (b"") for None values.
    """
    if isinstance(value, dict):
        return json.dumps(value).encode("utf-8")
    elif isinstance(value, str):
        return value.encode("utf-8")
    elif isinstance(value, bytes):
        return value
    elif value is None:
        return b""
    elif isinstance(value, (int, float)):
        return str(value).encode("utf-8")
    return str(value).encode("utf-8")
