import pytest
from flask import Flask
from models_mongo import db, User, Role

def test_user_creation():
    """Test user creation and role assignment"""
    # Create a test role
    role = Role(name='test_role', permissions=['test'])
    role.save()
    
    # Create a test user
    user = User(
        username='test_user',
        email='test@example.com',
        roles=[role]
    )
    user.set_password('password123')
    user.save()
    
    # Retrieve and verify
    saved_user = User.objects(username='test_user').first()
    assert saved_user is not None
    assert saved_user.email == 'test@example.com'
    assert saved_user.has_role('test_role')
    assert saved_user.check_password('password123')