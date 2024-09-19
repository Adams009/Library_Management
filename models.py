from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from dateutil import parser
import re
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException, is_valid_number, format_number, PhoneNumberFormat
# from sqlalchemy import UniqueConstraint

# initialize SQLAlchemy
db = SQLAlchemy()

date_check = r'^\d{4}[-/]\d{2}[-/]\d{2}$'
date_check2 = regex = r'^\d{2}[-/]\d{2}[-/]\d{4}$'
FINE_PER_WEEK = 500  # Fine amount per week for late returns
FINE_ON_DAMAGE = 1000 # Fine amount for damaged books

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # create a unique identifier for each user
    username = db.Column(db.String(150), nullable=False, unique=True, index=True) # unique username for each user
    save_hashed_password = db.Column(db.String(150), nullable=False) # hashed password for security
    email_address = db.Column(db.String(150), nullable=False, unique=True, index=True) # unique email for each user
    first_name = db.Column(db.String(150), nullable=False, index=True) # first name of the user
    last_name = db.Column(db.String(150), nullable=False, index=True) # last name of the user
    mobile_number = db.Column(db.String(150), nullable=False) # phone number of the user
    date_of_birth = db.Column(db.Date, nullable=False) # date of birth of user
    address = db.Column(db.String(255), nullable=False) # address of the user
    guarantor_fullname = db.Column(db.String(150), nullable=False) # fullname of the user's guarantor
    guarantor_mobile_number = db.Column(db.String(150), nullable=False) # phone number of the user's guarantor
    guarantor_address = db.Column(db.String(255), nullable=False) # address of the user's guarantor
    guarantor_relationship = db.Column(db.String(150), nullable=False) # relationship between the user and the guarantor
    register_date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow()) # date for registration

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
        self.save_hashed_password = generate_password_hash(password)

    @property
    def email(self):
        """Return the user's email address"""
        return self.email_address
    @email.setter
    def email(self, email):
        """Set user's email with validation."""
        try:
            if not isinstance(email, str) or not email:
                raise ValueError('Email must not be empty and be a valid email enclosed in a string')
            if email.isdigit():
                raise ValueError('Email must not be a numeric string')
            email = email.strip()
            validate_email(email)
            self.email_address = email
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email address: {e}")
        
    @property
    def phone_number(self):
        """Returns the user's phone number"""
        return self.mobile_number
    @phone_number.setter
    def phone_number(self, phone_number):
        """Sets the user's phone number with validation."""
        try:
            if type(phone_number) != str or not phone_number:
                raise ValueError('phonenumber cant be empty and  must be a string')
            phone_number = phone_number.strip() 
            number = phonenumbers.parse(phone_number, None)
            if not is_valid_number(number):
                raise ValueError("Invalid phone number format. Please enter the number with your country code")
            formatted_number = format_number(number, PhoneNumberFormat.INTERNATIONAL)
            if formatted_number == self.guarantor_mobile_number:
                raise ValueError("User's phone number cannot be the same as the guarantor's phone number")
            self.mobile_number = formatted_number
        except NumberParseException as e:
            raise ValueError(f"Invalid phone number. Please enter the number with your country code: {e}")
        
    @property
    def guarantor_phone_number(self):
        """Returns the guarantor's phone number"""
        return self.guarantor_mobile_number
    @guarantor_phone_number.setter
    def guarantor_phone_number(self, phone_number):
        """Sets the guarantor's phone number with validation."""
        try:
            if type(phone_number) != str or not phone_number:
                raise ValueError('phonenumber cant be empty and  must be a string')
            phone_number = phone_number.strip() 
            number = phonenumbers.parse(phone_number, None)
            if not is_valid_number(number):
                raise ValueError("Invalid phone number format. Please enter the number with your country code")
            formatted_number = format_number(number, PhoneNumberFormat.INTERNATIONAL)
            if formatted_number == self.mobile_number:
                raise ValueError("Guarantor's phone number cannot be the same as the user's phone number")
            self.guarantor_mobile_number = formatted_number
        except NumberParseException as e:
            raise ValueError(f"Invalid phone number format. Please enter the number with your country code: {e}")
    def check_password(self, password):
        """Check if the provided password matches the hashed password."""
        return check_password_hash(self.save_hashed_password, password)
    
    def update_password(self, old_password, new_password):
        """Update user's password with validation."""
        if not self.check_password(old_password):
            raise ValueError("Old password is incorrect")
        if len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters long")
        self.password = new_password
        db.session.commit()

    def validate_date_of_birth(self, date_of_birth):
        """Validate and set the date of birth."""
        if type(date_of_birth) != str or not date_of_birth:
            raise ValueError('Date of birth must be a string and not empty')
        dob = date_of_birth.strip()
        if not re.match(date_check, dob) and not re.match(date_check2, dob):
            raise ValueError("Date must be in the format YYYY-MM-DD or YYYY/MM/DD.")
        if not (dob.day and dob.month and dob.year):
                raise ValueError("Date must include day, month, and year.")
        dob = parser.parse(dob)
        if dob.date() > datetime.now().date():
            raise ValueError('Date of birth cannot be in the future')
        self.date_of_birth = dob.date()
        
    def validate_username(self, username):
        """Validate and set the username."""
        if type(username) != str or not username:
            raise ValueError('Username must not be empty and  be a valid username and string')
        if username.isdigit():
            raise ValueError('Username must not be a number')
        username = username.strip()
        nameformat = r'^[a-zA-Z][a-zA-Z0-9]*$'
        if not re.match(nameformat, username):
            raise ValueError('Username must only contain alphanumeric characters and start with a letter')
        if ' ' in username:
            raise ValueError('Username cannot contain spaces')
        if len(username) < 5 or len(username) > 15:
            raise ValueError('Username must be between 5 and 15 characters long')
        self.username = username

    def validate_address(self, address):
        """Validate the address."""
        if type(address) != str or not address:
            raise ValueError('Address must be a string and not empty')
        if address.isdigit():
            raise ValueError('Address cant be a number')
        address = address.strip()
        format = r'^[a-zA-Z0-9\s,\.-]+$'
        if not re.match(format, address):
            raise ValueError('Address can only contain alphanumeric characters, spaces, commas, periods, and hyphens')
        return address
    
    def validate_firstname(self, firstname):
        """ Validate the first name or last name"""
        if type(firstname) != str or not firstname:
            raise ValueError('First name or last name must be a string and not empty')
        if firstname.isdigit():
            raise ValueError('First name or last name cant be a number')
        firstname = firstname.strip()
        pattern = r"^[A-Za-z][A-Za-z'-]{2,70}$"
        if not re.match(pattern, firstname):
            raise ValueError('First name or last name should only contain alphabetical characters, hyphens and apostrophe and be 2 characters long')
        if ' ' in firstname:
            raise ValueError('first name or last name cannot contain space')
        if len(firstname) < 2 or len(firstname) > 70:
            raise ValueError('first name or last name must be 2 characters long and not over 70 characters')
        return firstname
    
    def validate_fullname(self, fullname):
        """Validate the fullname."""
        if type(fullname) != str or not fullname:
            raise ValueError('Fullname must be a string and not empty')
        if fullname.isdigit():
            raise ValueError('Fullname cant be a number')
        fullname = fullname.strip()
        pattern = r"^[A-Za-z][A-Za-z '-]{2,70}$"
        if not re.match(pattern, fullname):
            raise ValueError('Fullname should only contain alphabetical characters, hyphens and apostrophe and be 2 characters long')
        if len(fullname) < 2 or len(fullname) > 70:
            raise ValueError('fullname must be 2 characters long and not over 70 characters')
        return fullname

    def validate_relation(self, guarantor_relation):
        """ Validate the relation"""
        if type(guarantor_relation) != str or not guarantor_relation:
            raise ValueError('guarantor address must be a string and not empty')
        if guarantor_relation.isdigit():
            raise ValueError('guarantor relation cant be a number')
        guarantor_relation = guarantor_relation.strip()
        return guarantor_relation

    def user_serialize(self):
        """Serialize the user instance to a dictionary."""
        return {
            'a_message': "registration successful",
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'date_of_birth': self.date_of_birth.isoformat(),  # Convert date to ISO format string
            'address': self.address,
            'guarantor_fullname': self.guarantor_fullname,
            'guarantor_phone_number': self.guarantor_phone_number,
            'guarantor_address': self.guarantor_address,
            'guarantor_relationship': self.guarantor_relationship,
            'register_date': self.register_date.date().isoformat()
        }
    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True) # create a unique identifier for each book
    title = db.Column(db.String(150), nullable=False, index=True) # title of the book
    author = db.Column(db.String(150), nullable=False, index=True) # author of the book
    year = db.Column(db.Integer, nullable=False, index=True) # year the book was published
    isbn = db.Column(db.String(150), nullable=False, unique=True, index=True) # unique ISBN for each book
    total_copies = db.Column(db.Integer, nullable=False) # total number of copies of the book
    available_copies = db.Column(db.Integer, nullable=False) # number of copies of the book available for borrowing
    available = db.Column(db.Boolean, default=True) # whether the book is available for borrowing or not
    language = db.Column(db.String(50), nullable=False, index=True) # language of the book
    category = db.Column(db.String(100), nullable=False, index=True) # category of the book
    publisher = db.Column(db.String(150), nullable=False, index=True) # publisher of the book
    cover_image_url = db.Column(db.String(255), nullable=True, default='https://example.com/default-cover.jpg') # URL to the cover image of the book

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
            'available': self.available,
            'cover_image_url': self.cover_image_url
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
    borrow_date = db.Column(db.DateTime, nullable=False, default=lambda :datetime.utcnow()) # date when the book was borrowed
    return_date = db.Column(db.DateTime, nullable=True) # date when the book was returned
    due_date = db.Column(db.DateTime, nullable=False, index=True, default=lambda: datetime.utcnow() + timedelta(days=14)) # date when the book was returned
    fine_amount = db.Column(db.Float, default=0.0) # amount to be paid as fine for late return of the book
    damage_fine = db.Column(db.Float, default=0.0) # amount to be paid as fine for damages on book when returned 
    damage = db.Column(db.Boolean, default=False, nullable=False) # Flag indicating if the book was damaged on return
    total_fine = db.Column(db.Float, default=0.0) # total fine amount to be paid by the user (fine_amount + damage_fine)

    book = db.relationship('Book', back_populates='borrowed_books', lazy=True) # one-to-many relationship with Book model
    user = db.relationship('User', back_populates='borrowed_books', lazy=True) # one-to-many relationship with User model

    def borrowed_serialize(self):
        """Serialize borrowed book data for API responses."""
        return {
            'a_message': "Book borrowed successfully",
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date.date().isoformat(),
            'due_date': self.due_date.date().isoformat(),
            'fine': f"Failure to return on time will result in a fine of {FINE_PER_WEEK} per week.", # add fine information to the serialized data
            'damage_fine': f"There is Additional fine of damage: {FINE_ON_DAMAGE} if book is not returned as taken",
            'book_title': self.book.title, # add book title to the serialized data
        }
    
    def return_book(self, damage):
        """Handle book return, calculate fines, and update book availability."""
        self.return_date = datetime.utcnow()
        if self.return_date > self.due_date:
            days_late = (self.return_date - self.due_date).days
            weeks_late = days_late // 7
            self.fine_amount = weeks_late * FINE_PER_WEEK
        else:
            self.fine_amount = 0.0

        self.damage = damage
        if self.damage == True:
            self.damage_fine = FINE_ON_DAMAGE
        else:
            self.damage_fine = 0.0
        self.total_fine = self.fine_amount + self.damage_fine

        self.book.available_copies += 1
        new_availability_status = self.book.available_copies > 0

        if self.book.available != new_availability_status:
            self.book.available = new_availability_status
            db.session.commit()
        
        db.session.commit()

class ReadingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True) # Foreign key to User
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False, index=True) # Foreign key to Book

    user = db.relationship('User', backref='reading_list', lazy=True)
    book = db.relationship('Book', backref='reading_list', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='uix_user_book'),
    )

    def reading_serialize(self):
        return {
            "a_message": "Book Added to Read List successfully",
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username,
            "book_id": self.book_id,
            "title": self.book.title,
            "author": self.book.author,
            "year": self.book.year,
            "isbn": self.book.isbn,
            "language": self.book.language,
            "category": self.book.category,
            "publisher": self.book.publisher
        }
