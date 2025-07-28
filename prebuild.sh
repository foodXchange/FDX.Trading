#!/bin/bash
echo "Starting prebuild script..."

# Function to find Python executable
find_python() {
    # Check common Python locations
    for python_path in \
        "/opt/python/3.12.11/bin/python3" \
        "/opt/python/3.12/bin/python3" \
        "/usr/local/bin/python3.12" \
        "/usr/local/bin/python3" \
        "/usr/bin/python3.12" \
        "/usr/bin/python3" \
        "/tmp/oryx/platforms/python/3.12.11/bin/python3" \
        "/tmp/oryx/platforms/python/3.12/bin/python3" \
        "$(which python3.12 2>/dev/null)" \
        "$(which python3 2>/dev/null)" \
        "$(which python 2>/dev/null)"
    do
        if [ -f "$python_path" ] && [ -x "$python_path" ]; then
            echo "Found Python at: $python_path"
            echo "$python_path"
            return 0
        fi
    done
    
    # If not found, search for any Python 3.12
    echo "Searching for Python 3.12..."
    find /opt /usr -name "python3.12" -type f -executable 2>/dev/null | head -1
}

# Find Python executable
PYTHON_EXE=$(find_python)

if [ -z "$PYTHON_EXE" ]; then
    echo "ERROR: Could not find Python executable"
    exit 1
fi

echo "Using Python: $PYTHON_EXE"

# Export Python path
export PYTHON_PATH=$PYTHON_EXE
export PATH="$(dirname $PYTHON_EXE):$PATH"

# Create symbolic links if needed
if [ ! -f "/opt/python/3.12.11/bin/python3" ] && [ -f "$PYTHON_EXE" ]; then
    echo "Creating symbolic links for Python..."
    mkdir -p /opt/python/3.12.11/bin
    ln -sf "$PYTHON_EXE" /opt/python/3.12.11/bin/python3
    ln -sf "$PYTHON_EXE" /opt/python/3.12.11/bin/python
fi

# Fix pip if it exists
if [ -f "/tmp/oryx/platforms/python/3.12.11/bin/pip" ]; then
    echo "Fixing pip shebang..."
    sed -i "1s|.*|#!$PYTHON_EXE|" /tmp/oryx/platforms/python/3.12.11/bin/pip
fi

# Install pip if missing
if ! command -v pip &> /dev/null; then
    echo "Installing pip..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | $PYTHON_EXE
fi

echo "Prebuild script completed successfully"