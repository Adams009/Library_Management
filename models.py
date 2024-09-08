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
    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True) # create a unique identifier for each book
    title = db.Column(db.String(150), nullable=False) # title of the book
    author = db.Column(db.String(150), nullable=False) # author of the book
    year = db.Column(db.Integer, nullable=False) # year the book was published
    isbn = db.Column(db.String(150), nullable=False, unique=True) # unique ISBN for each book
    total_copies = db.Column(db.Integer, nullable=False)
    available_copies = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Boolean, default=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # create a relationship between the book and the user

    borrowed_books = db.relationship('Borrowed', back_populates='book', lazy=True) # one-to-many relationship with Borrowed model

    def update_availability(self):
        self.available = self.available_copies > 0

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'isbn': self.isbn,
            'available': self.available
        }
    
    # def borrow_book(self, user_id):
    #     if self.available_copies > 0:
    #         self.available_copies -= 1
    #         borrowed = Borrowed(user_id=user_id, book_id=self.id)
    #         db.session.add(borrowed)
    #         db.session.commit()
    #         self.update_availability()
    #         return True
    #     return False



