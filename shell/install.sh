#!/bin/bash

# DevBrain Installation Script

# Configuration
SHELL_RC=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    echo "Unsupported shell. Please use bash or zsh."
    exit 1
fi

# Create installation directory
INSTALL_DIR="$HOME/.devbrain"
mkdir -p "$INSTALL_DIR"

# Copy shell script
cp "$(dirname "$0")/devbrain.sh" "$INSTALL_DIR/devbrain.sh"
chmod +x "$INSTALL_DIR/devbrain.sh"

# Add to shell rc if not already present
if ! grep -q "source $INSTALL_DIR/devbrain.sh" "$SHELL_RC"; then
    echo "" >> "$SHELL_RC"
    echo "# DevBrain Integration" >> "$SHELL_RC"
    echo "source $INSTALL_DIR/devbrain.sh" >> "$SHELL_RC"
fi

# Create log directories
mkdir -p "$INSTALL_DIR/logs"

echo "DevBrain has been installed successfully!"
echo "Please restart your terminal or run: source $SHELL_RC" 