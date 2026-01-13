# 🚀 Quick Start Guide

## Installation (One-Time Setup)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Create custom config
cp .env.example .env
# Edit .env with your preferred settings
```

## Running the Server

### Option 1: Easy Start (Recommended for beginners)
```bash
python start.py
```

### Option 2: Direct Start
```bash
python server.py
```

### Option 3: Local Testing (No SSH)
```bash
python test_local.py
```

## Connecting to the Game

### From the same machine:
```bash
ssh -p 2222 player@localhost
```

### From another machine:
```bash
ssh -p 2222 player@YOUR_SERVER_IP
```

Default password: **roguelike**

## Quick Commands Reference

### Game Controls
```
Movement:
  Arrow keys, WASD, or hjkl (vi keys)
  
Actions:
  i/g - Pick up item
  e - Use item  
  . or space - Wait
  q - Quit
  r - Restart
```

### Server Management
```bash
# Stop server
Ctrl+C

# View logs
tail -f game.log

# Check if server is running
ps aux | grep server.py

# Kill server if stuck
pkill -f server.py
```

## Troubleshooting

### "Port already in use"
```bash
# Change port in .env:
SSH_PORT=3333

# OR kill process using port:
lsof -ti:2222 | xargs kill -9
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Permission denied"
```bash
# Check firewall:
sudo ufw allow 2222

# OR use higher port (>1024) that doesn't need sudo
```

### Terminal rendering issues
Try a modern terminal:
- **Linux**: GNOME Terminal, Alacritty
- **macOS**: iTerm2
- **Windows**: Windows Terminal

## File Structure Quick Reference

```
rogueterminal/
├── server.py          ← SSH server (start here)
├── config.py          ← Game settings
├── start.py           ← Easy launcher
├── test_local.py      ← Test without SSH
├── game/
│   ├── engine.py      ← Main game loop
│   ├── entities.py    ← Player/monsters/items
│   ├── map_gen.py     ← Dungeon creation
│   ├── render.py      ← Terminal graphics
│   └── input_handler.py ← Keyboard controls
└── README.md          ← Full documentation
```

## Making Changes

### Change game difficulty:
Edit `config.py`:
```python
PLAYER_STARTING_HP = 50  # More HP = easier
MAX_ROOMS = 50           # More rooms = bigger dungeon
```

### Add a new enemy:
Edit `game/entities.py`:
```python
def create_dragon(x, y):
    return Actor(x=x, y=y, char='D', color='bright_red',
                 name='Dragon', hp=50, max_hp=50,
                 attack=15, defense=5)
```

Then edit `game/engine.py` to spawn it:
```python
# In initialize_game():
dragon = create_dragon(x, y)
self.state.entities.append(dragon)
```

### Change map size:
Edit `config.py`:
```python
MAP_WIDTH = 100
MAP_HEIGHT = 60
```

## Resources

- **Full guide**: `README.md`
- **Learning tutorial**: `TUTORIAL.md`
- **Get help**: Check game.log for errors

## Common Questions

**Q: Can I run this on a public server?**
A: Yes! But read the Security section in README.md first.

**Q: How do I change the password?**
A: Edit `.env` or `config.py` and change `SERVER_PASSWORD`

**Q: Can multiple people play at once?**
A: Yes! Each SSH connection gets its own game instance.

**Q: Where are save files?**
A: Not implemented yet. See TUTORIAL.md for how to add this.

**Q: The game crashed, what do I do?**
A: Check `game.log` for errors. Most issues are in there.

## Getting Help

1. Check `game.log` for error messages
2. Read `TUTORIAL.md` for in-depth explanations
3. Read `README.md` for full documentation
4. Check terminal compatibility

---

**Happy Gaming!** 🎮
