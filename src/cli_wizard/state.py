"""
This module initializes and configures the main components of the CLI wizard
tool by creating instances of key classes required for its operation.

The `ConfigSettings` class is used to manage configuration settings, while
`GeminiInterface` facilitates interactions with the Gemini system. These
instances form the core foundation of the CLI wizard's functionality.
"""

from cli_wizard.core.gemini_interface import GeminiInterface
from cli_wizard.core.config_settings import ConfigSettings


config_settings = ConfigSettings()
gemini_interface = GeminiInterface(config_settings)