#!/bin/bash

# Configuration
TIMEOUT_SECONDS=10
LOG_FILE="PrintFlow.log"
TEST_SELECTION_FILE="test_selection.tmp"

# Write test arguments to file if provided
if [ $# -gt 0 ]; then
    echo "Running specific tests: $*"
    printf '%s\n' "$@" > "$TEST_SELECTION_FILE"
else
    echo "Starting test suite..."
    # Clear test selection file to run all tests
    > "$TEST_SELECTION_FILE"
fi
echo "Monitoring progress (timeout: ${TIMEOUT_SECONDS}s)..."

# Get starting point in log
if [ -f "$LOG_FILE" ]; then
    start_line=$(wc -l < "$LOG_FILE")
else
    start_line=0
fi

# Start the tests using F12 hotkey
sendkeys -d 0.01 -a FreeCAD_1.0.1 -c '<c:f12>'

# Monitor for completion
last_activity=$(date +%s)
while true; do
    sleep 1
    
    if [ -f "$LOG_FILE" ]; then
        current_lines=$(wc -l < "$LOG_FILE")
        
        # Detect if log was truncated (current lines < start_line)
        if [ $current_lines -lt $start_line ]; then
            echo "Log file truncated, resetting..."
            start_line=0
        fi
        
        # Check for new progress lines since start
        new_progress=$(tail -n +$((start_line + 1)) "$LOG_FILE" 2>/dev/null | \
                      grep -E "TESTPROG:|TESTDONE:")
        
        if [ -n "$new_progress" ]; then
            echo "$new_progress"
            last_activity=$(date +%s)
            
            # Check if done
            if echo "$new_progress" | grep -q "TESTDONE:"; then
                echo "Tests completed!"
                exit 0
            fi
            
            # Update start line to current position
            start_line=$current_lines
        fi
    fi
    
    # Check timeout
    current_time=$(date +%s)
    time_since_activity=$((current_time - last_activity))
    
    if [ $time_since_activity -gt $TIMEOUT_SECONDS ]; then
        echo "Timeout: No activity for ${TIMEOUT_SECONDS} seconds"
        echo "Test suite may have crashed or hung"
        exit 1
    fi
done
