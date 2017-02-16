# app package constructor imports most extensions
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_pagedown import PageDown
from config import config

# then creates them uninitialized (no app as arg)
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
pagedown = PageDown()
# session protection setting changes what is stored for the session to try to prevent user tampering
# strong stores client's ip, user agent and logs user out if there is a change
login_manager.session_protection = "strong"
# prefixed with bp bc the login route is in the auth bp
login_manager.login_view = "auth.login"


# Application factory with selected config name as argument
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Run config specific configurations (if any)
    config[config_name].init_app(app)
    # Initialize extensions with new app instance
    login_manager.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)
    
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)
        
    # Attach routes and custom error pages
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    # url_prefix is optional, but causes all routes defined in the bp to be registered with the prefix
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix="/api/v1.0")
    
    # Factory function returns app instance
    return app
