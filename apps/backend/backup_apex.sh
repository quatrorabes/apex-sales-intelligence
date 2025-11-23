#!/bin/bash
# APEX System Backup Script
# Creates timestamped backup of database and key files

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups/backup_$TIMESTAMP"

echo "📦 APEX System Backup"
echo "========================================================================"

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo "✅ Created backup directory: $BACKUP_DIR"

# Backup database
if [ -f "apex.db" ]; then
    cp apex.db "$BACKUP_DIR/apex.db"
    echo "✅ Backed up: apex.db"
else
    echo "⚠️  apex.db not found"
fi

# Backup main.py
if [ -f "main.py" ]; then
    cp main.py "$BACKUP_DIR/main.py"
    echo "✅ Backed up: main.py"
fi

# Backup .env file
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/.env"
    echo "✅ Backed up: .env"
fi

# Backup intelligence directory
if [ -d "intelligence" ]; then
    cp -r intelligence "$BACKUP_DIR/intelligence"
    echo "✅ Backed up: intelligence/ directory"
fi

# Backup frontend (if in same parent directory)
if [ -d "../dashboard_v1/src" ]; then
    mkdir -p "$BACKUP_DIR/frontend"
    cp -r ../dashboard_v1/src "$BACKUP_DIR/frontend/src"
    echo "✅ Backed up: frontend/src"
fi

# Get backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

echo ""
echo "========================================================================"
echo "✅ Backup Complete!"
echo "========================================================================"
echo "Location: $BACKUP_DIR"
echo "Size: $BACKUP_SIZE"
echo ""
echo "📋 Backup Contents:"
ls -lh "$BACKUP_DIR"

echo ""
echo "💡 To restore from this backup:"
echo "   cd ~/projects/apex/apps/backend"
echo "   cp -r $BACKUP_DIR/* ."
echo ""
echo "========================================================================"
