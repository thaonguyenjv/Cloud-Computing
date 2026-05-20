import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI        = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TAX_RATE = 0.08

    # SES SMTP
    MAIL_SERVER   = os.environ.get('MAIL_SERVER', 'email-smtp.us-east-1.amazonaws.com')
    MAIL_PORT     = 587
    MAIL_USE_TLS  = True
    MAIL_USE_SSL  = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # S3
    S3_BUCKET = os.environ.get('S3_BUCKET', 'pos-s3-receipt-g8')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')