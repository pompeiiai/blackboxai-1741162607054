from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association tables for many-to-many relationships
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment',
                                 foreign_keys='Appointment.patient_id',
                                 backref='patient',
                                 lazy='dynamic')
    
    doctor_appointments = db.relationship('Appointment',
                                        foreign_keys='Appointment.doctor_id',
                                        backref='doctor',
                                        lazy='dynamic')
    
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    
    medical_records = db.relationship('MedicalRecord', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission):
        return any(permission in role.permissions for role in self.roles if role.permissions)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            Config.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, Config.SECRET_KEY,
                          algorithms=['HS256'])['reset_password']
        except:
            return None
        return User.query.get(id)

    def __repr__(self):
        return f'<User {self.username}>'

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    intent = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)
    feedback = db.Column(db.Boolean, default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatHistory {self.id}>'

class Appointment(db.Model):
    __tablename__ = 'appointment'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Appointment {self.id}: Patient {self.patient_id} with Doctor {self.doctor_id}>'

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    bmi = db.Column(db.Float)
    medical_conditions = db.Column(db.JSON)
    medications = db.Column(db.JSON)
    allergies = db.Column(db.JSON)
    surgery_history = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MedicalRecord {self.id}>'

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))

    def __repr__(self):
        return f'<AuditLog {self.id}>'

class SurgeryType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    requirements = db.Column(db.JSON)
    preop_instructions = db.Column(db.JSON)
    postop_instructions = db.Column(db.JSON)
    risks = db.Column(db.JSON)
    cost_range = db.Column(db.JSON)
    recovery_time = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SurgeryType {self.name}>'

class DietPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surgery_type_id = db.Column(db.Integer, db.ForeignKey('surgery_type.id'))
    phase = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50))
    allowed_foods = db.Column(db.JSON)
    restricted_foods = db.Column(db.JSON)
    guidelines = db.Column(db.JSON)
    supplements = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    surgery_type = db.relationship('SurgeryType', backref=db.backref('diet_plans', lazy='dynamic'))

    def __repr__(self):
        return f'<DietPlan {self.phase} for {self.surgery_type.name}>'
