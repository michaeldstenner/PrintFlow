#!/bin/bash
# unpack_3mf.sh - Unpack 3MF files into organized folders
# Usage: ./unpack_3mf.sh <file.3mf> [file2.3mf ...]

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <file.3mf> [file2.3mf ...]"
    echo "Unpacks 3MF files into folders with same basename"
    exit 1
fi

for file in "$@"; do
    if [ ! -f "$file" ]; then
        echo "ERROR: File '$file' not found"
        continue
    fi
    
    # Check if it's a 3MF file
    if [[ ! "$file" =~ \.3mf$ ]]; then
        echo "WARNING: '$file' doesn't have .3mf extension, skipping"
        continue
    fi
    
    # Get basename without extension
    basename=$(basename "$file" .3mf)
    dirname=$(dirname "$file")
    output_dir="$dirname/$basename"
    
    echo "Unpacking '$file' to '$output_dir/'"
    
    # Remove existing directory if it exists to avoid conflicts
    if [ -d "$output_dir" ]; then
        rm -rf "$output_dir"
    fi
    
    # Create fresh output directory
    mkdir -p "$output_dir"
    
    # Unpack the 3MF file (which is a ZIP) into the folder
    unzip -q "$file" -d "$output_dir"
    
    echo "  Created: $output_dir/"
    echo "  Contents: $(ls -1 "$output_dir" | tr '\n' ' ')"
done

echo "Done."