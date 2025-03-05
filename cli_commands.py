from flask.cli import with_appcontext
import click
import json
from database import init_db, create_default_roles, create_default_admin
from models import db, SurgeryType, DietPlan

def register_commands(app):
    @app.cli.command('init')
    @with_appcontext
    def init_db_command():
        """Initialize the database."""
        init_db(app)
        click.echo('Database initialized.')

    @app.cli.command('create-admin')
    @with_appcontext
    @click.option('--username', prompt=True, help='Admin username')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
    @click.option('--email', prompt=True, help='Admin email')
    @click.option('--first-name', prompt=True, help='Admin first name', default='Admin')
    @click.option('--last-name', prompt=True, help='Admin last name', default='User')
    def create_admin(username, password, email, first_name, last_name):
        """Create an admin user."""
        try:
            create_default_admin(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            click.echo('Admin user created successfully.')
        except Exception as e:
            click.echo(f'Error creating admin: {str(e)}', err=True)

    @app.cli.command('import-surgery-types')
    @with_appcontext
    @click.argument('config_file', type=click.Path(exists=True))
    def import_surgery_types(config_file):
        """Import surgery types from JSON configuration file."""
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
            
            # Access the surgery_types list from the JSON
            surgery_types = data.get('surgery_types', [])
            
            for surgery_data in surgery_types:
                surgery = SurgeryType(
                    name=surgery_data['name'],
                    description=surgery_data['description'],
                    requirements=surgery_data['requirements'],
                    preop_instructions=surgery_data.get('preop_instructions', {}),
                    postop_instructions=surgery_data.get('postop_instructions', {}),
                    risks=surgery_data.get('risks', []),
                    cost_range=surgery_data.get('cost_range', ''),
                    recovery_time=surgery_data.get('recovery_time', '')
                )
                db.session.add(surgery)
            
            db.session.commit()
            click.echo('Surgery types imported successfully.')
        except Exception as e:
            db.session.rollback()
            click.echo(f'Error importing surgery types: {str(e)}', err=True)

    @app.cli.command('import-diet-plans')
    @with_appcontext
    @click.argument('config_file', type=click.Path(exists=True))
    def import_diet_plans(config_file):
        """Import diet plans from JSON configuration file."""
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
            
            # Access the diet_plans list from the JSON
            diet_plans = data.get('diet_plans', [])
            
            for plan_data in diet_plans:
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
