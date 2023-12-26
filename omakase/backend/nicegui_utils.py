"""Shared utils for NiceGUI"""
from dataclasses import dataclass
from typing import Callable


@dataclass
class TabConf:
    """Configure a NiceGUI tab"""

    name: str
    label: str
    icon: str
    content_generator: Callable
