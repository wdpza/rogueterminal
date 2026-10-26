# RogueTerminal

A multiplayer dungeon crawler you play over SSH. No client to install: if you have a terminal, you can play.

```bash
ssh -p 2222 player@<server-address>
```

Inspired by [terminal.shop](https://terminal.shop) and classic roguelikes such as NetHack.

## Features

- **Play from anywhere over SSH.** An async SSH server gives every connection its own game session.
- **Procedurally generated dungeons.** A rooms-and-corridors generator builds a new, always-playable map every game.
- **Turn-based combat** against goblins and orcs, with health, attack and defence stats.
- **Items and potions** to keep you alive.
- **Colour terminal graphics**, built on `blessed`.
- **Three control schemes:** arrow keys, WASD or vi keys (`hjkl` plus `yubn` for diagonals).

## Tech stack

| Area | Technology |
| --- | --- |
| Language | Python 3.7+ with `asyncio` |
| SSH server | [asyncssh](https://asyncssh.readthedocs.io/) |
| Terminal UI | [blessed](https://blessed.readthedocs.io/) |
| Config | `python-dotenv` (`.env`) |

## How it works

```
SSH client ──► server.py (asyncssh)
                  │  authenticates the player, then starts one game per connection
                  ▼
             game/engine.py   game loop: render → input → update
                  ├── map_gen.py        rooms-and-corridors dungeon generation
                  ├── entities.py       player, monsters and items (dataclasses)
                  ├── input_handler.py  key → action mapping (arrows, WASD, vi)
                  └── render.py         map, entities and HUD drawn with blessed
```

Each connection runs in its own async context, so several players can be in separate games at the same time.

## Getting started

### 1. Install

```bash
git clone https://github.com/wdpza/rogueterminal.git
cd rogueterminal
pip install -r requirements.txt
```

### 2. Configure (optional)

```bash
cp .env.example .env
```

| Variable | Default | Purpose |
| --- | --- | --- |
| `SSH_PORT` | `2222` | Port the game server listens on |
| `SSH_HOST` | `0.0.0.0` | Interface to bind (`127.0.0.1` for local only) |
| `SERVER_PASSWORD` | `roguelike` | Shared password players use to connect |
| `DEBUG` | `False` | Verbose logging |

Map size, room counts and starting stats live in `config.py`.

### 3. Run

| Command | What it does |
| --- | --- |
| `python start.py` | Checks Python and dependencies, then starts the server |
| `python server.py` | Starts the SSH game server directly |
| `python test_local.py` | Plays the game in your own terminal without SSH, for development |

Then connect from any machine:

```bash
ssh -p 2222 player@localhost
```

## Controls

| Key | Action |
| --- | --- |
| Arrows, `WASD` or `hjkl` | Move |
| `y` `u` `b` `n` | Move diagonally |
| `i` or `g` | Pick up item |
| `.` or `Space` | Wait a turn |
| `r` | Restart |
| `q` | Quit |

Clear the dungeon of monsters to win, and grab potions when your HP runs low.

## Project structure

```
rogueterminal/
├── server.py          # SSH server entry point
├── start.py           # Dependency check and launcher
├── test_local.py      # Run the game locally without SSH
├── config.py          # Server and game settings
├── requirements.txt
├── .env.example
├── QUICKSTART.md      # Short command reference
├── TUTORIAL.md        # Walkthrough of the code
└── game/
    ├── engine.py      # Game loop and state
    ├── entities.py    # Player, monsters, items
    ├── map_gen.py     # Dungeon generation
    ├── render.py      # Terminal rendering
    └── input_handler.py
```

SSH host keys are generated into `ssh_keys/` on first run.

## Running it publicly

The server uses a shared password, which is fine for friends and local play. Before exposing it to the internet:

- switch to SSH key authentication or per-user accounts;
- add rate limiting and idle timeouts;
- run it in a container or as a systemd service under a non-root user.

## Roadmap

- Multiple dungeon levels with stairs
- Inventory and equipment
- Field of view (fog of war)
- Save games and a high-score leaderboard
- Shared dungeons for real-time multiplayer

## Author

Built by [Wikus du Plessis](https://github.com/wdpza).
