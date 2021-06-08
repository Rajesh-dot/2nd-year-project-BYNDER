from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'rajesh aka the king'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_PATH'] = 'static'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')

    from .models import User, Note

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    from .models import User
    if not path.exists('website/'+DB_NAME):
        db.create_all(app=app)
        print("Created Database!")
        with app.app_context():
            new_user = User(email='rajesh@grasp.com', first_name='admin', password=generate_password_hash(
                '1234567', method='sha256'), user_type='a', dob=func.now(), mobile=8333030157, gender='m')
            db.session.add(new_user)
            db.session.commit()
            print('Admin added!')


def create_admin(app):
    from .models import User
    with app.app_context():
        new_user = User(email='rajesh@grasp.com', first_name='admin', password=generate_password_hash(
            '1234567', method='sha256'), user_type='a', dob=func.now(), mobile=8333030157, gender='m')
        db.session.add(new_user)
        db.session.commit()
        print('Admin added!')
