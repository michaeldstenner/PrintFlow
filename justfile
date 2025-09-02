# PrintFlow project tasks

# Run the test suite
test:
    ./scripts/runmacro.sh


# Run grip on the manual and open in browser
manual:
    #!/usr/bin/env bash
    @echo "Starting grip server for PrintFlowManaual.md..."
    @grip docs/PrintFlowManual.md &
    GRIP_PID=$!
    sleep 2
    open http://localhost:6419
    @echo "Grip running (PID: $GRIP_PID). Press Ctrl+C to stop."
    wait $GRIP_PID

# Run pylint on the macro
lint:
    pylint --rcfile .pylintrc PrintFlow.FCMacro > lint.log || true
    @echo "Pylint report written to lint.log"
    
# Clean up generated files
clean:
    rm -f *.3mf *.log

# Show available commands
help:
    @just --list