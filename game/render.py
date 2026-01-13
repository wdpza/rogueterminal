"""
Rendering Module

This module handles drawing the game to the terminal using the 'blessed' library.

BLESSED BASICS:
- Terminal object gives us control over the terminal
- terminal.move(y, x) moves cursor to position
- terminal.color('text') returns colored text
- terminal.clear() clears the screen
- terminal.hidden_cursor() hides the blinking cursor

The terminal uses a coordinate system:
- (0, 0) is top-left corner
- X increases going right
- Y increases going down
"""

from typing import List, TYPE_CHECKING
from blessed import Terminal
import config

# TYPE_CHECKING is True only during type checking, not at runtime
# This prevents circular imports
if TYPE_CHECKING:
    from game.entities import Entity, Actor
    from game.map_gen import GameMap


class Renderer:
    """
    Handles all drawing to the terminal
    """
    
    def __init__(self, terminal: Terminal):
        """
        Initialize the renderer
        
        Args:
            terminal: A blessed Terminal instance
        """
        self.terminal = terminal
        self.width = terminal.width
        self.height = terminal.height
    
    def clear(self):
        """Clear the entire screen and hide cursor"""
        return self.terminal.clear() + self.terminal.hide_cursor
    
    def draw_at(self, x: int, y: int, char: str, color: str = 'white'):
        """
        Draw a character at a specific position with color
        
        Returns the string to print (doesn't print it yet)
        This allows us to batch all drawing into one write operation
        """
        # Get the color function from terminal
        colored = getattr(self.terminal, color, self.terminal.white)
        
        # Move cursor and return the colored character
        return self.terminal.move_xy(x, y) + colored(char)
    
    def draw_string_at(self, x: int, y: int, text: str, color: str = 'white'):
        """Draw a string starting at position"""
        colored = getattr(self.terminal, color, self.terminal.white)
        return self.terminal.move_xy(x, y) + colored(text)
    
    def draw_map(self, game_map: 'GameMap', viewport_x: int = 0, viewport_y: int = 0):
        """
        Draw the map tiles
        
        viewport_x, viewport_y: Top-left corner of what to display
        This allows scrolling large maps
        """
        output = []
        
        # Calculate how much of the map we can show
        # Leave room for UI at bottom
        map_view_height = self.height - 5  # Reserve 5 lines for stats/messages
        map_view_width = self.width
        
        for screen_y in range(map_view_height):
            for screen_x in range(map_view_width):
                # Convert screen coordinates to map coordinates
                map_x = screen_x + viewport_x
                map_y = screen_y + viewport_y
                
                # Check if this map tile exists
                if not game_map.is_in_bounds(map_x, map_y):
                    continue
                
                # Draw wall or floor
                if game_map.is_walkable(map_x, map_y):
                    output.append(self.draw_at(screen_x, screen_y, '.', config.COLOR_FLOOR))
                else:
                    output.append(self.draw_at(screen_x, screen_y, '#', config.COLOR_WALL))
        
        return ''.join(output)
    
    def draw_entity(self, entity: 'Entity', viewport_x: int = 0, viewport_y: int = 0):
        """
        Draw an entity (player, monster, item)
        
        Converts entity's map position to screen position based on viewport
        """
        screen_x = entity.x - viewport_x
        screen_y = entity.y - viewport_y
        
        # Only draw if on screen
        map_view_height = self.height - 5
        if 0 <= screen_x < self.width and 0 <= screen_y < map_view_height:
            return self.draw_at(screen_x, screen_y, entity.char, entity.color)
        return ''
    
    def draw_entities(self, entities: List['Entity'], viewport_x: int = 0, viewport_y: int = 0):
        """Draw all entities"""
        output = []
        for entity in entities:
            output.append(self.draw_entity(entity, viewport_x, viewport_y))
        return ''.join(output)
    
    def draw_ui(self, player: 'Actor', messages: List[str], turn: int):
        """
        Draw the UI panel at the bottom of the screen
        
        Shows:
        - Player HP
        - Recent messages
        - Turn counter
        """
        output = []
        
        # UI starts after the map area
        ui_y = self.height - 5
        
        # Draw a separator line
        output.append(self.draw_string_at(0, ui_y, '─' * self.width, 'gray'))
        
        # Draw player stats
        hp_text = f"HP: {player.hp}/{player.max_hp}"
        hp_color = 'green' if player.hp > player.max_hp // 2 else 'yellow'
        if player.hp < player.max_hp // 4:
            hp_color = 'red'
        
        output.append(self.draw_string_at(2, ui_y + 1, hp_text, hp_color))
        
        # Draw turn counter
        turn_text = f"Turn: {turn}"
        output.append(self.draw_string_at(20, ui_y + 1, turn_text, 'cyan'))
        
        # Draw recent messages (last 3)
        message_start_y = ui_y + 2
        recent_messages = messages[-3:] if len(messages) > 3 else messages
        
        # Draw up to 3 message lines (clear with spaces if fewer messages)
        for i in range(3):
            if i < len(recent_messages):
                msg = recent_messages[i]
                # Truncate message if too long
                if len(msg) > self.width - 4:
                    msg = msg[:self.width - 7] + '...'
                # Pad with spaces to clear old text
                msg = msg.ljust(self.width - 4)
            else:
                # Empty line - clear it with spaces
                msg = ' ' * (self.width - 4)
            
            output.append(self.draw_string_at(2, message_start_y + i, msg, 'white'))
        
        return ''.join(output)
    
    def draw_welcome_screen(self):
        """Draw the initial welcome screen"""
        output = [self.clear()]
        
        title = "🗡️  TERMINAL ROGUELIKE  🗡️"
        subtitle = "A dungeon crawler you can play over SSH"
        
        center_y = self.height // 2
        center_x = self.width // 2
        
        # Center the title
        output.append(self.draw_string_at(
            center_x - len(title) // 2,
            center_y - 3,
            title,
            'bright_yellow'
        ))
        
        output.append(self.draw_string_at(
            center_x - len(subtitle) // 2,
            center_y - 1,
            subtitle,
            'white'
        ))
        
        instructions = [
            "",
            "Controls:",
            "  Arrow keys or hjkl - Move",
            "  i - Pick up item",
            "  u - Use item",
            "  q - Quit",
            "",
            "Press any key to start..."
        ]
        
        for i, line in enumerate(instructions):
            output.append(self.draw_string_at(
                center_x - len(line) // 2,
                center_y + 2 + i,
                line,
                'cyan'
            ))
        
        return ''.join(output)
    
    def draw_game_over(self, player: 'Actor', turn: int, won: bool = False):
        """Draw the game over screen"""
        output = [self.clear()]
        
        center_y = self.height // 2
        center_x = self.width // 2
        
        if won:
            title = "⭐ VICTORY! ⭐"
            color = 'bright_green'
        else:
            title = "💀 GAME OVER 💀"
            color = 'bright_red'
        
        output.append(self.draw_string_at(
            center_x - len(title) // 2,
            center_y - 2,
            title,
            color
        ))
        
        stats = f"You survived {turn} turns"
        output.append(self.draw_string_at(
            center_x - len(stats) // 2,
            center_y,
            stats,
            'white'
        ))
        
        prompt = "Press Q to quit or R to restart..."
        output.append(self.draw_string_at(
            center_x - len(prompt) // 2,
            center_y + 2,
            prompt,
            'cyan'
        ))
        
        return ''.join(output)


def create_renderer(terminal: Terminal) -> Renderer:
    """Factory function to create a renderer"""
    return Renderer(terminal)
