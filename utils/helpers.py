from flask import current_app
from flask_mail import Message, Mail
from threading import Thread
from datetime import datetime, timedelta
import jwt
import json
import logging
from functools import wraps
import pytz

mail = Mail()
logger = logging.getLogger(__name__)

def async_task(f):
    """Decorator to run a function asynchronously"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        Thread(target=f, args=args, kwargs=kwargs).start()
    return wrapped

@async_task
def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
            logger.info(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")

def send_email(subject, recipients, text_body, html_body=None, sender=None):
    """Send email wrapper"""
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=text_body,
            html=html_body,
            sender=sender or current_app.config['MAIL_DEFAULT_SENDER']
        )
        send_async_email(current_app._get_current_object(), msg)
        return True
    except Exception as e:
        logger.error(f"Error preparing email: {str(e)}")
        return False

def send_password_reset_email(user):
    """Send password reset email"""
    token = user.get_reset_password_token()
    send_email(
        subject='Reset Your Password',
        recipients=[user.email],
        text_body=f'''To reset your password, visit the following link:
{url_for('reset_password', token=token, _external=True)}

If you did not request a password reset, simply ignore this email.
''',
        html_body=render_template('email/reset_password.html',
                                user=user, token=token)
    )

def send_appointment_confirmation(appointment):
    """Send appointment confirmation email"""
    send_email(
        subject='Appointment Confirmation',
        recipients=[appointment.user.email],
        text_body=f'''Your appointment has been confirmed for {appointment.scheduled_time.strftime('%B %d, %Y at %I:%M %p')}

Details:
Doctor: Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}
Type: {appointment.appointment_type}
Status: {appointment.status}

Please arrive 15 minutes before your scheduled time.
''',
        html_body=render_template('email/appointment_confirmation.html',
                                appointment=appointment)
    )

def send_appointment_reminder(appointment):
    """Send appointment reminder email"""
    send_email(
        subject='Appointment Reminder',
        recipients=[appointment.user.email],
        text_body=f'''Reminder: You have an appointment tomorrow at {appointment.scheduled_time.strftime('%I:%M %p')}

Details:
Doctor: Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}
Type: {appointment.appointment_type}

Please arrive 15 minutes before your scheduled time.
''',
        html_body=render_template('email/appointment_reminder.html',
                                appointment=appointment)
    )

def format_datetime(value, format='medium'):
    """Format datetime based on specified format"""
    if format == 'full':
        format = "EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format = "EE dd.MM.y HH:mm"
    elif format == 'short':
        format = 'dd.MM.y'
    return value.strftime(format)

def to_local_time(utc_dt, timezone='UTC'):
    """Convert UTC datetime to local timezone"""
    local_tz = pytz.timezone(timezone)
    local_dt = utc_dt.replace(tzinfo=pytz.UTC).astimezone(local_tz)
    return local_dt

def generate_appointment_slots(doctor_id, date):
    """Generate available appointment slots for a given doctor and date"""
    from models import Appointment
    
    # Define working hours (9 AM to 5 PM)
    start_hour = 9
    end_hour = 17
    slot_duration = 30  # minutes
    
    # Get all appointments for the doctor on the given date
    existing_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.scheduled_time >= date.replace(hour=start_hour, minute=0),
        Appointment.scheduled_time <= date.replace(hour=end_hour, minute=0)
    ).all()
    
    # Generate all possible slots
    slots = []
    current_time = date.replace(hour=start_hour, minute=0)
    end_time = date.replace(hour=end_hour, minute=0)
    
    while current_time <= end_time:
        slot = {
            'time': current_time,
            'available': True
        }
        
        # Check if slot is already booked
        for appointment in existing_appointments:
            if appointment.scheduled_time == current_time:
                slot['available'] = False
                break
        
        slots.append(slot)
        current_time += timedelta(minutes=slot_duration)
    
    return slots

def format_phone_number(phone):
    """Format phone number to consistent format"""
    if not phone:
        return None
    
    # Remove all non-numeric characters
    cleaned = ''.join(filter(str.isdigit, phone))
    
    # Format as (XXX) XXX-XXXX for US numbers
    if len(cleaned) == 10:
        return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
    
    return cleaned

def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI given weight in kg and height in cm"""
    if not weight_kg or not height_cm:
        return None
    
    height_m = height_cm / 100
    bmi = weight_kg / (height_m * height_m)
    return round(bmi, 1)

def is_eligible_for_surgery(bmi, age, conditions=None):
    """
    Check if patient is eligible for bariatric surgery
    
    Args:
        bmi (float): Patient's BMI
        age (int): Patient's age
        conditions (list): List of medical conditions
    
    Returns:
        tuple: (is_eligible, reasons)
    """
    reasons = []
    is_eligible = True
    
    # Check BMI requirements
    if bmi < 35:
        is_eligible = False
        reasons.append("BMI must be 35 or higher")
    
    # Check age requirements
    if age < 18:
        is_eligible = False
        reasons.append("Must be 18 or older")
    elif age > 65:
        reasons.append("Age over 65 requires additional evaluation")
    
    # Check medical conditions
    if conditions:
        high_risk_conditions = [
            'uncontrolled_diabetes',
            'severe_heart_disease',
            'active_cancer'
        ]
        
        for condition in conditions:
            if condition in high_risk_conditions:
                is_eligible = False
                reasons.append(f"Medical condition {condition} requires clearance")
    
    return (is_eligible, reasons)

def generate_diet_plan(surgery_type, phase):
    """Generate diet plan based on surgery type and recovery phase"""
    from models import DietPlan
    
    diet_plan = DietPlan.query.filter_by(
        surgery_type=surgery_type,
        phase=phase
    ).first()
    
    if not diet_plan:
        return None
    
    return {
        'allowed_foods': diet_plan.allowed_foods,
        'restricted_foods': diet_plan.restricted_foods,
        'guidelines': diet_plan.guidelines,
        'supplements': diet_plan.supplements
    }

def log_audit(user_id, action, details, ip_address=None):
    """Log audit entry"""
    from models import AuditLog, db
    
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()
        logger.info(f"Audit log created: {action} by user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")
        db.session.rollback()
        return False

def sanitize_json(obj):
    """Sanitize object for JSON serialization"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return {k: sanitize_json(v) for k, v in obj.__dict__.items()
                if not k.startswith('_')}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    return obj

def format_currency(amount):
    """Format currency amount"""
    try:
        return "${:,.2f}".format(float(amount))
    except (ValueError, TypeError):
        return amount

def get_upcoming_appointments(days=7):
    """Get upcoming appointments within specified days"""
    from models import Appointment
    
    end_date = datetime.utcnow() + timedelta(days=days)
    return Appointment.query.filter(
        Appointment.scheduled_time > datetime.utcnow(),
        Appointment.scheduled_time <= end_date,
        Appointment.status != 'cancelled'
    ).order_by(Appointment.scheduled_time).all()

def get_appointment_statistics():
    """Get appointment statistics"""
    from models import Appointment
    from sqlalchemy import func
    
    now = datetime.utcnow()
    stats = {
        'total': Appointment.query.count(),
        'today': Appointment.query.filter(
            func.date(Appointment.scheduled_time) == func.date(now)
        ).count(),
        'upcoming': Appointment.query.filter(
            Appointment.scheduled_time > now,
            Appointment.status != 'cancelled'
        ).count(),
        'completed': Appointment.query.filter_by(status='completed').count(),
        'cancelled': Appointment.query.filter_by(status='cancelled').count()
    }
    
    return stats
