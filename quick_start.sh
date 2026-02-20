#!/bin/bash
# Quick Start Script for Situational Awareness System

echo "======================================"
echo "SAS - Quick Start Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Install dependencies
echo ""
echo "Installing required packages..."
pip install -q opencv-python-headless flask requests pandas numpy skyfield folium geopandas shapely scipy Pillow transformers torch torchvision

echo ""
echo "======================================"
echo "Installation complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Test cameras:    python test_cameras.py"
echo "2. Run application: python web_app.py"
echo "3. Open browser:    http://localhost:5000"
echo ""
echo "======================================"
