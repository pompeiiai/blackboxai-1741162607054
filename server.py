from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os

from config import config
from models_mongo import db, User, Role, ChatHistory
from utils.chatbot_logic import process_message
from decorators.role_required import role_required, permission_required, admin_required, super_admin_required
from forms import RegistrationForm, LoginForm

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize MongoDB
db.init_app(app)

# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()

# Main routes
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('welcome.html')
    return render_template('chat.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.objects(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                user.update_last_login()
                
                # Get the next page from args, or default to index
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('index')
                return redirect(next_page)
            else:
                flash('Invalid email or password', 'error')
                app.logger.warning(f'Failed login attempt for email: {form.email.data}')
        except Exception as e:
            app.logger.error(f'Login error: {str(e)}')
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            user.set_password(form.password.data)
            user.save()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
            app.logger.error(f'Registration error: {str(e)}')
    
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    chat_history = ChatHistory.objects(user=current_user.id).order_by('-created_at')
    return render_template('dashboard.html', chat_history=chat_history)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    if not current_user.is_authenticated:
        return jsonify({
            'error': 'Authentication required',
            'redirect': url_for('login')
        }), 401
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        response = process_message(data['message'])
        
        chat_history = ChatHistory(
            user=current_user.id,
            message=data['message'],
            response=response['message'],
            intent=response.get('intent'),
            confidence_score=response.get('confidence')
        )
        chat_history.save()
        
        return jsonify(response)
    except Exception as e:
        app.logger.error(f'Error processing chat message: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.has_role('admin'):
        return redirect(url_for('index'))
    
    stats = {
        'total_users': User.objects.count(),
        'total_chats': ChatHistory.objects.count(),
        'recent_activities': ChatHistory.objects.order_by('-created_at').limit(10)
    }
    return render_template('admin/dashboard.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
