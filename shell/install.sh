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

# Remove any old sourcing lines for devbrain.sh from the shell rc file
sed -i.bak '/devbrain\/shell\/devbrain.sh/d' "$SHELL_RC"
sed -i.bak '/\.devbrain\/devbrain.sh/d' "$SHELL_RC"

# Add to shell rc (only once)
echo "" >> "$SHELL_RC"
echo "# DevBrain Integration" >> "$SHELL_RC"
echo "source $INSTALL_DIR/devbrain.sh" >> "$SHELL_RC"

# Create log directories
mkdir -p "$INSTALL_DIR/logs"

echo "DevBrain has been installed successfully!"
echo "Please restart your terminal or run: source $SHELL_RC" 