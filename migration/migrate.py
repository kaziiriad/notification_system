#!/usr/bin/env python3
"""
Database migration management script.
Provides easy commands for common migration operations.
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd):
    """Run a shell command and handle errors."""
    try:
        # Get the directory where this script is located (migration directory)
        script_dir = Path(__file__).parent.resolve()
        
        # Try to get the current directory, but handle the case where it doesn't exist
        original_dir = None
        try:
            original_dir = os.getcwd()
        except (FileNotFoundError, OSError):
            # Current directory doesn't exist or is inaccessible
            print("Warning: Current directory is not accessible. Working from script directory.")
        
        # Change to the migration directory before running alembic commands
        os.chdir(script_dir)
        
        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return True
        finally:
            # Only try to change back if we had a valid original directory
            if original_dir:
                try:
                    os.chdir(original_dir)
                except (FileNotFoundError, OSError):
                    # Original directory no longer exists, stay in script directory
                    print("Warning: Original directory no longer exists. Staying in script directory.")
            
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def init_migrations():
    """Initialize Alembic migrations."""
    print("Initializing migrations...")
    return run_command("alembic init alembic")

def create_migration(message="Auto migration"):
    """Create a new migration."""
    print(f"Creating migration: {message}")
    return run_command(f'alembic revision --autogenerate -m "{message}"')

def upgrade_database(revision="head"):
    """Upgrade database to a specific revision."""
    print(f"Upgrading database to {revision}...")
    return run_command(f"alembic upgrade {revision}")

def downgrade_database(revision):
    """Downgrade database to a specific revision."""
    print(f"Downgrading database to {revision}...")
    return run_command(f"alembic downgrade {revision}")

def show_history():
    """Show migration history."""
    print("Migration history:")
    return run_command("alembic history")

def show_current():
    """Show current migration."""
    print("Current migration:")
    return run_command("alembic current")

def check_alembic_config():
    """Check if alembic.ini exists in the script directory."""
    try:
        script_dir = Path(__file__).parent.resolve()
        alembic_ini = script_dir / "alembic.ini"
        
        if not alembic_ini.exists():
            print(f"Error: alembic.ini not found in {script_dir}")
            print("Please run 'python migrate.py init' first to initialize migrations.")
            return False
        return True
    except Exception as e:
        print(f"Error checking alembic config: {e}")
        return False

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migrate.py init                    # Initialize migrations")
        print("  python migrate.py create [message]        # Create new migration")
        print("  python migrate.py upgrade [revision]      # Upgrade database")
        print("  python migrate.py downgrade <revision>    # Downgrade database")
        print("  python migrate.py history                 # Show migration history")
        print("  python migrate.py current                 # Show current migration")
        return

    command = sys.argv[1].lower()

    # For init command, we don't need to check for alembic.ini
    if command == "init":
        init_migrations()
        return

    # For all other commands, check if alembic.ini exists
    if not check_alembic_config():
        return

    if command == "create":
        message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Auto migration"
        create_migration(message)
    elif command == "upgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        upgrade_database(revision)
    elif command == "downgrade":
        if len(sys.argv) < 3:
            print("Error: downgrade requires a revision")
            return
        downgrade_database(sys.argv[2])
    elif command == "history":
        show_history()
    elif command == "current":
        show_current()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()