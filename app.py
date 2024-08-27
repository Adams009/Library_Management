from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) # create a Flask instance
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///library.db" #setup the database type and location
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # setup the modification tracker

db = SQLAlchemy(app) # create an SQLAlchemy instance

if __name__ == '__main__':
    app.run()