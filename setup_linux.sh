#!/bin/bash
# Check which Python command is available: python3, py, python

PYTHON_CMD=""

# Check for python3 first
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
# Check for py
elif command -v py >/dev/null 2>&1; then
    PYTHON_CMD="py"
# Check for python
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
fi

if [ -n "$PYTHON_CMD" ]; then
    export PYTHON="$PYTHON_CMD"
    echo "Creating virtual environment..."
    
    $PYTHON -m venv .venv

    echo "Generating launch script launch.sh..."
    cat <<'EOF' > launch.sh
#!/bin/bash
# Optional cleanup of a previous setup script
if [ -f setup_linux.sh ]; then
    rm setup_linux.sh
fi
# Activate virtual environment and run main.py
./.venv/bin/python3 main.py
EOF

    chmod +x launch.sh

    echo "Installing dependencies..."
    ./.venv/bin/pip install urllib3 tqdm

    rm -f setup_windows.bat

    echo "Setup complete. Use ./launch.sh to run the program."

else
    echo "No Python interpreter found! Install Python or add it to your PATH."
fi
