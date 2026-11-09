#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.github.aki77.claude-meter"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
APP_DIR="$HOME/Applications"
APP="$APP_DIR/Claude Meter.app"

echo "Installing dependencies..."
cd "$SCRIPT_DIR"
uv sync

# Stop a running instance before replacing the bundle it runs from.
launchctl unload "$PLIST" 2>/dev/null || true

echo "Building $APP..."
mkdir -p "$APP_DIR"
"$SCRIPT_DIR/.venv/bin/python" -m claude_meter.bundle "$APP_DIR" > /dev/null

sed "s|CLAUDE_METER_APP|$APP|g" "$SCRIPT_DIR/$LABEL.plist" > "$PLIST"

launchctl load "$PLIST"

echo "claude-meter installed and started."
echo "App: $APP"
echo "Log: /tmp/claude-meter.log"
