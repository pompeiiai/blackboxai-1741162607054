#!/bin/bash

# Import MongoDB 7.0 public GPG key
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor

# Add MongoDB 7.0 repository (using jammy instead of noble)
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package list
sudo apt-get update

# Install MongoDB
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod

# Enable MongoDB to start on system boot
sudo systemctl enable mongod

# Verify MongoDB is running
sudo systemctl status mongod

# Create data directory if it doesn't exist
sudo mkdir -p /data/db
sudo chown -R $USER:$USER /data/db

# Note: MongoDB will be running on default port 27017
# You can verify it's running using:
mongo --eval 'db.runCommand({ connectionStatus: 1 })'

# Make sure MongoDB is running
mongod --dbpath /path/to/data/db

# Install dependencies
pip install -r requirements.txt

# Initialize database and create admin user
python init_db.py
