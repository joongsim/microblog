from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

# First initialization (global)
bootstrap = Bootstrap()
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
migrate = Migrate()
mail = Mail()
moment = Moment()
babel = Babel()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Binding extension instances to main application
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Only enable email error logger if not in debug mode
    # Server must be configured in config.py
    if not app.debug and not app.testing:
        if current_app.config['MAIL_SERVER']:
            auth = None
            if current_app.config['MAIL_USERNAME'] or current_app.config['MAIL_PASSWORD']:
                auth = (current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            secure = None
            if current_app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']),
                fromaddr='no-reply@' + current_app.config['MAIL_SERVER'],
                toaddrs=current_app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure, timeout=10)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        # Rotating error log
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
            backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app


# Selects language from user OS setting
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from app import models
from app.auth import routes
