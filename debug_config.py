#!/usr/bin/env python3
"""
Debug script to check configuration loading
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=== Configuration Debug ===")
print(f"Project root: {project_root}")
print(f"Current working directory: {os.getcwd()}")

# Check if .env file exists
env_file = project_root / ".env"
print(f"\n.env file exists: {env_file.exists()}")
if env_file.exists():
    print(f".env file path: {env_file}")
    print("\n.env file contents:")
    with open(env_file, 'r') as f:
        content = f.read()
        print(content)
else:
    print("No .env file found!")

# Check environment variables
print(f"\nDATABASE_URL from environment: {os.getenv('DATABASE_URL', 'NOT SET')}")
print(f"DEBUG from environment: {os.getenv('DEBUG', 'NOT SET')}")

# Try to load the app config
try:
    from app.core.config import settings
    print("\nLoaded settings successfully!")
    print(f"DATABASE_URL from settings: {settings.DATABASE_URL}")
    print(f"DEBUG from settings: {settings.debug}")
except Exception as e:
    print(f"\nError loading settings: {e}")
    import traceback
    traceback.print_exc()

print("\n=== End Debug ===")