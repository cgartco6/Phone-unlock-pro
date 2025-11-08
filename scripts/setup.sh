#!/bin/bash

echo "Setting up Phone Unlock AI System..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install AI model dependencies
pip install -r ai_models/phone_detection/requirements.txt
pip install -r ai_models/unlock_recommender/requirements.txt

# Initialize database
python database/init_db.py

# Download pre-trained models (if available)
echo "Downloading AI models..."
wget -O ai_models/phone_detection/model.pth "https://example.com/models/phone_detection.pth"
wget -O ai_models/unlock_recommender/model.joblib "https://example.com/models/unlock_recommender.joblib"

echo "Setup complete!"
echo "Start the application with: python backend/app.py"
