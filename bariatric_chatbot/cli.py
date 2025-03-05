import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
import json
import logging
from datetime import datetime

from models import db, User, Role, SurgeryType, DietPlan
from database import init_db, create_default_roles

logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Bariatric Surgery Assistant CLI commands."""
    pass

@cli.command()
@with_appcontext
def init():
    """Initialize the database."""
    try:
        init_db()
        click.echo('Database initialized successfully.')
    except Exception as e:
        click.echo(f'Error initializing database: {str(e)}', err=True)

@cli.command()
@with_appcontext
@click.option('--username', prompt=True, help='Admin username')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@click.option('--first-name', prompt=True, help='Admin first name')
@click.option('--last-name', prompt=True, help='Admin last name')
def create_admin(username, email, password, first_name, last_name):
    """Create a new admin user."""
    try:
        # Check if super_admin role exists
        admin_role = Role.query.filter_by(name='super_admin').first()
        if not admin_role:
            click.echo('Creating default roles first...')
            create_default_roles()
            admin_role = Role.query.filter_by(name='super_admin').first()

        # Create admin user
        admin = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=generate_password_hash(password),
            email_verified=True,
            is_active=True
        )
        admin.roles.append(admin_role)
        
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Admin user {username} created successfully.')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error creating admin user: {str(e)}', err=True)

@cli.command()
@with_appcontext
@click.argument('config_file', type=click.Path(exists=True))
def import_surgery_types(config_file):
    """Import surgery types from JSON configuration file."""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        for surgery_data in config:
            surgery = SurgeryType(
                name=surgery_data['name'],
                description=surgery_data['description'],
                requirements=surgery_data['requirements'],
                preop_instructions=surgery_data.get('preop_instructions', {}),
                postop_instructions=surgery_data.get('postop_instructions', {}),
                risks=surgery_data['risks'],
                cost_range=surgery_data['cost_range'],
                recovery_time=surgery_data['recovery_time']
            )
            db.session.add(surgery)
        
        db.session.commit()
        click.echo('Surgery types imported successfully.')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error importing surgery types: {str(e)}', err=True)

@cli.command()
@with_appcontext
@click.argument('config_file', type=click.Path(exists=True))
def import_diet_plans(config_file):
    """Import diet plans from JSON configuration file."""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        for plan_data in config:
            surgery_type = SurgeryType.query.filter_by(name=plan_data['surgery_type']).first()
            if not surgery_type:
                click.echo(f"Surgery type {plan_data['surgery_type']} not found, skipping...")
                continue
            
            plan = DietPlan(
                surgery_type_id=surgery_type.id,
                phase=plan_data['phase'],
                duration=plan_data['duration'],
                allowed_foods=plan_data['allowed_foods'],
                restricted_foods=plan_data['restricted_foods'],
                guidelines=plan_data['guidelines'],
                supplements=plan_data.get('supplements', {})
            )
            db.session.add(plan)
        
        db.session.commit()
        click.echo('Diet plans imported successfully.')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error importing diet plans: {str(e)}', err=True)

@cli.command()
@with_appcontext
def list_users():
    """List all users in the system."""
    try:
        users = User.query.all()
        if not users:
            click.echo('No users found.')
            return
        
        click.echo('\nUser List:')
        click.echo('-' * 80)
        click.echo(f"{'ID':<5} {'Username':<15} {'Email':<25} {'Roles':<20} {'Status':<10}")
        click.echo('-' * 80)
        
        for user in users:
            roles = ', '.join(role.name for role in user.roles)
            status = 'Active' if user.is_active else 'Inactive'
            click.echo(f"{user.id:<5} {user.username:<15} {user.email:<25} {roles:<20} {status:<10}")
    except Exception as e:
        click.echo(f'Error listing users: {str(e)}', err=True)

@cli.command()
@with_appcontext
@click.argument('username')
def deactivate_user(username):
    """Deactivate a user account."""
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            click.echo(f'User {username} not found.')
            return
        
        user.is_active = False
        db.session.commit()
        click.echo(f'User {username} has been deactivated.')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error deactivating user: {str(e)}', err=True)

@cli.command()
@with_appcontext
@click.argument('username')
def activate_user(username):
    """Activate a user account."""
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            click.echo(f'User {username} not found.')
            return
        
        user.is_active = True
        db.session.commit()
        click.echo(f'User {username} has been activated.')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error activating user: {str(e)}', err=True)

@cli.command()
@with_appcontext
def cleanup_expired_tokens():
    """Clean up expired password reset tokens."""
    try:
        # This assumes you have a Token model or similar
        from models import Token
        expired = Token.query.filter(Token.expires_at < datetime.utcnow()).delete()
        db.session.commit()
        click.echo(f'Cleaned up {expired} expired tokens.')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error cleaning up tokens: {str(e)}', err=True)

@cli.command()
@with_appcontext
def export_config():
    """Export current surgery types and diet plans configuration."""
    try:
        surgery_types = SurgeryType.query.all()
        diet_plans = DietPlan.query.all()
        
        config = {
            'surgery_types': [
                {
                    'name': st.name,
                    'description': st.description,
                    'requirements': st.requirements,
                    'preop_instructions': st.preop_instructions,
                    'postop_instructions': st.postop_instructions,
                    'risks': st.risks,
                    'cost_range': st.cost_range,
                    'recovery_time': st.recovery_time
                }
                for st in surgery_types
            ],
            'diet_plans': [
                {
                    'surgery_type': dp.surgery_type.name,
                    'phase': dp.phase,
                    'duration': dp.duration,
                    'allowed_foods': dp.allowed_foods,
                    'restricted_foods': dp.restricted_foods,
                    'guidelines': dp.guidelines,
                    'supplements': dp.supplements
                }
                for dp in diet_plans
            ]
        }
        
        with open('config_export.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        click.echo('Configuration exported to config_export.json')
    except Exception as e:
        click.echo(f'Error exporting configuration: {str(e)}', err=True)

if __name__ == '__main__':
    cli()
