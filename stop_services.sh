#!/bin/bash

# Function to kill processes by name
kill_process_by_name() {
    process_name=$1
    echo "Killing process: $process_name"
    pkill -f $process_name
}

# Kill the E-Rezept-Fachdienst 
kill_process_by_name "erp-fd.py"

# Kill the OAuth server
kill_process_by_name "t-oauth.py"

# Kill the prescription service
kill_process_by_name "t-server.py"

# Kill the web client server (Python HTTP server)
kill_process_by_name "http.server"

echo "All services have been shut down."
