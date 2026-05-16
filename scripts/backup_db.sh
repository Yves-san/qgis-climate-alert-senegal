#!/bin/bash
BACKUP_DIR="data/backups"
mkdir -p "$BACKUP_DIR"
TS=$(date +%Y%m%d_%H%M%S)
cp data/senegal_climate_2025_2055.db "$BACKUP_DIR/backup_$TS.db"
echo "Backup saved: $BACKUP_DIR/backup_$TS.db"
# Keep only last 10 backups
ls -t "$BACKUP_DIR"/*.db | tail -n +11 | xargs rm -f
