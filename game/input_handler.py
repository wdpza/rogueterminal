"""
Input Handler Module

This module handles reading and interpreting keyboard input from the player.

INPUT IN TERMINALS:
- Regular keys send their ASCII character
- Special keys (arrows, etc.) send escape sequences
- We need to handle both synchronously and asynchronously

BLESSED INPUT:
- terminal.inkey() blocks waiting for a key
- terminal.inkey(timeout=0) returns immediately (non-blocking)
- Returns a keystroke object with properties like .code, .name, .is_sequence
"""

from blessed import Terminal
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class Action(Enum):
    """
    All possible player actions
    
    Using an Enum makes code clearer than using strings or magic numbers
    """
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UP_LEFT = auto()
    MOVE_UP_RIGHT = auto()
    MOVE_DOWN_LEFT = auto()
    MOVE_DOWN_RIGHT = auto()
    PICKUP = auto()
    USE_ITEM = auto()
    WAIT = auto()
    QUIT = auto()
    RESTART = auto()
    UNKNOWN = auto()


@dataclass
class InputResult:
    """
    Result of processing input
    
    action: The action the player wants to take
    dx, dy: Direction vector for movement (e.g., dx=1, dy=0 means move right)
    """
    action: Action
    dx: int = 0
    dy: int = 0


class InputHandler:
    """
    Handles keyboard input and converts it to game actions
    """
    
    def __init__(self, terminal: Terminal):
        self.terminal = terminal
        
        # Define key mappings
        # Vi keys (hjkl) are traditional in roguelikes
        self.key_map = {
            # Arrow keys
            'KEY_UP': InputResult(Action.MOVE_UP, 0, -1),
            'KEY_DOWN': InputResult(Action.MOVE_DOWN, 0, 1),
            'KEY_LEFT': InputResult(Action.MOVE_LEFT, -1, 0),
            'KEY_RIGHT': InputResult(Action.MOVE_RIGHT, 1, 0),
            
            # Vi keys (preferred by roguelike veterans)
            'k': InputResult(Action.MOVE_UP, 0, -1),
            'j': InputResult(Action.MOVE_DOWN, 0, 1),
            'h': InputResult(Action.MOVE_LEFT, -1, 0),
            'l': InputResult(Action.MOVE_RIGHT, 1, 0),
            
            # Diagonal movement (vi keys)
            'y': InputResult(Action.MOVE_UP_LEFT, -1, -1),
            'u': InputResult(Action.MOVE_UP_RIGHT, 1, -1),
            'b': InputResult(Action.MOVE_DOWN_LEFT, -1, 1),
            'n': InputResult(Action.MOVE_DOWN_RIGHT, 1, 1),
            
            # WASD (alternative, more familiar to modern gamers)
            'w': InputResult(Action.MOVE_UP, 0, -1),
            's': InputResult(Action.MOVE_DOWN, 0, 1),
            'a': InputResult(Action.MOVE_LEFT, -1, 0),
            'd': InputResult(Action.MOVE_RIGHT, 1, 0),
            
            # Actions
            'i': InputResult(Action.PICKUP),
            'g': InputResult(Action.PICKUP),  # Alternative for "get"
            'e': InputResult(Action.USE_ITEM),  # "eat" or "use"
            '.': InputResult(Action.WAIT),       # Wait/rest
            ' ': InputResult(Action.WAIT),       # Spacebar also waits
            
            # System
            'q': InputResult(Action.QUIT),
            'Q': InputResult(Action.QUIT),
            'r': InputResult(Action.RESTART),
            'R': InputResult(Action.RESTART),
        }
    
    def get_input(self, timeout: Optional[float] = None) -> Optional[InputResult]:
        """
        Get input from the player
        
        Args:
            timeout: How long to wait for input (None = wait forever, 0 = don't wait)
        
        Returns:
            InputResult if a key was pressed, None if timeout with no input
        """
        # Read a keystroke
        key = self.terminal.inkey(timeout=timeout)
        
        if not key:
            # No input (timeout expired)
            return None
        
        # Try to map the key to an action
        # First check if it's a named key (like KEY_UP)
        if key.name and key.name in self.key_map:
            return self.key_map[key.name]
        
        # Then check if it's a regular character
        if key in self.key_map:
            return self.key_map[key]
        
        # Unknown key
        return InputResult(Action.UNKNOWN)
    
    def wait_for_key(self) -> InputResult:
        """
        Wait indefinitely for a valid key press
        
        This is useful for "Press any key to continue" prompts
        """
        while True:
            result = self.get_input(timeout=None)
            if result:
                return result


def create_input_handler(terminal: Terminal) -> InputHandler:
    """Factory function to create an input handler"""
    return InputHandler(terminal)
