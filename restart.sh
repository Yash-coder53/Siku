#!/bin/bash

# SIKU TAGALL BOT - Restart Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║            SIKU TAGALL BOT - Restarting            ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Stop the bot
echo -e "${BLUE}[*] Stopping bot...${NC}"
./stop.sh

# Wait for cleanup
sleep 2

# Start the bot
echo -e "${BLUE}[*] Starting bot...${NC}"
./start.sh
