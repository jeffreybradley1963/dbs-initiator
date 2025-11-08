#!/bin/bash

# --- OBS STUDIO LAUNCHER & SCENE GENERATOR ---
# This script checks if OBS Studio is running. If not, it starts it
# before running the scene generator Python script.

# The name of the OBS executable. This might be 'obs' or 'obs-studio'.
# 'pgrep -x' checks for an exact match.
OBS_PROCESS_NAME="obs"

echo "Checking if OBS Studio is running..."
if ! pgrep -x "$OBS_PROCESS_NAME" > /dev/null
then
    echo "OBS Studio not found. Starting it now..."
    # Start OBS in the background. The '&' is important.
    nohup obs &> /dev/null &
    echo "Waiting for OBS to initialize..."
    sleep 10 # Adjust this delay if OBS takes longer to start on your system
else
    echo "OBS Studio is already running."
fi

echo "Running the OBS Scene Generator..."

# Find the directory where the script *actually* lives, resolving any symbolic links.
# This is crucial for finding the python script and virtual environment.
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # Resolve $SOURCE until the file is no longer a symlink
  SOURCE="$(readlink "$SOURCE")"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

# --- PYTHON VIRTUAL ENVIRONMENT ACTIVATION ---
# Assumes the virtual environment is in a 'venv' directory alongside the scripts.
VENV_PATH="$SCRIPT_DIR/venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    echo "Activating Python virtual environment..."
    source "$VENV_PATH"
else
    echo "Warning: Python virtual environment not found at '$VENV_PATH'."
    echo "Proceeding with system Python. This may fail if packages are not installed globally."
fi

# --- SCRIPT EXECUTION ---
python3 "$SCRIPT_DIR/obs_scene_generator.py" "$@"
