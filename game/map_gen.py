"""
Map Generation Module

This module handles procedural generation of dungeon maps using the
"rooms and corridors" algorithm, which is common in roguelikes.

HOW IT WORKS:
1. Start with a solid map (all walls)
2. Try to place random rectangular rooms
3. Connect rooms with corridors (tunnels)
4. Mark tiles as walkable or walls
"""

import random
from dataclasses import dataclass
from typing import List, Tuple
import config


@dataclass
class Rect:
    """
    Represents a rectangular room
    
    x1, y1: Top-left corner
    x2, y2: Bottom-right corner
    """
    x1: int
    y1: int
    x2: int
    y2: int
    
    @property
    def center(self) -> Tuple[int, int]:
        """Get the center point of the room"""
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return center_x, center_y
    
    def intersects(self, other: 'Rect') -> bool:
        """Check if this room overlaps with another room"""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


class GameMap:
    """
    The dungeon map
    
    Stores which tiles are walkable and which are walls.
    Uses a 2D list where True = walkable, False = wall
    """
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Initialize the map with all walls (False)
        # This creates a 2D list: [[False, False, ...], [False, False, ...], ...]
        self.tiles = [[False for x in range(width)] for y in range(height)]
        
        # Keep track of rooms for later use
        self.rooms: List[Rect] = []
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a tile can be walked on"""
        # First check if coordinates are in bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        return self.tiles[y][x]
    
    def is_in_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within map boundaries"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def carve_room(self, room: Rect):
        """
        Carve out a room by making all tiles within it walkable
        
        We add +1 to ranges to make them inclusive
        """
        for y in range(room.y1 + 1, room.y2):
            for x in range(room.x1 + 1, room.x2):
                self.tiles[y][x] = True
    
    def carve_horizontal_tunnel(self, x1: int, x2: int, y: int):
        """
        Carve a horizontal corridor between two points
        
        min/max ensure we handle tunnels in either direction
        """
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if self.is_in_bounds(x, y):
                self.tiles[y][x] = True
    
    def carve_vertical_tunnel(self, y1: int, y2: int, x: int):
        """Carve a vertical corridor between two points"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if self.is_in_bounds(x, y):
                self.tiles[y][x] = True
    
    def carve_tunnel_between_rooms(self, room1: Rect, room2: Rect):
        """
        Connect two rooms with an L-shaped tunnel
        
        Randomly choose to go horizontal-then-vertical or vertical-then-horizontal
        This creates more natural-looking dungeons
        """
        x1, y1 = room1.center
        x2, y2 = room2.center
        
        # Randomly choose the order
        if random.random() < 0.5:
            # Horizontal first, then vertical
            self.carve_horizontal_tunnel(x1, x2, y1)
            self.carve_vertical_tunnel(y1, y2, x2)
        else:
            # Vertical first, then horizontal
            self.carve_vertical_tunnel(y1, y2, x1)
            self.carve_horizontal_tunnel(x1, x2, y2)


def generate_dungeon(
    width: int = config.MAP_WIDTH,
    height: int = config.MAP_HEIGHT,
    max_rooms: int = config.MAX_ROOMS,
    room_min_size: int = config.ROOM_MIN_SIZE,
    room_max_size: int = config.ROOM_MAX_SIZE
) -> Tuple[GameMap, Tuple[int, int]]:
    """
    Generate a dungeon map using the rooms-and-corridors algorithm
    
    Returns:
        game_map: The generated map
        start_position: (x, y) coordinates for the player to start
    """
    
    # Create an empty map (all walls)
    game_map = GameMap(width, height)
    
    # Try to place rooms
    for _ in range(max_rooms):
        # Random room dimensions
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)
        
        # Random position within map bounds
        # Subtract room size to ensure room fits on map
        x = random.randint(0, width - room_width - 1)
        y = random.randint(0, height - room_height - 1)
        
        # Create the room
        new_room = Rect(x, y, x + room_width, y + room_height)
        
        # Check if this room overlaps with any existing rooms
        if any(new_room.intersects(other_room) for other_room in game_map.rooms):
            # Overlap detected, skip this room
            continue
        
        # No overlap, so this room is valid
        game_map.carve_room(new_room)
        
        # Connect to the previous room with a tunnel
        if len(game_map.rooms) > 0:
            # Connect to the most recent room
            game_map.carve_tunnel_between_rooms(game_map.rooms[-1], new_room)
        
        # Add to our list of rooms
        game_map.rooms.append(new_room)
    
    # Player starts in the center of the first room
    if game_map.rooms:
        start_x, start_y = game_map.rooms[0].center
    else:
        # Fallback if no rooms were generated (shouldn't happen)
        start_x, start_y = width // 2, height // 2
        game_map.tiles[start_y][start_x] = True
    
    return game_map, (start_x, start_y)


def get_random_empty_tile(game_map: GameMap) -> Tuple[int, int]:
    """
    Find a random walkable tile on the map
    
    Useful for spawning enemies and items
    """
    while True:
        x = random.randint(0, game_map.width - 1)
        y = random.randint(0, game_map.height - 1)
        
        if game_map.is_walkable(x, y):
            return x, y
