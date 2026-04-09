import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kmanager-secure-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/kmanager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TRANSLATION_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
