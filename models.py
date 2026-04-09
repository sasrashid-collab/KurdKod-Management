from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from datetime import datetime

db = SQLAlchemy()

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    license_key = db.Column(db.String(64), unique=True, nullable=False)
    license_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    users = db.relationship('User', backref='company', lazy=True)

    def set_license(self, key, secret):
        self.license_key = key
        self.license_hash = hashlib.sha256(key.encode() + secret.encode()).hexdigest()

    def verify_license(self, key, secret):
        return self.license_hash == hashlib.sha256(key.encode() + secret.encode()).hexdigest()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='کارمەند')
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    preferred_language = db.Column(db.String(5), default='ku')
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pwd):
        self.password_hash = generate_password_hash(pwd, method='pbkdf2:sha256')
    def check_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
