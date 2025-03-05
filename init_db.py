from flask import Flask
from models_mongo import db, User, Role
from config import config
import click

app = Flask(__name__)
app.config.from_object(config['development'])
db.init_app(app)

def init_roles():
    """Initialize default roles"""
    roles = {
        'super_admin': ['all'],
        'doctor': ['view_patients', 'manage_appointments', 'view_medical_records'],
        'staff': ['view_appointments', 'basic_patient_info'],
        'patient': ['view_own_records', 'schedule_appointments']
    }
    
    for role_name, permissions in roles.items():
        if not Role.objects(name=role_name).first():
            role = Role(
                name=role_name,
                permissions=permissions
            )
            role.save()
            click.echo(f'Created role: {role_name}')

def create_admin(email, password):
    """Create admin user"""
    if User.objects(email=email).first():
        click.echo('Admin user already exists')
        return
    
    admin_role = Role.objects(name='super_admin').first()
    if not admin_role:
        click.echo('Error: super_admin role not found')
        return
    
    admin = User(
        username='admin',
        email=email,
        first_name='Admin',
        last_name='User',
        email_verified=True,
        roles=[admin_role]
    )
    admin.set_password(password)
    admin.save()
    click.echo('Admin user created successfully')

@click.command()
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
def init_db(email, password):
    """Initialize the database with roles and admin user"""
    with app.app_context():
        init_roles()
        create_admin(email, password)

if __name__ == '__main__':
    init_db()


