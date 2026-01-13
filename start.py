#!/usr/bin/env python3
"""
Quick start script for Terminal Roguelike

This script checks dependencies and starts the server.
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Ensure Python 3.7+"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"   You have Python {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required = ['asyncssh', 'blessed', 'aiofiles', 'dotenv']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} not found")
    
    if missing:
        print("\n📦 Installing missing dependencies...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ])
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("   Try manually: pip install -r requirements.txt")
            return False
    
    return True

def check_config():
    """Check if configuration exists"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  No .env file found")
        print("   Using default configuration from config.py")
        print("   To customize, copy .env.example to .env")
    else:
        print("✅ Configuration file found")
    return True

def main():
    """Main startup routine"""
    print("🗡️  Terminal Roguelike - Startup Check")
    print("=" * 50)
    
    # Run checks
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    check_config()
    
    print("=" * 50)
    print("✅ All checks passed!")
    print("\n🚀 Starting server...\n")
    
    # Start the server
    try:
        import server
        server.main()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
