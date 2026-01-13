"""
Game Entities Module

This module defines all the "things" in the game world:
- The player character
- Monsters/enemies
- Items (potions, weapons, etc.)

In roguelikes, entities have properties like position, HP, attack power, etc.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Entity:
    """
    Base class for all game entities
    
    Using @dataclass makes Python auto-generate __init__, __repr__, etc.
    This is a cleaner way to create simple data-holding classes.
    
    Every entity has:
    - x, y: Position on the map
    - char: Character to display (like '@' for player, 'g' for goblin)
    - color: Terminal color for rendering
    - name: What to call this entity
    - blocks_movement: Does this entity block other entities?
    """
    x: int
    y: int
    char: str
    color: str
    name: str
    blocks_movement: bool
    
    def move(self, dx: int, dy: int):
        """Move the entity by dx, dy"""
        self.x += dx
        self.y += dy


@dataclass
class Actor(Entity):
    """
    An Actor is an Entity that can fight and has HP
    
    This includes the player and all monsters.
    """
    hp: int
    max_hp: int
    attack: int
    defense: int
    
    @property
    def is_alive(self) -> bool:
        """Check if this actor is still alive"""
        return self.hp > 0
    
    def take_damage(self, amount: int) -> int:
        """
        Take damage, reducing HP
        
        Returns the actual damage taken (after defense)
        """
        # Defense reduces damage
        actual_damage = max(0, amount - self.defense)
        self.hp -= actual_damage
        
        # Don't let HP go below 0
        if self.hp < 0:
            self.hp = 0
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """
        Restore HP
        
        Returns the actual amount healed (can't exceed max HP)
        """
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def attack_target(self, target: 'Actor') -> tuple[int, bool]:
        """
        Attack another actor
        
        Returns (damage_dealt, killed_target)
        """
        damage = self.attack
        damage_dealt = target.take_damage(damage)
        killed = not target.is_alive
        
        return damage_dealt, killed


@dataclass
class Item(Entity):
    """
    Base class for items (potions, weapons, etc.)
    
    Items don't block movement - you can walk through them to pick them up.
    """
    blocks_movement: bool = False
    
    def use(self, user: Actor) -> Optional[str]:
        """
        Use this item on an actor
        
        Returns a message describing what happened, or None if can't use
        Should be overridden by subclasses
        """
        return None


@dataclass
class HealthPotion(Item):
    """
    A health potion that restores HP
    """
    healing_amount: int = 20
    
    def use(self, user: Actor) -> Optional[str]:
        """Use the potion to heal"""
        if user.hp == user.max_hp:
            return f"{user.name} is already at full health!"
        
        healed = user.heal(self.healing_amount)
        return f"{user.name} heals {healed} HP!"


# Factory functions to create common entities
# These ensure consistency - all goblins have the same stats, etc.

def create_player(x: int, y: int, name: str = "Player") -> Actor:
    """Create the player character"""
    import config
    return Actor(
        x=x,
        y=y,
        char='@',
        color=config.COLOR_PLAYER,
        name=name,
        blocks_movement=True,
        hp=config.PLAYER_STARTING_HP,
        max_hp=config.PLAYER_STARTING_HP,
        attack=config.PLAYER_STARTING_ATTACK,
        defense=config.PLAYER_STARTING_DEFENSE
    )


def create_goblin(x: int, y: int) -> Actor:
    """Create a goblin enemy"""
    import config
    return Actor(
        x=x,
        y=y,
        char='g',
        color=config.COLOR_ENEMY,
        name='Goblin',
        blocks_movement=True,
        hp=10,
        max_hp=10,
        attack=3,
        defense=0
    )


def create_orc(x: int, y: int) -> Actor:
    """Create an orc enemy (tougher than goblin)"""
    import config
    return Actor(
        x=x,
        y=y,
        char='O',
        color=config.COLOR_ENEMY,
        name='Orc',
        blocks_movement=True,
        hp=16,
        max_hp=16,
        attack=4,
        defense=1
    )


def create_health_potion(x: int, y: int) -> HealthPotion:
    """Create a health potion"""
    import config
    return HealthPotion(
        x=x,
        y=y,
        char='!',
        color=config.COLOR_ITEM,
        name='Health Potion',
        blocks_movement=False,
        healing_amount=20
    )
