#!/usr/bin/env python
"""
Database migration management script
Usage:
    python migrate.py upgrade    # Apply all migrations
    python migrate.py downgrade  # Rollback one migration
    python migrate.py current    # Show current revision
    python migrate.py history    # Show migration history
"""
import sys
import subprocess
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_alembic_command(command):
    """Run an alembic command and handle output"""
    try:
        # Ensure we're in the right directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Build the full command
        full_command = ["alembic"] + command.split()
        
        logger.info(f"Running: {' '.join(full_command)}")
        
        # Run the command
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("Command completed successfully")
            print(result.stdout)
        else:
            logger.error(f"Command failed: {result.stderr}")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error running command: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "upgrade":
        # Apply all migrations
        target = sys.argv[2] if len(sys.argv) > 2 else "head"
        run_alembic_command(f"upgrade {target}")
        
    elif command == "downgrade":
        # Rollback migrations
        target = sys.argv[2] if len(sys.argv) > 2 else "-1"
        run_alembic_command(f"downgrade {target}")
        
    elif command == "current":
        # Show current revision
        run_alembic_command("current")
        
    elif command == "history":
        # Show migration history
        run_alembic_command("history")
        
    elif command == "create":
        # Create a new migration
        if len(sys.argv) < 3:
            print("Usage: python migrate.py create 'migration message'")
            sys.exit(1)
        message = " ".join(sys.argv[2:])
        run_alembic_command(f"revision --autogenerate -m '{message}'")
        
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()