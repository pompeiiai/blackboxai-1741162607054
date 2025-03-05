from models import db as sql_db, Role, User
from models_mongo import db as mongo_db
from werkzeug.security import generate_password_hash
import logging

logger = logging.getLogger(__name__)

def init_db(app):
    """Initialize the database and create required tables"""
    try:
        if app.config['DATABASE_TYPE'] == 'mongodb':
            # MongoDB initialization
            mongo_db.init_app(app)
            logger.info("MongoDB initialized successfully")
        else:
            # SQLAlchemy initialization
            with app.app_context():
                sql_db.create_all()
                create_default_roles()
                logger.info("SQLAlchemy database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def create_default_roles():
    """Create default roles with their permissions"""
    if not Role.query.first():  # Only create if no roles exist
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
                    'view_analytics'
                ]
            }
        }
        
        for role_name, role_data in roles.items():
            role = Role(
                name=role_name,
                description=role_data['description'],
                permissions=role_data['permissions']
            )
            sql_db.session.add(role)
        
        try:
            sql_db.session.commit()
            logger.info("Default roles created successfully")
        except Exception as e:
            sql_db.session.rollback()
            logger.error(f"Error creating default roles: {str(e)}")
            raise

def create_default_admin(username, password, email, first_name='Admin', last_name='User'):
    """Create a default super admin user if none exists"""
    if not User.query.filter_by(username=username).first():
        try:
            admin_role = Role.query.filter_by(name='super_admin').first()
            if admin_role:
                admin = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    email_verified=True
                )
                admin.set_password(password)
                admin.roles.append(admin_role)
                
                db.session.add(admin)
                db.session.commit()
                logger.info("Admin user created successfully")
            else:
                logger.error("Super admin role not found")
                raise Exception("Super admin role not found")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating admin: {str(e)}")
            raise
    else:
        raise Exception(f"User with username '{username}' already exists")

def reset_db():
    """Reset the database by dropping all tables and recreating them"""
    try:
        db.drop_all()
        db.create_all()
        logger.info("Database reset successfully")
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        raise
