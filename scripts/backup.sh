#!/bin/bash

# Backup script - copies files to backups/ with timestamp suffix
# Usage: ./backup.sh file1.py file2.txt ...

if [ $# -eq 0 ]; then
    echo "Usage: $0 <file1> [file2] [file3] ..."
    echo "Copies files to backups/ directory with timestamp suffix"
    exit 1
fi

# Create backups directory if it doesn't exist
mkdir -p backups

# Get clean timestamp (YYYYMMDD_HHMMSS format)
timestamp=$(date +%Y%m%d_%H%M%S)

for file in "$@"; do
    if [ ! -f "$file" ]; then
        echo "Warning: $file not found, skipping"
        continue
    fi
    
    basename=$(basename "$file")
    backup_name="${basename}.${timestamp}"
    backup_path="backups/$backup_name"
    
    # Copy file
    cp "$file" "$backup_path"
    echo "Backed up: $file -> $backup_path"
done