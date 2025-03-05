from flask import Flask
from flask_mongoengine import MongoEngine
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure MongoDB settings
app.config['MONGODB_SETTINGS'] = {
    'host': os.getenv('MONGODB_URI', 'mongodb://localhost:27017/bariatric'),
    'db': os.getenv('MONGODB_DB', 'bariatric')
}

# Initialize MongoDB
db = MongoEngine(app)

# Test connection
with app.app_context():
    try:
        # This will trigger a connection attempt
        db.connection
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")