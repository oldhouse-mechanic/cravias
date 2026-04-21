#!/usr/bin/env python3
"""
C.R.A.V.I.A.S. — CRA VI a.s.
Computer Response Automation - Voice Input Assistance
Version 2.0.0

Entry point. Run this to start Cravias.

Usage:
    python main.py              # Voice mode (microphone)
    python main.py --text       # Text mode (keyboard, no mic needed)
    python main.py --config PATH  # Custom config file path
"""

import argparse
import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Cravias — Computer Response Automation Voice Input Assistance"
    )
    parser.add_argument(
        "--text", "-t",
        action="store_true",
        help="Run in text mode (keyboard input instead of microphone)"
    )
    parser.add_argument(
        "--silent", "-s",
        action="store_true",
        help="Silent mode: voice input but text-only output (no TTS)"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config/settings.yaml",
        help="Path to config file (default: config/settings.yaml)"
    )
    return parser.parse_args()


def print_banner():
    banner = r"""
 ██████╗ ██████╗  █████╗ ██╗   ██╗██╗  █████╗ ███████╗
██╔════╝ ██╔══██╗██╔══██╗██║   ██║██║ ██╔══██╗██╔════╝
██║      ██████╔╝███████║╚██╗ ██╔╝██║ ███████║███████╗
██║      ██╔══██╗██╔══██║ ╚████╔╝ ██║ ██╔══██║╚════██║
╚██████╗ ██║  ██║██║  ██║  ╚██╔╝  ██║ ██║  ██║███████║
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═╝  ╚═╝╚══════╝

  C.R.A.V.I.A.S. — Computer Response Automation
         Voice Input Assistance  |  v2.0.0
    """
    print(banner)


def main():
    print_banner()
    args = parse_args()

    try:
        from core.assistant import Assistant
        assistant = Assistant(config_path=args.config)
        assistant.run(text_mode=args.text)
    except ImportError as e:
        print(f"\n[ERROR] Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Failed to start Cravias: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
