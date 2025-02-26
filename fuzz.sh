#!/bin/bash

# Default max depth
MAX_DEPTH=200

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -d|--depth)
      MAX_DEPTH="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [-d|--depth MAX_DEPTH]"
      exit 1
      ;;
  esac
done

# Validate max depth
if ! [[ "$MAX_DEPTH" =~ ^[0-9]+$ ]]; then
  echo "Error: Max depth must be a positive integer"
  exit 1
fi

# Directory paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ATTACKER_DIR="$SCRIPT_DIR/attacker"
VICTIM_DIR="$SCRIPT_DIR/victim"

# Port configuration
ATTACKER_PORT=1337
VICTIM_PORT=5000

port_in_use() {
    lsof -i:"$1" &>/dev/null
    return $?
}

kill_port_process() {
    echo "Killing process using port $1..."
    lsof -ti:"$1" | xargs kill -9 2>/dev/null
}

cleanup() {
    echo "Cleaning up..."
    if [ -n "$ATTACKER_PID" ]; then
        kill $ATTACKER_PID 2>/dev/null
    fi
    if [ -n "$VICTIM_PID" ]; then
        kill $VICTIM_PID 2>/dev/null
    fi
    exit 0
}

# Set up trap for cleanup on exit
trap cleanup SIGINT SIGTERM

# Check if ports are already in use
if port_in_use $ATTACKER_PORT; then
    echo "Port $ATTACKER_PORT is already in use. Attempting to free it..."
    kill_port_process $ATTACKER_PORT
fi

if port_in_use $VICTIM_PORT; then
    echo "Port $VICTIM_PORT is already in use. Attempting to free it..."
    kill_port_process $VICTIM_PORT
fi

# Start the attacker's server
echo "[*] Starting attacker server on port $ATTACKER_PORT..."
cd "$ATTACKER_DIR" || { echo "Failed to change directory to $ATTACKER_DIR"; exit 1; }
python3 -m http.server $ATTACKER_PORT &
ATTACKER_PID=$!

# Check if attacker server started successfully
sleep 1
if ! port_in_use $ATTACKER_PORT; then
    echo "Failed to start attacker server on port $ATTACKER_PORT"
    cleanup
    exit 1
fi
echo "[+] Attacker server started: http://attacker.com:$ATTACKER_PORT/grandparent.html"

# Start the victim's server with the specified max depth
echo "[*] Starting victim server on port $VICTIM_PORT with max depth $MAX_DEPTH..."
cd "$VICTIM_DIR" || { echo "Failed to change directory to $VICTIM_DIR"; exit 1; }
XFO_MAX_DEPTH=$MAX_DEPTH python3 app.py &
VICTIM_PID=$!

# Check if victim server started successfully
sleep 1
if ! port_in_use $VICTIM_PORT; then
    echo "Failed to start victim server on port $VICTIM_PORT"
    cleanup
    exit 1
fi
echo "[+] Victim server started: http://victim.com:$VICTIM_PORT/1"

# Remind about hosts file
echo ""
echo "IMPORTANT: Make sure your /etc/hosts file contains these entries:"
echo "127.0.0.1 victim.com"
echo "127.0.0.1 attacker.com"
echo ""
echo "Open http://attacker.com:$ATTACKER_PORT/grandparent.html in your browser"
echo ""
echo "Current configuration:"
echo "- Maximum nesting depth: $MAX_DEPTH"
echo ""
echo "Press Ctrl+C to stop the servers"

# Wait for Ctrl+C
wait

