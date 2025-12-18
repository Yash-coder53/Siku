#!/bin/bash

# SIKU TAGALL BOT - Stop Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║            SIKU TAGALL BOT - Stopping              ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Find bot processes
BOT_PIDS=$(pgrep -f "python3 main.py")

if [ -z "$BOT_PIDS" ]; then
    BOT_PIDS=$(pgrep -f "python main.py")
fi

if [ -z "$BOT_PIDS" ]; then
    echo -e "${YELLOW}[!] Bot is not running${NC}"
    exit 0
fi

echo -e "${BLUE}[*] Found bot processes:${NC}"
ps -fp $BOT_PIDS | grep -v "PID"

echo -e "${BLUE}[*] Stopping bot...${NC}"
kill $BOT_PIDS 2>/dev/null

# Wait for graceful shutdown
sleep 3

# Force kill if still running
STILL_RUNNING=$(pgrep -f "python3 main.py")
if [ -n "$STILL_RUNNING" ]; then
    STILL_RUNNING=$(pgrep -f "python main.py")
fi

if [ -n "$STILL_RUNNING" ]; then
    echo -e "${YELLOW}[!] Force killing...${NC}"
    kill -9 $STILL_RUNNING 2>/dev/null
fi

# Verify stopped
if pgrep -f "python3 main.py" > /dev/null || pgrep -f "python main.py" > /dev/null; then
    echo -e "${RED}[!] Failed to stop bot${NC}"
    exit 1
else
    echo -e "${GREEN}[+] Bot stopped successfully!${NC}"
fi
