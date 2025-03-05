from models import db, Role, User
from werkzeug.security import generate_password_hash
import logging

logger = logging.getLogger(__name__)

def init_db(app):
    """Initialize the database and create required tables"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Create default roles if they don't exist
            create_default_roles()
            
            # Create default super admin if it doesn't exist
            create_default_admin()
            
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def create_default_roles():
    """Create default roles with their permissions"""
    roles = {
        'super_admin': {
            'description': 'Super Administrator with full system access',
            'permissions': ['all']
        },
        'admin': {
            'description': 'Administrator with management access',
            'permissions': [
                'manage_users',
                'manage_content',
                'view_analytics',
                'manage_appointments',
                'manage_doctors',
                'view_audit_logs'
            ]
        },
        'doctor': {
            'description': 'Medical professional',
            'permissions': [
                'view_patients',
                'manage_appointments',
                'view_medical_records',
                'update_patient_status'
            ]
        },
        'staff': {
            'description': 'General staff member',
            'permissions': [
                'view_appointments',
                'basic_patient_info',
                'update_appointment_status'
            ]
        },
        'content_manager': {
            'description': 'Manages chatbot content and responses',
            'permissions': [
                'manage_chatbot_content',
                'view_chat_analytics'
            ]
        }
    }
    
    for role_name, role_data in roles.items():
        if not Role.query.filter_by(name=role_name).first():
            role = Role(
                name=role_name,
                description=role_data['description'],
                permissions=role_data['permissions']
            )
            db.session.add(role)
    
    try:
        db.session.commit()
        logger.info("Default roles created successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating default roles: {str(e)}")
        raise

def create_default_admin():
    """Create a default super admin user if none exists"""
    if not User.query.filter_by(username='admin').first():
        try:
            admin_role = Role.query.filter_by(name='super_admin').first()
            if admin_role:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    first_name='System',
                    last_name='Administrator',
                    email_verified=True
                )
                admin.set_password('admin123')  # This should be changed immediately
                admin.roles.append(admin_role)
                
                db.session.add(admin)
                db.session.commit()
                logger.info("Default admin user created successfully")
            else:
                logger.error("Super admin role not found")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating default admin: {str(e)}")
            raise

def reset_db():
    """Reset the database by dropping all tables and recreating them"""
    try:
        db.drop_all()
        db.create_all()
        logger.info("Database reset successfully")
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        raise
