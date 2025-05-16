#!/bin/bash

# DevBrain Shell Integration
# This script captures terminal commands and sends them to the DevBrain API

# Configuration
DEVBRAIN_API_URL="http://localhost:8000"
DEVBRAIN_LOG_DIR="$HOME/.devbrain/logs"
DEVBRAIN_LOG_FILE="$DEVBRAIN_LOG_DIR/commands.log"
DEVBRAIN_ERROR_LOG="$DEVBRAIN_LOG_DIR/error.log"
DEVBRAIN_ENABLED=true  # Toggle with devbrain_toggle

# Ensure log directories exist
mkdir -p "$DEVBRAIN_LOG_DIR"

# Function to get current Git branch
get_git_branch() {
    git rev-parse --abbrev-ref HEAD 2>/dev/null
}

# Function to send the command to the API
log_command() {
    [ "$DEVBRAIN_ENABLED" = false ] && return

    local command="$1"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local directory
    directory=$(pwd | sed 's/^\/Users\/[^/]*/~/')
    local git_branch
    git_branch=$(get_git_branch)

    # Escape for JSON
    local escaped_command
    escaped_command=$(echo "$command" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])')
    local escaped_directory
    escaped_directory=$(echo "$directory" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])')
    local escaped_git_branch
    escaped_git_branch=$(echo "$git_branch" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])')

    local payload
    payload=$(cat <<EOF
{
    "command": "$escaped_command",
    "timestamp": "$timestamp",
    "directory": "$escaped_directory",
    "git_branch": "$escaped_git_branch",
    "tags": []
}
EOF
)

    (curl -s -X POST "$DEVBRAIN_API_URL/commands" \
        -H "Content-Type: application/json" \
        -d "$payload" >> "$DEVBRAIN_LOG_FILE" 2>> "$DEVBRAIN_ERROR_LOG") &
}

# Pre-execution hook
preexec() {
    # Skip logging if this is a devbrain command
    if [[ "$1" == devbrain_* ]]; then
        return
    fi
    DEVBRAIN_LAST_COMMAND="$1"
}

# Pre-prompt hook
precmd() {
    if [ -n "$DEVBRAIN_LAST_COMMAND" ]; then
        log_command "$DEVBRAIN_LAST_COMMAND"
        DEVBRAIN_LAST_COMMAND=""  # Clear the command after logging
    fi
}

# Shell integration
if [ -n "$ZSH_VERSION" ]; then
    autoload -U add-zsh-hook
    add-zsh-hook preexec preexec
    add-zsh-hook precmd precmd
elif [ -n "$BASH_VERSION" ]; then
    trap 'preexec "$BASH_COMMAND"' DEBUG
    PROMPT_COMMAND="precmd; $PROMPT_COMMAND"
fi

# Search function
devbrain_search() {
    local query="$1"
    if [ -z "$query" ]; then
        echo "Usage: devbrain_search \"<query>\""
        return 1
    fi

    curl -s -G --data-urlencode "query=$query" "$DEVBRAIN_API_URL/commands/search" | \
    python3 -c '
import json, sys
data = json.load(sys.stdin)
results = data.get("results", [])
if not results:
    print("No results found.")
else:
    for cmd in results:
        print("\n\033[1;34mCommand:\033[0m " + cmd.get("command", ""))
        print("\033[1;33mDirectory:\033[0m " + cmd.get("directory", ""))
        if cmd.get("git_branch"):
            print("\033[1;35mGit Branch:\033[0m " + cmd.get("git_branch", ""))
        print("\033[1;36mTime:\033[0m " + cmd.get("timestamp", ""))
        print("-" * 80)
'
}

# Toggle logging on/off
devbrain_toggle() {
    if [ "$DEVBRAIN_ENABLED" = true ]; then
        DEVBRAIN_ENABLED=false
        echo "DevBrain logging disabled"
    else
        DEVBRAIN_ENABLED=true
        echo "DevBrain logging enabled"
    fi
}

# Export utility functions
export -f devbrain_search
export -f devbrain_toggle