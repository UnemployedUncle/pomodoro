#!/bin/bash

# Pomodoro Focus App Startup Script

echo "🎯 Starting Pomodoro Focus App..."
echo "📦 Installing dependencies..."

# Install dependencies
pip3 install -r requirements.txt

echo "🚀 Starting Flask application..."
echo "🌐 Application will be available at: http://localhost:5001"
echo "📱 Open your browser and navigate to the URL above"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Start the Flask application
python3 app.py 