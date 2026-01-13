"""
Game Engine Module

This is the heart of the game - the main game loop that:
1. Processes player input
2. Updates game state
3. Handles enemy AI
4. Renders the screen

GAME LOOP PATTERN:
while game_running:
    1. Get input from player
    2. Process player action
    3. Update enemies (AI)
    4. Render everything
    5. Check win/loss conditions
"""

import asyncio
import random
from typing import List, Optional
from blessed import Terminal

import config
from game.entities import (
    Actor, Entity, Item, 
    create_player, create_goblin, create_orc, create_health_potion
)
from game.map_gen import GameMap, generate_dungeon, get_random_empty_tile
from game.render import create_renderer, Renderer
from game.input_handler import create_input_handler, InputHandler, Action, InputResult


class GameState:
    """
    Holds all the game state
    
    This makes it easy to save/load games and reset state
    """
    def __init__(self):
        self.game_map: Optional[GameMap] = None
        self.player: Optional[Actor] = None
        self.entities: List[Entity] = []
        self.messages: List[str] = []
        self.turn: int = 0
        self.running: bool = True
        self.game_over: bool = False
        self.won: bool = False


class GameEngine:
    """
    The main game engine
    
    Manages the game loop and coordinates all subsystems
    """
    
    def __init__(self, stdin, stdout, username: str = "Player"):
        """
        Initialize the game engine
        
        Args:
            stdin: Input stream from SSH connection
            stdout: Output stream to SSH connection
            username: Player's name
        """
        self.stdin = stdin
        self.stdout = stdout
        self.username = username
        
        # We'll create the terminal in the run() method
        # because blessed.Terminal needs to be in an async context
        self.terminal: Optional[Terminal] = None
        self.renderer: Optional[Renderer] = None
        self.input_handler: Optional[InputHandler] = None
        
        # Game state
        self.state = GameState()
    
    async def read_input(self) -> Optional[InputResult]:
        """
        Read input from SSH stdin and map to actions
        
        Returns InputResult or None if timeout/no input
        """
        try:
            # Read one character from stdin
            char = await self.stdin.read(1)
            
            if not char:
                return None
            
            # Map common keys to actions
            key_map = {
                # Arrow keys (escape sequences)
                '\x1b[A': InputResult(Action.MOVE_UP, 0, -1),
                '\x1b[B': InputResult(Action.MOVE_DOWN, 0, 1),
                '\x1b[C': InputResult(Action.MOVE_RIGHT, 1, 0),
                '\x1b[D': InputResult(Action.MOVE_LEFT, -1, 0),
                
                # Vi keys
                'k': InputResult(Action.MOVE_UP, 0, -1),
                'j': InputResult(Action.MOVE_DOWN, 0, 1),
                'h': InputResult(Action.MOVE_LEFT, -1, 0),
                'l': InputResult(Action.MOVE_RIGHT, 1, 0),
                
                # WASD
                'w': InputResult(Action.MOVE_UP, 0, -1),
                's': InputResult(Action.MOVE_DOWN, 0, 1),
                'a': InputResult(Action.MOVE_LEFT, -1, 0),
                'd': InputResult(Action.MOVE_RIGHT, 1, 0),
                
                # Actions
                'i': InputResult(Action.PICKUP),
                'g': InputResult(Action.PICKUP),
                'e': InputResult(Action.USE_ITEM),
                '.': InputResult(Action.WAIT),
                ' ': InputResult(Action.WAIT),
                
                # System
                'q': InputResult(Action.QUIT),
                'Q': InputResult(Action.QUIT),
                'r': InputResult(Action.RESTART),
                'R': InputResult(Action.RESTART),
            }
            
            # Check for escape sequences (arrow keys)
            if char == '\x1b':
                # Read next two chars for arrow key
                seq = await self.stdin.read(2)
                full_seq = char + seq
                if full_seq in key_map:
                    return key_map[full_seq]
            
            # Regular character
            if char in key_map:
                return key_map[char]
            
            return InputResult(Action.UNKNOWN)
            
        except Exception as e:
            import logging
            logging.error(f"Input read error: {e}")
            return None
    
    def initialize_game(self):
        """Set up a new game"""
        # Generate the dungeon
        self.state.game_map, start_pos = generate_dungeon()
        
        # Create the player
        self.state.player = create_player(start_pos[0], start_pos[1], self.username)
        
        # Reset entities list
        self.state.entities = [self.state.player]
        
        # Spawn enemies
        num_enemies = random.randint(5, 10)
        for _ in range(num_enemies):
            x, y = get_random_empty_tile(self.state.game_map)
            
            # Don't spawn on player
            if (x, y) == (self.state.player.x, self.state.player.y):
                continue
            
            # Random enemy type
            if random.random() < 0.7:
                enemy = create_goblin(x, y)
            else:
                enemy = create_orc(x, y)
            
            self.state.entities.append(enemy)
        
        # Spawn items
        num_potions = random.randint(3, 6)
        for _ in range(num_potions):
            x, y = get_random_empty_tile(self.state.game_map)
            potion = create_health_potion(x, y)
            self.state.entities.append(potion)
        
        # Initialize game state
        self.state.messages = [
            f"Welcome, {self.username}!",
            "Descend into the dungeon and defeat all monsters!",
            "Press ? for help (not implemented yet)"
        ]
        self.state.turn = 0
        self.state.running = True
        self.state.game_over = False
        self.state.won = False
    
    def add_message(self, message: str):
        """Add a message to the message log"""
        self.state.messages.append(message)
    
    def get_entity_at(self, x: int, y: int) -> Optional[Entity]:
        """Get an entity at a specific position"""
        for entity in self.state.entities:
            if entity.x == x and entity.y == y:
                return entity
        return None
    
    def get_actor_at(self, x: int, y: int) -> Optional[Actor]:
        """Get an actor (entity that can fight) at a position"""
        entity = self.get_entity_at(x, y)
        if isinstance(entity, Actor):
            return entity
        return None
    
    def try_move_entity(self, entity: Entity, dx: int, dy: int) -> bool:
        """
        Try to move an entity
        
        Returns True if successful, False if blocked
        """
        new_x = entity.x + dx
        new_y = entity.y + dy
        
        # Check map bounds
        if not self.state.game_map.is_walkable(new_x, new_y):
            return False
        
        # Check for blocking entities
        target = self.get_entity_at(new_x, new_y)
        if target and target.blocks_movement:
            return False
        
        # Move is valid
        entity.move(dx, dy)
        return True
    
    def handle_player_action(self, action_result) -> bool:
        """
        Handle the player's action
        
        Returns True if the action took a turn, False otherwise
        """
        action = action_result.action
        
        # Quit
        if action == Action.QUIT:
            self.state.running = False
            return False
        
        # Restart
        if action == Action.RESTART:
            self.initialize_game()
            return False
        
        # Movement actions
        if action in [Action.MOVE_UP, Action.MOVE_DOWN, Action.MOVE_LEFT, 
                     Action.MOVE_RIGHT, Action.MOVE_UP_LEFT, Action.MOVE_UP_RIGHT,
                     Action.MOVE_DOWN_LEFT, Action.MOVE_DOWN_RIGHT]:
            
            new_x = self.state.player.x + action_result.dx
            new_y = self.state.player.y + action_result.dy
            
            # Check for enemies to attack
            target = self.get_actor_at(new_x, new_y)
            if target and target != self.state.player:
                # Attack!
                damage, killed = self.state.player.attack_target(target)
                self.add_message(
                    f"You attack {target.name} for {damage} damage!"
                )
                
                if killed:
                    self.add_message(f"You killed the {target.name}!")
                    self.state.entities.remove(target)
                    
                    # Check win condition (all enemies dead)
                    enemies = [e for e in self.state.entities 
                              if isinstance(e, Actor) and e != self.state.player]
                    if not enemies:
                        self.state.won = True
                        self.state.game_over = True
                        self.add_message("Victory! You defeated all enemies!")
                
                return True  # Combat takes a turn
            
            # Try to move
            if self.try_move_entity(self.state.player, action_result.dx, action_result.dy):
                return True  # Movement takes a turn
            else:
                self.add_message("You bump into a wall.")
                return False
        
        # Pickup item
        if action == Action.PICKUP:
            # Check for items at player position
            items_here = [e for e in self.state.entities 
                         if isinstance(e, Item) and 
                         e.x == self.state.player.x and 
                         e.y == self.state.player.y]
            
            if items_here:
                item = items_here[0]
                self.add_message(f"You pick up {item.name}.")
                # For now, items auto-use when picked up
                # In a full game, you'd add to inventory
                if isinstance(item, Item):
                    message = item.use(self.state.player)
                    if message:
                        self.add_message(message)
                self.state.entities.remove(item)
                return True
            else:
                self.add_message("There's nothing here to pick up.")
                return False
        
        # Wait/rest
        if action == Action.WAIT:
            self.add_message("You rest for a moment.")
            return True
        
        return False
    
    def run_enemy_turn(self):
        """
        Process all enemy actions
        
        Simple AI: Move towards player if in range, otherwise random movement
        """
        for entity in self.state.entities:
            # Skip non-actors and the player
            if not isinstance(entity, Actor) or entity == self.state.player:
                continue
            
            # Skip dead enemies
            if not entity.is_alive:
                continue
            
            # Calculate distance to player
            dx = self.state.player.x - entity.x
            dy = self.state.player.y - entity.y
            distance = max(abs(dx), abs(dy))  # Chebyshev distance
            
            # If close enough, move towards player
            if distance <= 10:
                # Normalize direction (get -1, 0, or 1 for each axis)
                move_x = 0 if dx == 0 else (1 if dx > 0 else -1)
                move_y = 0 if dy == 0 else (1 if dy > 0 else -1)
                
                # Check if we can attack the player
                new_x = entity.x + move_x
                new_y = entity.y + move_y
                
                if (new_x, new_y) == (self.state.player.x, self.state.player.y):
                    # Attack player!
                    damage, killed = entity.attack_target(self.state.player)
                    self.add_message(
                        f"{entity.name} attacks you for {damage} damage!"
                    )
                    
                    if killed:
                        self.add_message("You have been defeated!")
                        self.state.game_over = True
                        self.state.running = False
                else:
                    # Try to move towards player
                    if not self.try_move_entity(entity, move_x, move_y):
                        # If blocked, try alternative moves
                        if move_x != 0 and self.try_move_entity(entity, move_x, 0):
                            pass
                        elif move_y != 0 and self.try_move_entity(entity, 0, move_y):
                            pass
            else:
                # Too far from player, wander randomly (or stand still)
                if random.random() < 0.3:  # 30% chance to move
                    dx = random.choice([-1, 0, 1])
                    dy = random.choice([-1, 0, 1])
                    self.try_move_entity(entity, dx, dy)
    
    def render_game(self):
        """Render the current game state"""
        output = []
        
        # Clear screen
        output.append(self.renderer.clear())
        
        # Draw map
        output.append(self.renderer.draw_map(self.state.game_map))
        
        # Draw entities (items first, then actors, so actors appear on top)
        items = [e for e in self.state.entities if isinstance(e, Item)]
        actors = [e for e in self.state.entities if isinstance(e, Actor)]
        
        output.append(self.renderer.draw_entities(items))
        output.append(self.renderer.draw_entities(actors))
        
        # Draw UI
        output.append(self.renderer.draw_ui(self.state.player, self.state.messages, self.state.turn))
        
        # Write everything at once
        return ''.join(output)
    
    async def run(self):
        """
        Main game loop
        
        This is the entry point called by the SSH server
        """
        try:
            # Create blessed terminal
            # For SSH, we need special handling
            import sys
            self.terminal = Terminal(kind='xterm-256color', force_styling=True)
            
            # Initialize subsystems
            self.renderer = create_renderer(self.terminal)
            self.input_handler = create_input_handler(self.terminal)
            
            # Show welcome screen
            self.stdout.write(self.renderer.draw_welcome_screen())
            await self.stdout.drain()
            
            # Wait for player to press a key (read directly from stdin)
            await self.stdin.read(1)
            
            # Initialize the game
            self.initialize_game()
            
            # Main game loop
            while self.state.running:
                # Render current state
                self.stdout.write(self.render_game())
                await self.stdout.drain()
                
                # Check game over
                if self.state.game_over:
                    # Show game over screen
                    self.stdout.write(
                        self.renderer.draw_game_over(
                            self.state.player, 
                            self.state.turn, 
                            self.state.won
                        )
                    )
                    await self.stdout.drain()
                    
                    # Wait for input
                    action_result = await self.read_input()
                    
                    if action_result and action_result.action == Action.QUIT:
                        break
                    elif action_result and action_result.action == Action.RESTART:
                        self.initialize_game()
                        continue
                    else:
                        continue
                
                # Get player input - read directly from SSH stdin
                action_result = await self.read_input()
                
                if not action_result:
                    continue
                
                # Handle player action
                player_took_turn = self.handle_player_action(action_result)
                
                # If player took a turn, enemies take their turns
                if player_took_turn:
                    self.run_enemy_turn()
                    self.state.turn += 1
            
            # Clean exit message
            self.stdout.write(self.terminal.clear())
            self.stdout.write("Thanks for playing! Goodbye.\n\r")
            await self.stdout.drain()
            
        except Exception as e:
            # Log error
            import logging
            logging.error(f"Game error: {e}", exc_info=True)
            # Try to show error to player
            try:
                self.stdout.write(f"\n\rGame error: {e}\n\r")
                await self.stdout.drain()
            except:
                pass
