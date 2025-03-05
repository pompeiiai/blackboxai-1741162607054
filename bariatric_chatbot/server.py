from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os

from config import config
from models import db, User, Role, ChatHistory, Appointment, MedicalRecord, AuditLog
from database import init_db
from decorators.role_required import admin_required, role_required, permission_required
from utils.chatbot_logic import process_message

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Setup logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/bariatric_chatbot.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Bariatric Chatbot startup')

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log the login
        log = AuditLog(
            user_id=user.id,
            action='login',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Log the logout
    log = AuditLog(
        user_id=current_user.id,
        action='logout',
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    logout_user()
    return redirect(url_for('index'))

# User routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_id = current_user.id if current_user.is_authenticated else None
        response = process_message(data['message'])
        
        # Save chat history if user is authenticated
        if user_id:
            chat_history = ChatHistory(
                user_id=user_id,
                message=data['message'],
                response=response['message'],
                intent=response.get('intent'),
                confidence_score=response.get('confidence')
            )
            db.session.add(chat_history)
            db.session.commit()
        
        return jsonify(response)
    except Exception as e:
        app.logger.error(f'Error processing chat message: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

# Admin routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_chats': ChatHistory.query.count(),
        'total_appointments': Appointment.query.count(),
        'recent_activities': AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
    }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/users')
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'])
    roles = Role.query.all()
    return render_template('admin/users.html', users=users, roles=roles)

@app.route('/admin/roles')
@role_required('super_admin')
def admin_roles():
    roles = Role.query.all()
    return render_template('admin/roles.html', roles=roles)

@app.route('/admin/audit-logs')
@permission_required('view_audit_logs')
def admin_audit_logs():
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=app.config['ITEMS_PER_PAGE']
    )
    return render_template('admin/audit_logs.html', logs=logs)

@app.route('/admin/appointments')
@permission_required('manage_appointments')
def admin_appointments():
    page = request.args.get('page', 1, type=int)
    appointments = Appointment.query.order_by(Appointment.scheduled_time.desc()).paginate(
        page=page, per_page=app.config['ITEMS_PER_PAGE']
    )
    return render_template('admin/appointments.html', appointments=appointments)

# API routes for AJAX calls
@app.route('/api/user/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'roles' in data:
            # Clear existing roles
            user.roles = []
            # Add new roles
            for role_id in data['roles']:
                role = Role.query.get(role_id)
                if role:
                    user.roles.append(role)
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        
        # Log the action
        log = AuditLog(
            user_id=current_user.id,
            action='update_user',
            details={'target_user_id': user_id, 'changes': data},
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error updating user: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointment/<int:appointment_id>', methods=['PUT'])
@permission_required('manage_appointments')
def update_appointment(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.get_json()
        
        if 'status' in data:
            appointment.status = data['status']
        if 'notes' in data:
            appointment.notes = data['notes']
        
        db.session.commit()
        
        # Log the action
        log = AuditLog(
            user_id=current_user.id,
            action='update_appointment',
            details={'appointment_id': appointment_id, 'changes': data},
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'Appointment updated successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error updating appointment: {str(e)}')
        return jsonify({'error': str(e)}), 500

# Initialize database
with app.app_context():
    init_db(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
