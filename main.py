#!/usr/bin/env python3
"""LED Strip Controller - Main entry point.

Controls a 392-pixel NeoPixel LED strip displaying time, temperature,
countdown, and custom text via Telegram bot interface.
"""

import asyncio
import sys

from src.bot import run_bot


def main() -> int:
    """Application entry point.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        asyncio.run(run_bot())
        return 0
    except KeyboardInterrupt:
        print("\nShutting down...")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
