from flask import Flask
from models_mongo import db, User

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost:27017/bariatric_assistant'
}
db.init_app(app)

with app.app_context():
    # Check if test user exists
    test_user = User.objects(email='test@example.com').first()
    if not test_user:
        user = User(
            email='test@example.com',
            username='testuser'
        )
        user.set_password('password123')
        user.save()
        print("Test user created successfully")
    else:
        print("Test user already exists")