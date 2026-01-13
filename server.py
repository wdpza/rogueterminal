"""
SSH Server for Roguelike Game

This module sets up an SSH server that allows players to connect and play
the roguelike game through their terminal. Each SSH connection spawns a new
game instance.

HOW IT WORKS:
1. AsyncSSH creates an SSH server listening on a port
2. When a player connects, they authenticate with a password
3. Their connection is handed to handle_client()
4. We create a game instance for them and run it
5. When they disconnect, the game cleans up
"""

import asyncio
import asyncssh
import logging
import sys
from pathlib import Path

# Import our configuration
import config

# Import the game engine (we'll create this next)
from game.engine import GameEngine

# Set up logging to help us debug issues
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RoguelikeSSHServer(asyncssh.SSHServer):
    """
    Custom SSH Server Handler
    
    This class handles SSH connection events like authentication and
    session establishment. AsyncSSH calls these methods automatically.
    """
    
    def connection_made(self, conn):
        """Called when a new connection is established"""
        self._conn = conn
        peer = conn.get_extra_info('peername')[0]
        logger.info(f"New connection from {peer}")
    
    def connection_lost(self, exc):
        """Called when a connection is closed"""
        if exc:
            logger.error(f"Connection lost with error: {exc}")
        else:
            logger.info("Connection closed normally")
    
    def password_auth_supported(self):
        """Enable password authentication"""
        return True
    
    def validate_password(self, username, password):
        """
        Validate user credentials
        
        For simplicity, we use a shared password for all players.
        In a production environment, you'd want:
        - Individual user accounts
        - SSH key authentication
        - Rate limiting to prevent brute force attacks
        """
        # Check if password matches our configured password
        is_valid = password == config.SERVER_PASSWORD
        
        if is_valid:
            logger.info(f"User '{username}' authenticated successfully")
        else:
            logger.warning(f"Failed authentication attempt for '{username}'")
        
        return is_valid


async def handle_client(process):
    """
    Handle an SSH client connection
    
    This is called for each new SSH session. The 'process' object gives us:
    - process.stdin: Input from the player's terminal
    - process.stdout: Output to the player's terminal
    - process.stderr: Error output (if needed)
    - process.channel: The SSH channel with more control options
    
    Args:
        process: AsyncSSH SSHServerProcess object representing this session
    """
    try:
        # Get the username (for display, save files, etc.)
        username = process.channel.get_extra_info('username', 'anonymous')
        logger.info(f"Starting game session for {username}")
        
        # Set terminal to raw mode for immediate keypress response
        # This allows character-by-character input without waiting for Enter
        process.channel.set_line_mode(False)
        process.channel.set_echo(False)
        
        # Create a new game instance for this player
        # We pass the stdin/stdout so the game can read input and draw output
        game = GameEngine(
            stdin=process.stdin,
            stdout=process.stdout,
            username=username
        )
        
        # Run the game loop
        # This will block until the player quits or disconnects
        await game.run()
        
        logger.info(f"Game session ended for {username}")
        
    except asyncio.CancelledError:
        # Connection was terminated
        logger.info(f"Game session cancelled for user")
    except Exception as e:
        # Something went wrong
        logger.error(f"Error in game session: {e}", exc_info=True)
        # Try to show error to player if connection still alive
        try:
            process.stdout.write(f"\n\nAn error occurred: {e}\n")
            await process.stdout.drain()
        except:
            pass
    finally:
        # Clean up - close the connection gracefully
        process.exit(0)


async def start_server():
    """
    Start the SSH server
    
    This creates the SSH server and keeps it running until interrupted.
    """
    
    # Check if we have an SSH host key, generate one if not
    if not config.SSH_HOST_KEY.exists():
        logger.info("No SSH host key found, generating one...")
        logger.info(f"This may take a moment...")
        
        # Generate a new RSA key pair for the server
        # This is what proves the server's identity to connecting clients
        key = asyncssh.generate_private_key('ssh-rsa')
        config.SSH_HOST_KEY.write_bytes(key.export_private_key())
        logger.info(f"Generated SSH host key at {config.SSH_HOST_KEY}")
    
    # Start the SSH server
    logger.info(f"Starting SSH server on {config.SSH_HOST}:{config.SSH_PORT}")
    logger.info(f"Players can connect with: ssh -p {config.SSH_PORT} player@{config.SSH_HOST}")
    logger.info(f"Password: {config.SERVER_PASSWORD}")
    
    try:
        await asyncssh.create_server(
            RoguelikeSSHServer,          # Our custom server handler
            config.SSH_HOST,              # Host to bind to
            config.SSH_PORT,              # Port to listen on
            server_host_keys=[str(config.SSH_HOST_KEY)],  # Our cryptographic identity
            process_factory=handle_client,  # Function to handle each connection
            encoding='utf-8'              # Character encoding for text
        )
        
        logger.info("Server is running! Press Ctrl+C to stop.")
        
        # Keep the server running forever (until Ctrl+C)
        await asyncio.Event().wait()
        
    except OSError as e:
        if e.errno == 98:  # Address already in use
            logger.error(f"Port {config.SSH_PORT} is already in use!")
            logger.error("Try a different port in config.py or .env file")
        else:
            logger.error(f"Failed to start server: {e}")
        sys.exit(1)
    except asyncssh.Error as e:
        logger.error(f"SSH error: {e}")
        sys.exit(1)


def main():
    """Main entry point for the server"""
    try:
        # Run the async server
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
