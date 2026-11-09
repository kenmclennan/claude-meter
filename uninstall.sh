#!/bin/bash
set -e

LABEL="com.github.aki77.claude-meter"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
APP="$HOME/Applications/Claude Meter.app"

if [ -f "$PLIST" ]; then
    launchctl unload "$PLIST" 2>/dev/null || true
    rm "$PLIST"
    rm -rf "$APP"
    echo "claude-meter uninstalled."
else
    rm -rf "$APP"
    echo "claude-meter is not installed."
fi
