from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

# initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # crate a unique identifier for each user
    username = db.Column(db.String(150), nullable=False, unique=True) # unique username for each user
    password = db.Column(db.String(150), nullable=False) # password for each user authentication
    email = db.Column(db.String(150), nullable=False, unique=True) # unique email for each user
    first_name = db.Column(db.String(150), nullable=False) # first name of the user
    last_name = db.Column(db.String(150), nullable=False) # last name of the user
    phone_number = db.Column(db.String(150), nullable=False) # phone number of the user
    date_of_birth = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(255), nullable=True) # address of the user
    guarantor_fullname = db.Column(db.String(150), nullable=True) # fullname of the user's guarantor
    guarantor_phone_number = db.Column(db.String(150), nullable=True) # phone number of the user's guarantor
    guarantor_address = db.Column(db.String(255), nullable=True) # address of the user's guarantor
    guarantor_relationship = db.Column(db.String(150), nullable=True) # relationship between the user and the guarantor

    borrowed_books = db.relationship('Borrowed', back_populates='user', lazy=True) # one-to-many relationship with Borrowed model

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
    total_copies = db.Column(db.Integer, nullable=False) # total number of copies of the book
    available_copies = db.Column(db.Integer, nullable=False) # number of copies of the book available for borrowing
    available = db.Column(db.Boolean, default=True) # whether the book is available for borrowing or not
    language = db.Column(db.String(50), nullable=True) # language of the book
    category = db.Column(db.String(100), nullable=True) # category of the book
    publisher = db.Column(db.String(150), nullable=True) # publisher of the book
    cover_image_url = db.Column(db.String(255), nullable=True) # URL to the cover image of the book

    borrowed_books = db.relationship('Borrowed', back_populates='book', lazy=True) # one-to-many relationship with Borrowed model

    def update_availability(self):
        self.available = self.available_copies > 0

    def book_serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'isbn': self.isbn,
            'language': self.language,
            'category': self.category,
            'publisher': self.publisher,
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


class Borrowed(db.Model):
    id = db.Column(db.Integer, primary_key=True) # create a unique identifier for each borrowed book
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # create a relationship between the borrowed book and the user
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False) # create a relationship between the borrowed book and the book
    borrow_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # date when the book was borrowed
    return_date = db.Column(db.DateTime, nullable=True) # date when the book was returned
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow() + timedelta(days=14)) # date when the book was returned
    fine_amount = db.Column(db.Float, default=0.0) # amount to be paid as fine for late return of the book

    book = db.relationship('Book', back_populates='borrowed_books', lazy=True) # one-to-many relationship with Book model
    user = db.relationship('User', back_populates='borrowed_books', lazy=True) # one-to-many relationship with User model

    def borrowed_serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date,
            'due_date': self.due_date,
            'book_title': self.book.title, # add book title to the serialized data
        }
    
    def return_book(self):
        FINE_PER_WEEK = 500  # Define fine per week
        self.return_date = datetime.utcnow()
        if self.return_date > self.due_date:
            self.fine_amount = (self.return_date - self.due_date).weeks * FINE_PER_WEEK  # Define FINE_PER_DAY
        db.session.commit()
        self.book.available_copies += 1
        self.book.update_availability()