#!/bin/bash

# --- OBS STUDIO LAUNCHER & DBS-INITIATOR ---
# This script checks if OBS Studio is running. If not, it starts it
# before running the dbs-initiator application.

# The name of the OBS executable. This might be 'obs' or 'obs-studio'.
# 'pgrep -x' checks for an exact match of the process name.
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

echo "Running the dbs-initiator application..."

# Find the directory where the script lives to locate the executable.
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # Resolve $SOURCE until the file is no longer a symlink
  SOURCE="$(readlink "$SOURCE")"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

# --- APPLICATION EXECUTION ---
# Assumes the 'dbs-initiator' executable is in the same directory as this script.
# The executable is created by running 'go build' in the project root.
EXECUTABLE_PATH="$SCRIPT_DIR/dbs-initiator"

# Pass all command-line arguments from this script directly to the Go application.
"$EXECUTABLE_PATH" "$@"
