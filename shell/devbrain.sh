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

# Function to escape JSON strings
escape_json() {
    printf '%s' "$1" | sed 's/["\\]/\\&/g' | tr '\n' 'n' | sed 's/n/\\n/g'
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
    git_branch=$(get_git_branch | tr -d '\n')  # Remove newline from git branch

    # Simple JSON escaping
    command=$(printf '%s' "$command" | sed 's/"/\\"/g')
    directory=$(printf '%s' "$directory" | sed 's/"/\\"/g')
    git_branch=$(printf '%s' "$git_branch" | sed 's/"/\\"/g')

    local json_data
    json_data=$(cat <<EOF
{
"command": "$command",
"timestamp": "$timestamp",
"directory": "$directory",
"git_branch": "$git_branch",
"tags": []
}
EOF
)

    (
        curl -s -X POST "$DEVBRAIN_API_URL/commands" \
            -H "Content-Type: application/json" \
            -d "$json_data" \
            >/dev/null 2>> "$DEVBRAIN_ERROR_LOG"
    ) &
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

# Natural language command search
devbrain_ask() {
    local query="$1"
    if [ -z "$query" ]; then
        echo "Usage: devbrain_ask \"<your question>\""
        return 1
    fi

    curl -s -G --data-urlencode "query=$query" "$DEVBRAIN_API_URL/commands/natural-search" | \
    python3 -c '
import json, sys
data = json.load(sys.stdin)
if data.get("status") == "success":
    message = data.get("message", "")
    command = data.get("command", "")
    
    # Print the full explanation
    print("\n\033[1;32mExplanation:\033[0m")
    print(message)
    
    # Print the command in a copy-paste friendly format
    if command:
        print("\n\033[1;34mCommand to run:\033[0m")
        print(f"\033[1;33m{command}\033[0m")
    else:
        print("\033[1;31mError:\033[0m " + data.get("detail", "Unknown error"))
'
}

# Generate commit message based on changes
devbrain_commit() {
    local directory
    directory=$(pwd)
    
    # Get commit message from API
    local response
    response=$(curl -s -G --data-urlencode "directory=$directory" "$DEVBRAIN_API_URL/git/commit-message")
    
    # Parse response using Python
    local message
    message=$(echo "$response" | python3 -c '
import json, sys
data = json.load(sys.stdin)
if data.get("status") == "success":
    print(data.get("message", ""))
else:
    print("Error: " + data.get("detail", "Unknown error"))
    sys.exit(1)
')
    
    if [ $? -eq 0 ]; then
        echo -e "\033[1;32mSuggested commit message:\033[0m"
        echo -e "\033[1;34m$message\033[0m"
        
        # Show changes
        echo "$response" | python3 -c '
import json, sys
data = json.load(sys.stdin)
changes = data.get("changes", [])
for change in changes:
    color = "\033[1;33m"  # Yellow for modified
    if change["change_type"] == "added":
        color = "\033[1;32m"  # Green for added
    elif change["change_type"] == "deleted":
        color = "\033[1;31m"  # Red for deleted
    change_type = change["change_type"].upper()
    file_path = change["file_path"]
    print(f"{color}{change_type}\033[0m {file_path}")
'
        
        # Ask if user wants to commit with this message
        echo -e "\n\033[1;33mDo you want to commit with this message? (y/N)\033[0m"
        read -r answer
        if [[ "$answer" =~ ^[Yy]$ ]]; then
            git commit -m "$message"
        fi
    else
        echo "$message"
    fi
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
export -f devbrain_ask
export -f devbrain_toggle
export -f devbrain_commit