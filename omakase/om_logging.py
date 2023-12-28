"""
Set up the logger
"""
import os

from loguru import logger

from omakase.io import get_conf_toml, get_log_path

# Getting the logger configuration for the app scope
logging_conf_toml = get_conf_toml("logging.toml")
app_scope = logging_conf_toml["app_scope"]
logging_conf = logging_conf_toml[app_scope]

# Updating the log path
logging_conf["sink"] = os.path.join(get_log_path(), logging_conf["sink"])

# Configuring the logger
logger.add(**logging_conf)
