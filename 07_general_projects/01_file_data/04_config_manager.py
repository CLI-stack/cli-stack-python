"""
Project: Configuration File Manager
What it does: Reads, writes, and updates configuration files.
Applications use config files to store settings without hardcoding them.
Supports both JSON and INI formats — the two most common config formats.

JSON format:  {"key": "value"}  — good for nested settings
INI format:   [section] / key = value  — good for simple settings

Run: python 04_config_manager.py
"""

import json          # for reading/writing JSON config
import configparser  # built-in: reads/writes .ini and .cfg files
import os
from datetime import datetime


# ── Part 1: JSON Config Manager ───────────────────────────────────────────────

class JsonConfig:
    """Manages application settings stored in a JSON file."""

    def __init__(self, config_file="app_config.json"):
        self.config_file = config_file  # path to the config file
        self.data = {}                  # in-memory copy of the settings

        # Load existing config if the file exists
        if os.path.exists(self.config_file):
            self.load()
        else:
            # Set sensible default values for a new config
            self.data = {
                "app": {
                    "name":    "MyApp",
                    "version": "1.0.0",
                    "debug":   False
                },
                "database": {
                    "host":     "localhost",
                    "port":     5432,
                    "name":     "myapp_db",
                    "timeout":  30
                },
                "logging": {
                    "level":    "INFO",
                    "file":     "app.log",
                    "max_size": 10485760    # 10 MB in bytes
                }
            }
            self.save()  # write defaults to disk

    def load(self):
        """Read the JSON file and load settings into memory."""
        with open(self.config_file, "r") as f:
            self.data = json.load(f)  # JSON string → Python dict
        print(f"Config loaded from: {self.config_file}")

    def save(self):
        """Write current settings to the JSON file."""
        with open(self.config_file, "w") as f:
            json.dump(self.data, f, indent=2)  # indent=2 for human-readable format
        print(f"Config saved to: {self.config_file}")

    def get(self, section, key, default=None):
        """
        Get a setting value using section.key notation.
        Returns 'default' if the section or key doesn't exist.
        """
        return self.data.get(section, {}).get(key, default)

    def set(self, section, key, value):
        """Update a setting value. Creates the section if it doesn't exist."""
        if section not in self.data:
            self.data[section] = {}      # create new section
        self.data[section][key] = value  # update the setting
        self.save()                      # persist immediately
        print(f"Updated [{section}] {key} = {value}")

    def display(self):
        """Print all settings in a readable format."""
        print("\n  Current Configuration:")
        for section, settings in self.data.items():
            print(f"\n  [{section}]")
            for key, value in settings.items():
                print(f"    {key:<15} = {value}")


# ── Part 2: INI Config Manager ────────────────────────────────────────────────

class IniConfig:
    """Manages settings in an INI file (Windows-style config format)."""

    def __init__(self, config_file="app_settings.ini"):
        self.config_file = config_file

        # ConfigParser reads .ini files. interpolation=None disables
        # special character interpretation (% signs in values, etc.)
        self.parser = configparser.ConfigParser(interpolation=None)

        if os.path.exists(config_file):
            self.parser.read(config_file)   # load existing file
        else:
            self._create_defaults()

    def _create_defaults(self):
        """Set up default sections and values in the INI parser."""
        self.parser["General"] = {
            "app_name":   "MyApp",
            "version":    "1.0.0",
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }
        self.parser["Server"] = {
            "host":       "0.0.0.0",
            "port":       "8080",
            "workers":    "4",
            "debug":      "false"
        }
        self.save()

    def save(self):
        """Write the current parser state to the INI file."""
        with open(self.config_file, "w") as f:
            self.parser.write(f)  # write in INI format: [section]\nkey = value
        print(f"INI config saved to: {self.config_file}")

    def get(self, section, key, fallback=""):
        """Get a value from the INI file (always returns a string)."""
        return self.parser.get(section, key, fallback=fallback)

    def set(self, section, key, value):
        """Set a value in the INI file."""
        if not self.parser.has_section(section):
            self.parser.add_section(section)   # create section if missing
        self.parser.set(section, key, str(value))  # INI values must be strings
        self.save()

    def display(self):
        """Print all INI settings."""
        print("\n  INI Configuration:")
        for section in self.parser.sections():
            print(f"\n  [{section}]")
            for key, value in self.parser[section].items():
                print(f"    {key:<15} = {value}")


# ── Demo ──────────────────────────────────────────────────────────────────────
print("=== Configuration File Manager ===\n")

# ── JSON config demo ──────────────────────────────────────────────────────────
print("--- JSON Config ---")
json_cfg = JsonConfig("demo_app_config.json")
json_cfg.display()

# Update some settings
json_cfg.set("app", "debug", True)
json_cfg.set("database", "port", 5433)
json_cfg.set("app", "version", "1.1.0")

# Read back settings
db_host = json_cfg.get("database", "host")
debug   = json_cfg.get("app", "debug")
print(f"\n  Read back: DB host = {db_host}, Debug = {debug}")

# ── INI config demo ───────────────────────────────────────────────────────────
print("\n--- INI Config ---")
ini_cfg = IniConfig("demo_app_settings.ini")
ini_cfg.display()

# Update and read a setting
ini_cfg.set("Server", "port", "9090")
port = ini_cfg.get("Server", "port")
print(f"\n  New server port: {port}")

# ── Show file contents ────────────────────────────────────────────────────────
print("\n--- Raw JSON File Contents ---")
with open("demo_app_config.json") as f:
    print(f.read())

# Clean up demo files
os.remove("demo_app_config.json")
os.remove("demo_app_settings.ini")
print("Demo config files cleaned up.")
