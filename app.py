from flask import Flask
from models import db
from flask_migrate import Migrate

app = Flask(__name__) # create a Flask instance
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///library.db" #setup the database type and location
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # setup the modification tracker for the database to False

db.init_app(app) # create an SQLAlchemy instance for the database
migrate = Migrate(app,db) # create a Migration instance

from blueprints.user_routes import users_bp
from blueprints.book_routes import books_bp
from blueprints.borrow_routes import borrow_bp

app.register_blueprint(users_bp, url_prefix='/api') # register the blueprint for the users
app.register_blueprint(books_bp, url_prefix='/api') # register the blueprint for the books
app.register_blueprint(borrow_bp, url_prefix='/api') # register the blueprint for the borrowed books

if __name__ == '__main__':
    app.run(debug=True) # run the app in debug mode