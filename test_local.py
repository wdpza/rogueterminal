#!/usr/bin/env python3
"""
Local Test Script

Run the game directly in your terminal without SSH.
This is useful for development and testing.
"""

import asyncio
import sys
from blessed import Terminal
from game.engine import GameEngine

class MockProcess:
    """Mock SSH process for local testing"""
    def __init__(self):
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        
    async def drain(self):
        """Mock drain method"""
        sys.stdout.flush()

async def main():
    """Run the game locally"""
    print("Starting local test game...")
    print("This simulates the game as if you connected via SSH.")
    print("Press Ctrl+C to exit.\n")
    
    # Create a mock SSH process
    process = MockProcess()
    
    # Create and run the game engine
    engine = GameEngine(
        stdin=sys.stdin,
        stdout=sys.stdout,
        username="LocalPlayer"
    )
    
    await engine.run()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGame stopped. Goodbye!")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
