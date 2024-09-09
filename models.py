from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from sqlalchemy import UniqueConstraint

# initialize SQLAlchemy
db = SQLAlchemy()

FINE_PER_WEEK = 500  # Fine amount per week for late returns
FINE_ON_DAMAGE = 1000 # Fine amount for damaged books

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # create a unique identifier for each user
    username = db.Column(db.String(150), nullable=False, unique=True, index=True) # unique username for each user
    _save_hashed_password = db.Column(db.String(150), nullable=False) # hashed password for security
    email = db.Column(db.String(150), nullable=False, unique=True, index=True) # unique email for each user
    first_name = db.Column(db.String(150), nullable=False) # first name of the user
    last_name = db.Column(db.String(150), nullable=False) # last name of the user
    phone_number = db.Column(db.String(150), nullable=False) # phone number of the user
    date_of_birth = db.Column(db.Date, nullable=False) # date of birth of user
    address = db.Column(db.String(255), nullable=False) # address of the user
    guarantor_fullname = db.Column(db.String(150), nullable=False) # fullname of the user's guarantor
    guarantor_phone_number = db.Column(db.String(150), nullable=False) # phone number of the user's guarantor
    guarantor_address = db.Column(db.String(255), nullable=False) # address of the user's guarantor
    guarantor_relationship = db.Column(db.String(150), nullable=False) # relationship between the user and the guarantor

    borrowed_books = db.relationship('Borrowed', back_populates='user', lazy=True) # one-to-many relationship with Borrowed model

    @property
    def password(self):
        """Password property is not readable."""
        raise AttributeError("Password not readable")
    
    @password.setter
    def password(self, password):
        """Set hashed password with validation."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        self._save_hashed_password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hashed password."""
        return check_password_hash(self._save_hashed_password, password)
    
    def update_password(self, old_password, new_password):
        """Update user's password with validation."""
        if not self.check_password(old_password):
            raise ValueError("Old password is incorrect")
        if len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters long")
        self.password = new_password
        db.session.commit()
    
    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True) # create a unique identifier for each book
    title = db.Column(db.String(150), nullable=False, index=True) # title of the book
    author = db.Column(db.String(150), nullable=False, index=True) # author of the book
    year = db.Column(db.Integer, nullable=False) # year the book was published
    isbn = db.Column(db.String(150), nullable=False, unique=True, index=True) # unique ISBN for each book
    total_copies = db.Column(db.Integer, nullable=False) # total number of copies of the book
    available_copies = db.Column(db.Integer, nullable=False) # number of copies of the book available for borrowing
    available = db.Column(db.Boolean, default=True) # whether the book is available for borrowing or not
    language = db.Column(db.String(50), nullable=True, index=True) # language of the book
    category = db.Column(db.String(100), nullable=True, index=True) # category of the book
    publisher = db.Column(db.String(150), nullable=True, index=True) # publisher of the book
    cover_image_url = db.Column(db.String(255), nullable=True) # URL to the cover image of the book

    borrowed_books = db.relationship('Borrowed', back_populates='book', lazy=True) # one-to-many relationship with Borrowed model

    def update_availability(self):
        """Update the availability status of the book based on available copies."""
        self.available = self.available_copies > 0

    def book_serialize(self):
        """Serialize book data for API responses."""
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True) # Foreign key to User
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False, index=True) # Foreign key to Book
    borrow_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # date when the book was borrowed
    return_date = db.Column(db.DateTime, nullable=True) # date when the book was returned
    due_date = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow() + timedelta(days=14)) # date when the book was returned
    fine_amount = db.Column(db.Float, default=0.0) # amount to be paid as fine for late return of the book
    damage_fine = db.Column(db.Float, default=0.0) # amount to be paid as fine for damages on book when returned 
    damage = db.Column(db.Boolean, default=False, nullable=False) # Flag indicating if the book was damaged on return
    total_fine = db.Column(db.Float, default=0.0) # total fine amount to be paid by the user (fine_amount + damage_fine)

    book = db.relationship('Book', back_populates='borrowed_books', lazy=True) # one-to-many relationship with Book model
    user = db.relationship('User', back_populates='borrowed_books', lazy=True) # one-to-many relationship with User model

    def borrowed_serialize(self):
        """Serialize borrowed book data for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date,
            'due_date': self.due_date,
            'fine': f"Failure to return on time will result in a fine of {FINE_PER_WEEK} per week.", # add fine information to the serialized data
            'damage_fine': f"There is Additional fine of damage: {FINE_ON_DAMAGE} if book is not returned as taken",
            'book_title': self.book.title, # add book title to the serialized data
        }
    
    def return_book(self):
        """Handle book return, calculate fines, and update book availability."""
        self.return_date = datetime.utcnow()
        if self.return_date > self.due_date:
            days_late = (self.return_date - self.due_date).days
            weeks_late = days_late // 7
            self.fine_amount = weeks_late * FINE_PER_WEEK
        if self.damage == True:
            self.damage_fine = FINE_ON_DAMAGE
        self.total_fine = self.fine_amount + self.damage_fine

        self.book.available_copies += 1
        new_availability_status = self.book.available_copies > 0
        db.session.commit()

        if self.book.available != new_availability_status:
            self.book.available = new_availability_status
            db.session.commit()


class ReadingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True) # Foreign key to User
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False, index=True) # Foreign key to Book
    user = db.relationship('User', backref='reading_list', lazy=True)
    book = db.relationship('Book', backref='reading_list', lazy=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'book_id', name='uix_user_book'),
    )