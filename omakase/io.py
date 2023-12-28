import os
import tomllib

import omakase


def get_lib_path() -> str:
    """Path to current library"""
    return os.path.join(
        os.path.dirname(omakase.__file__),
        "..",
    )


def get_config_path() -> str:
    """Path to conf folder"""
    return os.path.join(
        get_lib_path(),
        "conf",
    )


def get_conf_toml(filename) -> dict:
    """Get conf/`filename` (toml files)"""
    filepath = os.path.join(get_config_path(), filename)
    with open(filepath, "rb") as f:
        conf = tomllib.load(f)
    return conf


def get_log_path() -> str:
    """Path to log folder"""
    return os.path.join(
        get_lib_path(),
        "logs",
    )
