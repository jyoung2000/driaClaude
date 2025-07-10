#!/bin/bash

# driaClaude Setup Script
# This script prepares the host directories with proper permissions

echo "=== driaClaude Setup Script ==="
echo

# Get current user's UID and GID
USER_ID=$(id -u)
GROUP_ID=$(id -g)

echo "Your current UID: $USER_ID"
echo "Your current GID: $GROUP_ID"
echo

# Create directories if they don't exist
echo "Creating required directories..."
mkdir -p ./data ./voices ./outputs

# Create voices.json if it doesn't exist
if [ ! -f ./voices/voices.json ]; then
    echo "{}" > ./voices/voices.json
    echo "Created voices.json"
fi

# Fix permissions
echo "Setting directory permissions..."
chmod -R 755 ./data ./voices ./outputs

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# User ID and Group ID for container permissions
# These should match your host user to avoid permission issues
PUID=$USER_ID
PGID=$GROUP_ID

# API Key for authentication (change this in production!)
API_KEY=your_secure_api_key_here

# Enable authentication (set to true in production)
ENABLE_AUTH=false
EOF
    echo ".env file created with your UID/GID"
else
    echo ".env file already exists"
    echo "Make sure PUID=$USER_ID and PGID=$GROUP_ID are set in your .env file"
fi

echo
echo "Setup complete!"
echo
echo "To start the container, run:"
echo "  docker compose build"
echo "  docker compose up -d"
echo
echo "The web interface will be available at: http://localhost:4144"