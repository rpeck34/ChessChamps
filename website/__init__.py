from flask import Flask
from os import path
from flask_login import LoginManager
from .events import socketio

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'jhalsdkjfhlakjhlkjshl'

    from .models import db, DB_NAME
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    #stuff that requires db to be active already goes here
    #need to register blueprings in auth and views
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    with app.app_context():
        #only run this when you have made a change to db models
        #db.drop_all()
        db.create_all()

    #needs to come from events otherwise don't get access
    #to the evenhandlers there
    #from .events import socketio

    login_manager = LoginManager()
    #this is where we get redirected when a page requires login
    #but user is not logged in
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    #this tells flask how we load a user.  Here we are looking
    #for user id
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    socketio.init_app(app)
    return app

#checks if database exists or not, if so do nothing,
#if not, create a new database
def create_database(app):
    if not path.exists('website/' + DB_Name):
        db.create_all(app = app)
        print('Created Database!')
