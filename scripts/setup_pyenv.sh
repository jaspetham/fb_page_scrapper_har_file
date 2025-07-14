#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e
# Enable verbose output for commands, useful for debugging
# set -x

echo "--- Comprehensive Automated Pyenv and Project Python Setup Script ---"

# --- Configuration ---
# Determine the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Determine the project root: assumes script is in a subdirectory (e.g., 'scripts')
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

PYTHON_VERSION_FILE="${PROJECT_ROOT}/.python-version"

# Determine the user's shell configuration file
case "$SHELL" in
    */bash) SHELL_RC_FILE="${HOME}/.bashrc" ;;
    */zsh)  SHELL_RC_FILE="${HOME}/.zshrc" ;;
    *)
        echo "Warning: Unsupported shell '$SHELL'. Defaulting to ~/.bashrc for configuration." >&2
        SHELL_RC_FILE="${HOME}/.bashrc"
        ;;
esac

echo "Script located in: ${SCRIPT_DIR}"
echo "Project root determined as: ${PROJECT_ROOT}"
echo "Python version file will be at: ${PYTHON_VERSION_FILE}"
echo "Shell RC file for pyenv configuration: ${SHELL_RC_FILE}"

# --- Step 1: Install pyenv if not present, or handle existing partial installs ---
if ! command -v pyenv &> /dev/null; then
    echo ""
    echo "Pyenv is not found on your system."

    # Check for partially installed .pyenv directory
    if [ -d "${HOME}/.pyenv" ]; then
        echo "A partial pyenv installation exists at ${HOME}/.pyenv."
        read -p "Do you want to REMOVE this directory and perform a clean pyenv installation? (y/N): " remove_pyenv_confirm
        if [[ "$remove_pyenv_confirm" =~ ^[Yy]$ ]]; then
            echo "Removing ${HOME}/.pyenv..."
            rm -rf "${HOME}/.pyenv" || {
                echo "Error: Failed to remove ${HOME}/.pyenv. Please remove it manually and re-run the script." >&2
                exit 1
            }
            echo "${HOME}/.pyenv removed."
        else
            echo "Cannot proceed with pyenv installation without a clean state. Exiting." >&2
            exit 1
        fi
    fi

    read -p "Do you want to INSTALL pyenv now? (y/N): " install_pyenv_confirm
    if [[ "$install_pyenv_confirm" =~ ^[Yy]$ ]]; then
        echo "Installing pyenv via curl (may require internet connection)..."
        curl https://pyenv.run | bash || {
            echo "Error: Failed to install pyenv. Please check internet connection or curl installation." >&2
            exit 1
        }
        echo "Pyenv installed successfully to ${HOME}/.pyenv."
    else
        echo "Pyenv installation skipped. Cannot proceed without pyenv." >&2
        exit 1
    fi
else
    echo "Pyenv is already installed."
fi

# --- Step 2: Add pyenv initialization to shell RC file if not present ---
# Check for PYENV_ROOT, which is a good indicator
if ! grep -q 'PYENV_ROOT="$HOME/.pyenv"' "$SHELL_RC_FILE"; then
    echo ""
    echo "Pyenv initialization lines not found in ${SHELL_RC_FILE}."
    read -p "Do you want to add pyenv initialization to ${SHELL_RC_FILE} permanently? (y/N): " add_rc_confirm
    if [[ "$add_rc_confirm" =~ ^[Yy]$ ]]; then
        echo "Adding pyenv initialization lines to ${SHELL_RC_FILE}..."
        echo '' >> "$SHELL_RC_FILE"
        echo '# pyenv setup - added by setup_pyenv.sh script' >> "$SHELL_RC_FILE"
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> "$SHELL_RC_FILE"
        echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> "$SHELL_RC_FILE"
        echo 'eval "$(pyenv init -)"' >> "$SHELL_RC_FILE"
        echo 'eval "$(pyenv virtualenv-init -)"' >> "$SHELL_RC_FILE"
        echo '# End pyenv setup' >> "$SHELL_RC_FILE"
        echo "Pyenv initialization lines added to ${SHELL_RC_FILE}."
    else
        echo "Skipping permanent addition of pyenv initialization lines."
        echo "You will need to manually source pyenv in future sessions."
    fi
else
    echo "Pyenv initialization lines already exist in ${SHELL_RC_FILE}."
fi

# --- Step 3: Initialize pyenv for the current script's execution context ---
# This is crucial for pyenv commands to work immediately within THIS script.
echo "Initializing pyenv for current script execution..."
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
echo "Pyenv is now active in this script's environment."


# --- Step 4: Handle .python-version file ---
# If not, prompt user for desired version and create the file
if [ ! -f "$PYTHON_VERSION_FILE" ]; then
    echo ""
    echo "Info: .python-version file not found at ${PYTHON_VERSION_FILE}."
    echo "This file defines the Python version for this specific project."
    read -p "Enter the desired Python version (e.g., 3.9.18, 3.10.13, 3.11.9, 3.12.3): " DESIRED_VERSION

    if [ -z "$DESIRED_VERSION" ]; then
        echo "Error: No Python version entered. Exiting." >&2
        exit 1
    fi

    echo "$DESIRED_VERSION" > "$PYTHON_VERSION_FILE"
    echo "Created .python-version file with: ${DESIRED_VERSION}"
else
    # Read the desired Python version from existing file
    DESIRED_VERSION=$(cat "$PYTHON_VERSION_FILE" | tr -d '[:space:]')
    if [ -z "$DESIRED_VERSION" ]; then
        echo "Error: .python-version file is empty at ${PYTHON_VERSION_FILE}. Please add a version or delete the file to be prompted." >&2
        exit 1
    fi
    echo "Desired Python version from .python-version: ${DESIRED_VERSION}"
fi


# --- Step 5: Install the Python version using pyenv ---
echo ""
echo "--- Installing Python ${DESIRED_VERSION} using pyenv ---"
pyenv install "$DESIRED_VERSION" || {
    echo "Error: Failed to install Python ${DESIRED_VERSION}." >&2
    echo "This often means missing build dependencies. For Ubuntu/Debian, try:" >&2
    echo "  sudo apt update && sudo apt install build-essential libssl-dev zlib1g-dev \\" >&2
    echo "  libbz2-dev libreadline-dev libsqlite3-dev curl \\" >&2
    echo "  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev" >&2
    exit 1
}
echo "Python ${DESIRED_VERSION} installation complete (or already installed)."

# --- Step 6: Set the local Python version for the project directory ---
echo ""
echo "--- Setting local Python version to ${DESIRED_VERSION} for ${PROJECT_ROOT} ---"
(
    cd "$PROJECT_ROOT" && \
    pyenv local "$DESIRED_VERSION"
) || {
    echo "Error: Failed to set local Python version to ${DESIRED_VERSION}." >&2
    echo "Ensure the version is installed correctly and you have write permissions in ${PROJECT_ROOT}." >&2
    exit 1
}
echo "Local Python version successfully set to ${DESIRED_VERSION} in ${PROJECT_ROOT}."

echo ""
echo "--- All Pyenv setup finished successfully! ---"
echo "----------------------------------------------------------------------------------"
echo "IMPORTANT: For 'pyenv' and the newly installed Python version to be active in your"
echo "           *current* interactive terminal session (and future ones),"
echo "           you MUST close and reopen your terminal OR run: 'source ${SHELL_RC_FILE}'"
echo "           After that, navigate to your project root (${PROJECT_ROOT})"
echo "           and run 'python --version' or 'python3 --version' to confirm."
echo "----------------------------------------------------------------------------------"