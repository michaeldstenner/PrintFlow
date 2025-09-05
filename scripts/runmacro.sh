#!/bin/bash

# Configuration
TIMEOUT_SECONDS=10
DEFAULT_APP="FreeCAD_1.1.Weekly"
LOG_FILE="PrintFlow.log"
TEST_SELECTION_FILE="tests/test_selection.tmp"

# Parse options
EXPLICIT_APP=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --freecad|-f)
            EXPLICIT_APP="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [options] [test_names...]"
            echo "Options:"
            echo "  -f, --freecad VERSION    Specify FreeCAD version (default: auto-detect)"
            echo "  -h, --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                       # Run tests with auto-detected FreeCAD"
            echo "  $0 -f FreeCAD_1.0.1     # Run tests with specific FreeCAD version"
            echo "  $0 test1 test2           # Run specific tests"
            echo "  $0 -f FreeCAD_1.0.1 test1  # Run specific test with FreeCAD 1.0.1"
            echo ""
            echo "Note: Script auto-detects running FreeCAD instances. Use -f to override."
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

# Auto-detect running FreeCAD or use explicit version
if [ -n "$EXPLICIT_APP" ]; then
    APP="$EXPLICIT_APP"
    echo "Using explicitly specified FreeCAD: $APP"
else
    # Detect running FreeCAD instances
    running_freecads=$(ps x | grep /Applications/FreeCAD | grep -v grep | awk '{for(i=5;i<=NF;i++) printf "%s ", $i; print ""}' | sed 's|.*/Applications/||' | sed 's|\.app.*||' | sort -u)
    freecad_count=$(echo "$running_freecads" | wc -l | tr -d ' ')
    
    if [ -z "$running_freecads" ] || [ "$running_freecads" = "" ]; then
        echo "ERROR: No running FreeCAD instances detected."
        echo "Please start FreeCAD first, then run this script."
        echo "Alternatively, use -f to specify a FreeCAD version explicitly."
        exit 1
    elif [ "$freecad_count" -eq 1 ]; then
        APP="$running_freecads"
        echo "Auto-detected running FreeCAD: $APP"
    else
        echo "ERROR: Multiple FreeCAD instances running:"
        echo "$running_freecads" | sed 's/^/  /'
        echo ""
        echo "Please specify which version to use with -f option:"
        echo "$running_freecads" | sed 's/^/  -f /'
        echo ""
        echo "Or close one of the FreeCAD instances and try again."
        # TODO: Future enhancement could accept "all" to run tests on each instance sequentially
        exit 1
    fi
fi

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
sendkeys -d 0.01 -a $APP -c '<c:f12>'

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
