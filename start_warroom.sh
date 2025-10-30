#!/bin/bash
# Quick start script for Real-Time War Room

echo "=================================="
echo "🐠 Starting Nemo War Room Server"
echo "=================================="
echo ""

# Check if flask-socketio is installed
if ! python -c "import flask_socketio" 2>/dev/null; then
    echo "⚠️  flask-socketio not found. Installing..."
    pip install flask-socketio
    echo ""
fi

# Check if required files exist
if [ ! -f "web_app_realtime.py" ]; then
    echo "❌ Error: web_app_realtime.py not found"
    exit 1
fi

if [ ! -f "templates/investigating_realtime.html" ]; then
    echo "❌ Error: templates/investigating_realtime.html not found"
    exit 1
fi

echo "✅ All dependencies satisfied"
echo ""
echo "🚀 Launching server..."
echo "📡 WebSocket enabled for real-time agent conversations"
echo ""
echo "🌐 Open your browser to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="
echo ""

python web_app_realtime.py
