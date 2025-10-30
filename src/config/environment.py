from dotenv import load_dotenv
import os

load_dotenv()
ENV = os.getenv("FLASK_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")
PORT = int(os.getenv("PORT", 3000))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000")


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_DIALECT = os.getenv('DB_DIALECT', "mysql+pymysql")
SQLALCHEMY_DATABASE_URI = f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
