"""
Open apps / files skill — macOS only.
Uses 'open' command which is native to macOS.
"""

import subprocess
import os


COMMON_APPS = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "safari": "Safari",
    "firefox": "Firefox",
    "spotify": "Spotify",
    "slack": "Slack",
    "terminal": "Terminal",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
    "code": "Visual Studio Code",
    "finder": "Finder",
    "calendar": "Calendar",
    "mail": "Mail",
    "notes": "Notes",
    "messages": "Messages",
    "facetime": "FaceTime",
    "zoom": "zoom.us",
    "discord": "Discord",
    "whatsapp": "WhatsApp",
    "xcode": "Xcode",
    "figma": "Figma",
    "notion": "Notion",
    "obsidian": "Obsidian",
    "vlc": "VLC",
    "calculator": "Calculator",
    "photos": "Photos",
    "music": "Music",
    "podcasts": "Podcasts",
    "maps": "Maps",
    "system preferences": "System Preferences",
    "system settings": "System Settings",
    "activity monitor": "Activity Monitor",
}


def open_app(name: str) -> str:
    """Open an application or file on macOS."""
    name_lower = name.lower().strip()

    app_name = COMMON_APPS.get(name_lower, name)

    if os.path.exists(name):
        try:
            subprocess.Popen(["open", name])
            return f"Opened file: {name}"
        except Exception as e:
            return f"Couldn't open file: {e}"

    try:
        result = subprocess.run(
            ["open", "-a", app_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return f"Opening {app_name}."
        else:
            result2 = subprocess.run(
                ["open", name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result2.returncode == 0:
                return f"Opened {name}."
            return f"Couldn't find '{name}'. Make sure the app is installed."
    except subprocess.TimeoutExpired:
        return f"Opening {app_name} (it may take a moment)."
    except Exception as e:
        return f"Failed to open {name}: {str(e)}"
