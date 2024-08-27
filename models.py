from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # crate a unique identifier for each user
    username = db.Column(db.String(150), nullable=False, unique=True) # unique username for each user
    password = db.Column(db.String(150), nullable=False) # password for each user authentication
    email = db.Column(db.String(150), nullable=False, unique=True) # unique email for each user

    def password_hash(self, password):
        """
        Hash the password produced by the user for security purposes
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        Verify the password provided by the user against the hashed password stored in the database
        """
        return check_password_hash(self.password, password)