#!/usr/bin/env python3
"""
Extract contiguous lines from a file to a new file.

Usage: python3 extract_lines.py <source_file> <start_line> <end_line> <output_file>
Example: python3 extract_lines.py fcexport.py 37 138 utilities.py
"""

import sys

def extract_lines(source_file, start_line, end_line, output_file):
    """Extract lines from source_file and write to output_file."""
    try:
        with open(source_file, 'r') as f:
            lines = f.readlines()
        
        # Convert to 0-based indexing
        start_idx = start_line - 1
        end_idx = end_line  # end_line is inclusive
        
        if start_idx < 0 or end_idx > len(lines):
            print(f"ERROR: Line range {start_line}-{end_line} invalid for file with {len(lines)} lines")
            return False
            
        extracted_lines = lines[start_idx:end_idx]
        
        with open(output_file, 'w') as f:
            f.writelines(extracted_lines)
            
        print(f"Extracted lines {start_line}-{end_line} from {source_file} to {output_file}")
        return True
        
    except FileNotFoundError:
        print(f"ERROR: File {source_file} not found")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 extract_lines.py <source_file> <start_line> <end_line> <output_file>")
        sys.exit(1)
        
    source_file = sys.argv[1]
    start_line = int(sys.argv[2])
    end_line = int(sys.argv[3])
    output_file = sys.argv[4]
    
    success = extract_lines(source_file, start_line, end_line, output_file)
    sys.exit(0 if success else 1)