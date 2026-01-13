# 🗡️ Terminal Roguelike

A classic dungeon-crawler roguelike game that you can play over SSH! Inspired by terminal.shop and traditional roguelikes like NetHack.

## 🎮 What is This?

This is a fully functional roguelike game that runs entirely in your terminal and can be accessed remotely via SSH. Players can connect from anywhere and play the game directly in their terminal, no installation required on the client side!

**Features:**
- 🏰 Procedurally generated dungeons
- ⚔️ Turn-based combat system
- 🧌 Multiple enemy types (Goblins, Orcs)
- 🧪 Items and potions
- 📊 Health and stats tracking
- 🎨 Colorful terminal graphics using blessed
- 🔐 SSH-based multiplayer access

## 📋 Prerequisites

Before you start, you'll need:

- **Python 3.7+** installed on your server
- **pip** (Python package manager)
- **SSH access** to your server (if deploying remotely)
- **Basic terminal/command line knowledge**

## 🚀 Quick Start

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

This installs:
- `asyncssh` - For SSH server functionality
- `blessed` - For terminal graphics and input handling
- `aiofiles` - For async file operations
- `python-dotenv` - For environment variable management

### 2. Configure the Server

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` to customize your settings:

```bash
# Optional: Change the port (default is 2222)
SSH_PORT=2222

# Optional: Change the password (default is "roguelike")
SERVER_PASSWORD=your_secret_password

# Optional: Enable debug logging
DEBUG=False
```

**Important:** You can also edit settings in `config.py` if you prefer.

### 3. Run the Server

Start the SSH game server:

```bash
python server.py
```

You should see output like:

```
INFO - Starting SSH server on 0.0.0.0:2222
INFO - Players can connect with: ssh -p 2222 player@localhost
INFO - Password: roguelike
INFO - Server is running! Press Ctrl+C to stop.
```

### 4. Play the Game!

From any machine (including the same machine), connect via SSH:

```bash
ssh -p 2222 player@localhost
```

Replace `localhost` with your server's IP address if connecting remotely.

Enter the password (default: `roguelike`) and start playing!

## 🎯 How to Play

### Controls

**Movement:**
- Arrow Keys OR `hjkl` (vi keys) OR `wasd`
- Diagonal: `yubn` (vi keys)

**Actions:**
- `i` or `g` - Pick up item
- `e` - Use item (currently auto-uses on pickup)
- `.` or `space` - Wait/rest
- `q` - Quit game
- `r` - Restart game

### Objective

Explore the dungeon and defeat all monsters to win! Watch your HP and pick up health potions to survive.

## 📂 Project Structure

```
rogueterminal/
├── server.py              # SSH server entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
├── game/                 # Game package
│   ├── __init__.py
│   ├── engine.py         # Main game loop and logic
│   ├── entities.py       # Player, monsters, items
│   ├── map_gen.py        # Dungeon generation
│   ├── render.py         # Terminal rendering
│   └── input_handler.py  # Keyboard input processing
├── data/                 # Game data
│   └── saves/            # Player save files (future)
└── ssh_keys/             # SSH host keys (auto-generated)
```

## 🔧 Architecture Explained

### How It Works

#### 1. **SSH Server (`server.py`)**
- Uses `asyncssh` to create an SSH server
- Listens for incoming connections on port 2222
- Authenticates players with a password
- Spawns a new game instance for each connection

#### 2. **Game Engine (`game/engine.py`)**
- Main game loop: Input → Update → Render
- Manages game state (player, enemies, map, messages)
- Handles player actions and enemy AI
- Coordinates all subsystems

#### 3. **Entity System (`game/entities.py`)**
- Defines all game objects (player, monsters, items)
- Uses Python dataclasses for clean code
- Implements combat mechanics (attack, damage, HP)
- Factory functions for creating entities with consistent stats

#### 4. **Map Generation (`game/map_gen.py`)**
- Procedural dungeon generation using "rooms and corridors" algorithm
- Creates random rectangular rooms
- Connects rooms with L-shaped tunnels
- Ensures playable maps every time

#### 5. **Rendering (`game/render.py`)**
- Uses `blessed` library for terminal control
- Draws map, entities, and UI
- Supports colors and positioning
- Handles terminal resize events

#### 6. **Input Handling (`game/input_handler.py`)**
- Maps keyboard keys to game actions
- Supports multiple control schemes (arrows, vi keys, wasd)
- Uses enums for type-safe action handling

### Technology Stack

**AsyncSSH:**
- Provides SSH2 protocol implementation in Python
- Handles encryption, authentication, channels
- Allows us to create custom SSH applications
- Each connection gets its own async context

**Blessed:**
- High-level terminal control library
- Abstracts away ANSI escape codes
- Provides easy color and positioning
- Cross-platform terminal handling

**Python asyncio:**
- Enables concurrent handling of multiple SSH connections
- Non-blocking I/O for responsive gameplay
- Event loop manages all async operations

## 🎓 Learning Guide

### For Beginners

If you're new to this stack, here's how to learn:

1. **Start with the basics:**
   - Read through `config.py` to understand settings
   - Look at `game/entities.py` - it's the simplest module
   - The `@dataclass` decorator auto-generates boilerplate code

2. **Understand the game loop:**
   - Open `game/engine.py` and find the `run()` method
   - Follow the loop: render → input → update → repeat
   - This is the core pattern of all games

3. **Learn terminal programming:**
   - `blessed` makes this easy - try the examples in `game/render.py`
   - `terminal.move_xy(x, y)` moves the cursor
   - Colors are as simple as `terminal.red('text')`

4. **Explore SSH server code:**
   - `server.py` shows how asyncssh works
   - Each connection calls `handle_client()`
   - The game engine runs in that context

### Next Steps for Development

**Easy additions:**
- Add more enemy types in `entities.py`
- Create new items (weapons, armor)
- Adjust game balance in `config.py`
- Add more room shapes in `map_gen.py`

**Medium complexity:**
- Implement proper inventory system
- Add multiple dungeon levels (stairs up/down)
- Save/load game state
- Add field of view (fog of war)

**Advanced features:**
- User accounts and persistent characters
- High score leaderboard
- Spectator mode
- Real-time multiplayer in same dungeon

## 🌐 Deploying to Production

### Security Considerations

**⚠️ IMPORTANT:** This starter template uses basic password auth. For production:

1. **Use SSH keys instead of passwords:**
   ```python
   # In server.py, modify validate_password to validate_public_key
   ```

2. **Run in a container:**
   ```bash
   docker run --rm -p 2222:2222 your-roguelike-image
   ```

3. **Rate limiting:**
   - Add connection rate limiting to prevent DoS
   - Implement failed login tracking

4. **Resource limits:**
   - Set max memory per game session
   - Timeout idle connections
   - Limit CPU usage

### Running as a Service

Create a systemd service file `/etc/systemd/system/roguelike.service`:

```ini
[Unit]
Description=Terminal Roguelike SSH Server
After=network.target

[Service]
Type=simple
User=gameserver
WorkingDirectory=/opt/rogueterminal
ExecStart=/usr/bin/python3 /opt/rogueterminal/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable roguelike
sudo systemctl start roguelike
```

## 🐛 Troubleshooting

### "Port already in use"
Another process is using port 2222. Change the port in `.env` or stop the other process.

### "Module not found"
Install dependencies: `pip install -r requirements.txt`

### "Connection refused"
- Check firewall: `sudo ufw allow 2222`
- Verify server is running: `ps aux | grep server.py`
- Check logs in `game.log`

### Terminal looks weird
Your terminal emulator might not support all features. Try:
- iTerm2 (macOS)
- Windows Terminal (Windows)
- GNOME Terminal or Alacritty (Linux)

## 📚 Resources

**Learn More About:**
- [Roguelike Development](http://rogueliketutorials.com/) - Comprehensive tutorials
- [asyncssh Documentation](https://asyncssh.readthedocs.io/)
- [blessed Documentation](https://blessed.readthedocs.io/)
- [Python asyncio Guide](https://docs.python.org/3/library/asyncio.html)

**Inspiration:**
- [terminal.shop](https://terminal.shop) - The coffee shop that inspired this
- [NetHack](https://www.nethack.org/) - Classic roguelike
- [Brogue](https://sites.google.com/site/broguegame/) - Beautiful roguelike

## 🤝 Contributing

This is a learning project! Feel free to:
- Add features
- Fix bugs
- Improve documentation
- Share your deployed version

## 📝 License

This project is provided as-is for educational purposes. Feel free to use and modify as you wish!

## 🎮 Have Fun!

You've now got a fully functional SSH-accessible roguelike game! 

Try it out, modify it, break it, fix it, and most importantly - learn from it. This is a great foundation for understanding async programming, terminal interfaces, and game development.

Happy coding! 🚀
