from .environment import ENV, SECRET_KEY, PORT, SQLALCHEMY_DATABASE_URI, FRONTEND_URL, MAIL_SERVER, MAIL_PASSWORD, MAIL_USERNAME
from .settings import load_config
from .mail_config import mail, load_mail_config
