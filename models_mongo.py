from flask_mongoengine import MongoEngine
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

db = MongoEngine()

class Role(db.Document):
    name = db.StringField(required=True, unique=True)
    permissions = db.ListField(db.StringField(), default=[])
    description = db.StringField()
    created_at = db.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'roles',
        'ordering': ['name']
    }

    def __str__(self):
        return self.name

class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.StringField(required=True, unique=True)
    email_verified = db.BooleanField(default=False)
    password_hash = db.StringField(required=True)
    first_name = db.StringField(required=True)
    last_name = db.StringField(required=True)
    roles = db.ListField(db.ReferenceField(Role), default=[])
    is_active = db.BooleanField(default=True)
    created_at = db.DateTimeField(default=datetime.utcnow)
    last_login = db.DateTimeField()

    meta = {
        'collection': 'users',
        'ordering': ['-created_at']
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class ChatHistory(db.Document):
    user = db.ReferenceField('User', required=True)
    message = db.StringField(required=True)
    response = db.StringField(required=True)
    intent = db.StringField()
    confidence_score = db.FloatField()
    created_at = db.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'chat_history',
        'ordering': ['-created_at']
    }

    def __str__(self):
        return f"Chat: {self.user.username} - {self.created_at}"
