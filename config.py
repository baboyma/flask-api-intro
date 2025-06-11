import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    APP_NAME = os.getenv('APP_NAME', 'Flask API Intro')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'flask_api_intro.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_NAME
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('DATABASE_TRACK_MODIFICATIONS', False)