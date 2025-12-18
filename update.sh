#!/bin/bash

# SIKU TAGALL BOT - Update Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║            SIKU TAGALL BOT - Updating              ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Backup current version
echo -e "${BLUE}[*] Creating backup...${NC}"
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r data/* "$BACKUP_DIR/" 2>/dev/null
cp bot_settings.json "$BACKUP_DIR/" 2>/dev/null
cp main.py "$BACKUP_DIR/" 2>/dev/null
echo -e "${GREEN}[+] Backup created: $BACKUP_DIR${NC}"

# Update from Git if available
if command -v git &> /dev/null && [ -d ".git" ]; then
    echo -e "${BLUE}[*] Checking for updates via Git...${NC}"
    git fetch origin
    
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main 2>/dev/null || git rev-parse origin/master 2>/dev/null)
    
    if [ "$LOCAL" != "$REMOTE" ] && [ -n "$REMOTE" ]; then
        echo -e "${YELLOW}[!] Updates available${NC}"
        read -p "Update now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}[*] Pulling updates...${NC}"
            git pull
            echo -e "${GREEN}[+] Git update complete${NC}"
        fi
    else
        echo -e "${GREEN}[+] Already up to date${NC}"
    fi
else
    echo -e "${YELLOW}[!] Git not available or not a repository${NC}"
fi

# Update requirements
echo -e "${BLUE}[*] Updating requirements...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt --upgrade > /dev/null 2>&1
    echo -e "${GREEN}[+] Requirements updated${NC}"
else
    echo -e "${YELLOW}[!] Virtual environment not found${NC}"
fi

# Check configuration
echo -e "${BLUE}[*] Checking configuration...${NC}"
if [ ! -f "bot_settings.json" ]; then
    echo -e "${YELLOW}[!] bot_settings.json not found, creating default...${NC}"
    cp bot_settings.example.json bot_settings.json 2>/dev/null || echo '{}' > bot_settings.json
fi

# Make scripts executable
echo -e "${BLUE}[*] Updating script permissions...${NC}"
chmod +x *.sh *.bsh 2>/dev/null
echo -e "${GREEN}[+] Script permissions updated${NC}"

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════╗"
echo "║            Update Completed!                       ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}Note:${NC}"
echo "1. Check backup in: ${BLUE}$BACKUP_DIR${NC}"
echo "2. Review new features in the update"
echo "3. Restart the bot: ${BLUE}./restart.bsh${NC}"
echo ""
echo -e "${CYAN}Update process complete!${NC}"
