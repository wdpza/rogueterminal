"""
Configuration file for the Roguelike SSH Game

This file centralizes all configuration settings for the game server.
By keeping config in one place, we make it easy to adjust settings
without hunting through code.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
# This allows you to override these settings locally without changing code
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).parent.absolute()

# ============================================================================
# SSH SERVER SETTINGS
# ============================================================================

# Port the SSH server listens on
# Port 22 is standard SSH, but requires root privileges
# Port 2222 is common for custom SSH services
SSH_PORT = int(os.getenv('SSH_PORT', '2222'))

# Host to bind to - '0.0.0.0' means accept connections from any network interface
# Use '127.0.0.1' for localhost-only testing
SSH_HOST = os.getenv('SSH_HOST', '0.0.0.0')

# SSH server authentication settings
# For simplicity, we'll use a shared password. In production, consider SSH keys.
SERVER_PASSWORD = os.getenv('SERVER_PASSWORD', 'roguelike')  # Change this!

# Path to SSH host keys
# The server needs cryptographic keys to establish secure connections
SSH_KEYS_DIR = BASE_DIR / 'ssh_keys'
SSH_HOST_KEY = SSH_KEYS_DIR / 'ssh_host_key'

# ============================================================================
# GAME SETTINGS
# ============================================================================

# Map dimensions
MAP_WIDTH = 80  # Width of the dungeon in tiles
MAP_HEIGHT = 45  # Height of the dungeon in tiles

# How many rooms to try to generate in each dungeon level
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

# Starting stats for the player character
PLAYER_STARTING_HP = 30
PLAYER_STARTING_ATTACK = 5
PLAYER_STARTING_DEFENSE = 2

# Game tick rate (how often the game updates per second)
# Lower = slower game, higher = faster game
GAME_TICK_RATE = 30  # Times per second

# ============================================================================
# DATA STORAGE
# ============================================================================

# Directory where player save files are stored
SAVES_DIR = BASE_DIR / 'data' / 'saves'

# Ensure directories exist
SSH_KEYS_DIR.mkdir(parents=True, exist_ok=True)
SAVES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# TERMINAL SETTINGS
# ============================================================================

# Minimum terminal size required to play
MIN_TERMINAL_WIDTH = 80
MIN_TERMINAL_HEIGHT = 50

# Colors (using terminal color codes)
# These work with blessed's color system
COLOR_PLAYER = 'white'
COLOR_ENEMY = 'red'
COLOR_ITEM = 'yellow'
COLOR_WALL = 'gray'
COLOR_FLOOR = 'black'
COLOR_FOV = 'bright_yellow'  # Field of view tint

# ============================================================================
# DEBUG SETTINGS
# ============================================================================

# Enable debug mode for extra logging
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Log file location
LOG_FILE = BASE_DIR / 'game.log'
