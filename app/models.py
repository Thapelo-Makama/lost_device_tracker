from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    id_number = db.Column(db.String(30))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)   # admin must approve
    is_banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.Text)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    devices = db.relationship('Device', backref='owner', lazy=True, cascade='all, delete-orphan')
    evidences = db.relationship('Evidence', backref='user', lazy=True, cascade='all, delete-orphan', foreign_keys='Evidence.user_id')

    def set_password(self, p): self.password_hash = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password_hash, p)
    def unread_count(self):
        return Message.query.filter_by(recipient_id=self.id, is_read=False).count()

class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50))
    imei_number = db.Column(db.String(30), index=True)
    serial_number = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    color = db.Column(db.String(30))
    description = db.Column(db.Text)
    is_lost = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)     # user can "lock" (mark as needing recovery)
    is_recovered = db.Column(db.Boolean, default=False)
    lost_date = db.Column(db.DateTime)
    lost_location = db.Column(db.String(200))
    last_location_lat = db.Column(db.Float)
    last_location_lng = db.Column(db.Float)
    last_location_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    evidences = db.relationship('Evidence', backref='device', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='device', lazy=True, cascade='all, delete-orphan')
    locations = db.relationship('LocationHistory', backref='device', lazy=True, cascade='all, delete-orphan')

class Evidence(db.Model):
    __tablename__ = 'evidences'
    id = db.Column(db.Integer, primary_key=True)
    evidence_type = db.Column(db.String(50))         # affidavit, receipt, photo, id_document
    file_path = db.Column(db.String(300), nullable=False)
    original_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    is_private = db.Column(db.Boolean, default=True)
    is_from_admin = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id', ondelete='SET NULL'))

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(50), default='pending')  # pending, investigating, resolved, rejected
    description = db.Column(db.Text, nullable=False)
    police_station = db.Column(db.String(100))
    police_report_number = db.Column(db.String(50))
    officer_name = db.Column(db.String(100))
    officer_contact = db.Column(db.String(50))
    admin_notes = db.Column(db.Text)
    resolution_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    assigned_admin = db.Column(db.Integer, db.ForeignKey('users.id'))

class LocationHistory(db.Model):
    __tablename__ = 'location_history'
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float)
    note = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id', ondelete='CASCADE'))

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref='activities')

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    message = db.Column(db.Text)
    type = db.Column(db.String(30), default='info')
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
