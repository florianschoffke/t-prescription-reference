#!/bin/bash

# Start the OAuth server
echo "Starting OAuth server..."
python3 webserver/t-oauth.py &

# Start the prescription service
echo "Starting prescription service..."
python3 webserver/t-server.py &

# Serve the web client
echo "Starting web client server..."
cd web_client
python3 -m http.server 8000 &

# Wait for all background processes to exit
wait
