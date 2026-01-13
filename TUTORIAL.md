# 🎓 Tutorial: Understanding Your SSH Roguelike

This tutorial walks you through the entire codebase, explaining how everything works together. Perfect for learning!

## 📚 Table of Contents

1. [The Big Picture](#the-big-picture)
2. [Starting Simple: Entities](#starting-simple-entities)
3. [Building the World: Map Generation](#building-the-world-map-generation)
4. [Seeing is Believing: Rendering](#seeing-is-believing-rendering)
5. [Player Control: Input Handling](#player-control-input-handling)
6. [The Heart: Game Engine](#the-heart-game-engine)
7. [The Gateway: SSH Server](#the-gateway-ssh-server)
8. [Configuration](#configuration)
9. [Next Steps](#next-steps)

---

## The Big Picture

Your roguelike has a **layered architecture**:

```
┌─────────────────────────────────────┐
│  Player's Terminal (anywhere)       │
│  $ ssh -p 2222 player@your-server   │
└──────────────┬──────────────────────┘
               │ SSH Protocol
┌──────────────▼──────────────────────┐
│  server.py (SSH Server)             │
│  - Accepts connections              │
│  - Authenticates players            │
│  - Spawns game instances            │
└──────────────┬──────────────────────┘
               │ stdin/stdout
┌──────────────▼──────────────────────┐
│  game/engine.py (Game Loop)         │
│  Input → Update → Render → Repeat   │
└─┬────────┬────────┬────────┬────────┘
  │        │        │        │
  ▼        ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Entity│ │Map   │ │Render│ │Input │
│System│ │Gen   │ │      │ │      │
└──────┘ └──────┘ └──────┘ └──────┘
```

---

## Starting Simple: Entities

**File: `game/entities.py`**

### What Are Entities?

Everything in the game is an entity: the player, monsters, items. They all have:
- Position (x, y coordinates)
- Appearance (character and color)
- Name

### The Class Hierarchy

```python
Entity                    # Base class
├── Actor                 # Things that fight (have HP, can attack)
│   ├── Player           
│   ├── Goblin           
│   └── Orc              
└── Item                  # Things that can be used
    └── HealthPotion     
```

### Key Concept: Dataclasses

```python
@dataclass
class Entity:
    x: int
    y: int
    char: str
    color: str
    name: str
```

The `@dataclass` decorator automatically creates:
- `__init__()` method
- `__repr__()` for printing
- `__eq__()` for comparison

Without it, you'd write:
```python
class Entity:
    def __init__(self, x, y, char, color, name):
        self.x = x
        self.y = y
        # ... etc
```

### Combat System

```python
def attack_target(self, target: 'Actor') -> tuple[int, bool]:
    damage = self.attack
    damage_dealt = target.take_damage(damage)
    killed = not target.is_alive
    return damage_dealt, killed
```

Simple formula: Attacker's attack power - Defender's defense = Damage

### Try It!

Add a new enemy type:

```python
def create_troll(x: int, y: int) -> Actor:
    return Actor(
        x=x, y=y,
        char='T',
        color='bright_red',
        name='Troll',
        hp=30,
        max_hp=30,
        attack=8,
        defense=3
    )
```

---

## Building the World: Map Generation

**File: `game/map_gen.py`**

### The Algorithm: Rooms and Corridors

This is the classic roguelike dungeon generation method:

**Step 1: Start with solid rock**
```
######################
######################
######################
```

**Step 2: Carve random rooms**
```
######################
###........###########
###........###########
###........###########
######################
```

**Step 3: Connect rooms with tunnels**
```
######################
###........#####......
###........#####......
###........#####......
###........#####......
```

### The Code Flow

```python
# 1. Create empty map (all walls)
game_map = GameMap(width, height)

# 2. Try to place rooms
for _ in range(max_rooms):
    new_room = Rect(x, y, width, height)
    
    # 3. Check overlap
    if any(new_room.intersects(other) for other in game_map.rooms):
        continue  # Skip this room
    
    # 4. Carve it out
    game_map.carve_room(new_room)
    
    # 5. Connect to previous room
    if len(game_map.rooms) > 0:
        game_map.carve_tunnel_between_rooms(game_map.rooms[-1], new_room)
    
    game_map.rooms.append(new_room)
```

### Why L-shaped Tunnels?

```python
if random.random() < 0.5:
    # Horizontal then vertical
    self.carve_horizontal_tunnel(x1, x2, y1)
    self.carve_vertical_tunnel(y1, y2, x2)
else:
    # Vertical then horizontal
    self.carve_vertical_tunnel(y1, y2, x1)
    self.carve_horizontal_tunnel(x1, x2, y2)
```

This creates more natural-looking dungeons than straight diagonal lines.

### Try It!

Create circular rooms:

```python
def carve_circular_room(self, center_x, center_y, radius):
    for y in range(center_y - radius, center_y + radius):
        for x in range(center_x - radius, center_x + radius):
            # Distance formula: √((x2-x1)² + (y2-y1)²)
            dist = ((x - center_x)**2 + (y - center_y)**2)**0.5
            if dist <= radius:
                self.tiles[y][x] = True
```

---

## Seeing is Believing: Rendering

**File: `game/render.py`**

### How Terminal Graphics Work

Terminals use **ANSI escape codes** to:
- Move the cursor: `\033[10;5H` (row 10, col 5)
- Set colors: `\033[31m` (red text)
- Clear screen: `\033[2J`

**Blessed** abstracts this:
```python
# Instead of: print("\033[10;5H@")
terminal.move_xy(5, 10) + '@'
```

### The Rendering Pipeline

```python
def render_game(self):
    output = []
    
    # 1. Clear screen
    output.append(self.renderer.clear())
    
    # 2. Draw map (floor/walls)
    output.append(self.renderer.draw_map(self.state.game_map))
    
    # 3. Draw entities (items, then actors)
    output.append(self.renderer.draw_entities(items))
    output.append(self.renderer.draw_entities(actors))
    
    # 4. Draw UI (HP, messages)
    output.append(self.renderer.draw_ui(...))
    
    # 5. Write everything at once (fast!)
    return ''.join(output)
```

### Why Build a String First?

Writing to stdout is **slow**. If you write character-by-character:
```python
# SLOW - 100 separate writes
for char in map:
    stdout.write(char)
```

Instead, build one big string:
```python
# FAST - 1 write
stdout.write(''.join(all_output))
```

### Coordinate Systems

Terminal coordinates are **(x, y)** where:
- (0, 0) is top-left
- X increases going right →
- Y increases going down ↓

```
(0,0) (1,0) (2,0) ...
(0,1) (1,1) (2,1) ...
(0,2) (1,2) (2,2) ...
  ...
```

### Try It!

Add a minimap in the corner:

```python
def draw_minimap(self, game_map, player, x, y, size):
    """Draw a small overview map"""
    for my in range(size):
        for mx in range(size):
            # Scale coordinates
            map_x = (mx * game_map.width) // size
            map_y = (my * game_map.height) // size
            
            # Draw simplified tile
            if (map_x, map_y) == (player.x, player.y):
                char = '@'
            elif game_map.is_walkable(map_x, map_y):
                char = '.'
            else:
                char = '#'
            
            output.append(self.draw_at(x + mx, y + my, char))
```

---

## Player Control: Input Handling

**File: `game/input_handler.py`**

### How Keyboard Input Works

When you press a key, it sends:
- **Regular keys**: Their ASCII character ('a', 'w', etc.)
- **Special keys**: Escape sequences (Arrow keys, Function keys)

### The Input Handler's Job

```python
# Map keys to actions
self.key_map = {
    'KEY_UP': InputResult(Action.MOVE_UP, 0, -1),
    'k': InputResult(Action.MOVE_UP, 0, -1),
    'w': InputResult(Action.MOVE_UP, 0, -1),
}
```

This allows multiple keys to do the same thing!

### Why Use Enums?

```python
class Action(Enum):
    MOVE_UP = auto()
    QUIT = auto()
```

Enums are better than strings:
```python
# With strings - typos cause bugs!
if action == "MOVE_UP":  # Works
if action == "MOVE_UO":  # Silently fails!

# With enums - typos are caught immediately
if action == Action.MOVE_UP:  # Works
if action == Action.MOVE_UO:  # Error! No such attribute
```

### InputResult

```python
@dataclass
class InputResult:
    action: Action
    dx: int = 0
    dy: int = 0
```

This bundles the action with its parameters. Moving up is `Action.MOVE_UP` plus `dx=0, dy=-1`.

### Try It!

Add a "look" mode:

```python
Action.LOOK = auto()

# In key_map:
'x': InputResult(Action.LOOK),

# In game engine:
if action == Action.LOOK:
    self.add_message("Look mode - arrow keys to examine")
    # ... implement look logic
```

---

## The Heart: Game Engine

**File: `game/engine.py`**

### The Game Loop

All games use this pattern:

```python
while game_running:
    # 1. Get input
    action = get_player_input()
    
    # 2. Update game state
    handle_action(action)
    update_enemies()
    check_win_lose()
    
    # 3. Render
    draw_everything()
```

### Turn-Based Logic

```python
# Player takes action
player_took_turn = self.handle_player_action(action_result)

# If player took a turn, enemies get to act
if player_took_turn:
    self.run_enemy_turn()
    self.state.turn += 1
```

Not all actions take a turn:
- Moving: ✅ Takes a turn
- Attacking: ✅ Takes a turn
- Quitting: ❌ No turn
- Bumping into wall: ❌ No turn

### Simple AI

```python
def run_enemy_turn(self):
    for enemy in enemies:
        # Calculate distance to player
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        distance = max(abs(dx), abs(dy))
        
        # If close, chase player
        if distance <= 10:
            # Normalize direction (-1, 0, or 1)
            move_x = 0 if dx == 0 else (1 if dx > 0 else -1)
            move_y = 0 if dy == 0 else (1 if dy > 0 else -1)
            
            # Try to move towards player
            self.try_move_entity(enemy, move_x, move_y)
```

### Game States

```python
class GameState:
    running: bool = True      # Game loop active?
    game_over: bool = False   # Player dead/won?
    won: bool = False         # Victory?
```

These control the flow:
```python
while self.state.running:
    if self.state.game_over:
        show_game_over_screen()
    else:
        play_normal_game()
```

### Try It!

Add a hunger system:

```python
# In GameState.__init__:
self.hunger = 0
self.max_hunger = 100

# In run():
if player_took_turn:
    self.state.hunger += 1
    if self.state.hunger >= self.state.max_hunger:
        self.state.player.take_damage(1)
        self.add_message("You're starving!")
```

---

## The Gateway: SSH Server

**File: `server.py`**

### How SSH Servers Work

1. **Server listens on a port** (like 2222)
2. **Client connects** (you run `ssh`)
3. **Cryptographic handshake** (establishing secure channel)
4. **Authentication** (password or key)
5. **Channel opened** (for terminal I/O)
6. **Data flows** (encrypted)

### AsyncSSH Structure

```python
# Define how to handle connections
class RoguelikeSSHServer(asyncssh.SSHServer):
    def validate_password(self, username, password):
        return password == config.SERVER_PASSWORD

# Define what to do with each session
async def handle_client(process):
    game = GameEngine(process.stdin, process.stdout, username)
    await game.run()

# Start the server
await asyncssh.create_server(
    RoguelikeSSHServer,
    host, port,
    server_host_keys=[key_path],
    process_factory=handle_client
)
```

### The Process Object

```python
process.stdin   # Read from player's keyboard
process.stdout  # Write to player's terminal
process.stderr  # Error messages
```

These are **streams** that work like files:
```python
# Read
data = await process.stdin.read()

# Write
process.stdout.write("Hello!")
await process.stdout.drain()  # Flush buffer
```

### Why Async?

**Without async** (traditional threading):
```python
# Each connection needs a new thread
# 100 players = 100 threads = lots of memory!
for connection in connections:
    thread = Thread(target=handle_client, args=(connection,))
    thread.start()
```

**With async** (event loop):
```python
# One event loop handles many connections
# 100 players = 1 thread = efficient!
await asyncio.gather(
    handle_client1(),
    handle_client2(),
    # ... all running concurrently
)
```

### SSH Host Keys

```python
if not config.SSH_HOST_KEY.exists():
    key = asyncssh.generate_private_key('ssh-rsa')
    config.SSH_HOST_KEY.write_bytes(key.export_private_key())
```

The server needs a cryptographic identity. This key:
- Proves the server is who it claims to be
- Prevents man-in-the-middle attacks
- Is like an SSL certificate for websites

### Try It!

Add connection logging:

```python
# In RoguelikeSSHServer:
def connection_made(self, conn):
    peer_ip = conn.get_extra_info('peername')[0]
    logger.info(f"New connection from {peer_ip}")
    
    # Store connection info
    self._connections = getattr(self, '_connections', [])
    self._connections.append(peer_ip)
```

---

## Configuration

**File: `config.py`**

### Why Centralize Configuration?

❌ **Bad**: Magic numbers scattered everywhere
```python
# In file1.py
hp = 30

# In file2.py
hp = 20  # Oops, inconsistent!
```

✅ **Good**: One source of truth
```python
# config.py
PLAYER_STARTING_HP = 30

# Everywhere else
hp = config.PLAYER_STARTING_HP
```

### Environment Variables

```python
SSH_PORT = int(os.getenv('SSH_PORT', '2222'))
#              ^^^^^^^^^^^^^^^^^^^^^^^^  ^^^^^
#              From .env file           Default
```

This pattern allows:
- Development: Use defaults
- Production: Override with .env file
- Security: Keep secrets out of git

### Path Management

```python
BASE_DIR = Path(__file__).parent.absolute()
SAVES_DIR = BASE_DIR / 'data' / 'saves'
```

`Path` is better than string concatenation:
```python
# Don't do this:
path = '/home/user' + '/' + 'data' + '/' + 'saves'

# Do this:
path = Path('/home/user') / 'data' / 'saves'
```

Works on Windows and Linux!

---

## Next Steps

### Easy Modifications

1. **Change game balance**
   - Edit stats in `config.py`
   - Modify entity stats in `entities.py`

2. **Add new enemies**
   - Copy `create_goblin()` function
   - Change stats and appearance
   - Add to spawn logic in `engine.py`

3. **More items**
   - Create new `Item` subclass in `entities.py`
   - Add to spawn logic

### Medium Challenges

1. **Inventory system**
   - Add `inventory: List[Item]` to player
   - Implement pickup without auto-use
   - Create inventory UI

2. **Multiple levels**
   - Add stairs entity
   - Track current level
   - Generate new map when going down

3. **Field of view**
   - Implement FOV algorithm (shadowcasting)
   - Only show visible tiles
   - Remember explored areas

### Advanced Features

1. **Persistent accounts**
   - User database (SQLite)
   - Save/load game state
   - Death=permanent (permadeath)

2. **Multiplayer**
   - Multiple players in same dungeon
   - Chat system
   - PvP or co-op

3. **Content generation**
   - Procedural weapons/items
   - Random quest generation
   - Unique monster variations

---

## 🎓 You're Ready!

You now understand:
- ✅ How SSH servers work
- ✅ Terminal rendering with blessed
- ✅ Game loop architecture
- ✅ Turn-based game logic
- ✅ Procedural generation
- ✅ Entity component patterns
- ✅ Async Python programming

**Time to build!** 🚀

Start small, test often, and have fun. Every roguelike legend started with their first dungeon.
