#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export ALSA_CONFIG_PATH=/dev/null
python main.py "$@" 2>/dev/null
