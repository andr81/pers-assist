#!/bin/bash

# Script to help set up SINGULARITY_API_TOKEN for testing

echo "=== Singularity MCP Token Setup ==="
echo ""

# Check if token is already set
if [ -n "$SINGULARITY_API_TOKEN" ]; then
    echo "✓ SINGULARITY_API_TOKEN is already set (length: ${#SINGULARITY_API_TOKEN})"
    echo ""
    echo "You can run tests with:"
    echo "  python test_tags.py"
    exit 0
fi

# Try to find token in common locations
echo "Looking for token in common locations..."

# Check Claude config
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
if [ -f "$CLAUDE_CONFIG" ]; then
    echo "Found Claude config at: $CLAUDE_CONFIG"
    TOKEN=$(python3 -c "
import json
with open('$CLAUDE_CONFIG') as f:
    config = json.load(f)
    servers = config.get('mcpServers', {})
    singularity = servers.get('singularity', {})
    env = singularity.get('env', {})
    token = env.get('SINGULARITY_API_TOKEN', '')
    print(token)
" 2>/dev/null)

    if [ -n "$TOKEN" ]; then
        echo "✓ Found token in Claude config!"
        echo ""
        echo "To use the token for testing, run:"
        echo "  export SINGULARITY_API_TOKEN='$TOKEN'"
        echo "  python test_tags.py"
        exit 0
    fi
fi

echo ""
echo "Token not found. To get your token:"
echo "1. Go to https://me.singularity-app.com"
echo "2. Log in to your account"
echo "3. Navigate to API settings or integrations"
echo "4. Copy your API token"
echo ""
echo "Then set it with:"
echo "  export SINGULARITY_API_TOKEN='your-token-here'"
echo ""
echo "Or add it to your Claude Desktop config at:"
echo "  ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "Example config:"
echo '
{
  "mcpServers": {
    "singularity": {
      "command": "uv",
      "args": ["--directory", "'$PWD'", "run", "singularity-mcp"],
      "env": {
        "SINGULARITY_API_TOKEN": "your-token-here"
      }
    }
  }
}
'