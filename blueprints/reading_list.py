from flask import Blueprint,jsonify, request
from models import *
from werkzeug.exceptions import BadRequest
import re
from email_validator import validate_email, EmailNotValidError

read_list_bp = Blueprint('reading', __name__)

@read_list_bp.route('/users/<int:user_id>/read', methods=['POST'])
def add_read_list(user_id):
    """
Summary:
    Add a book to a user's reading list if certain conditions are met; otherwise, return an error message.

Description:
    This endpoint allows a user to add a book to their reading list. It accepts a JSON request body containing the book ID,
    username, and email. The endpoint performs several checks to ensure that the addition meets the required criteria.
    It verifies:
    - The user exists and the provided username and email match the user's records.
    - The book exists in the database.
    - The user has previously borrowed the book and has returned it.
    - The book is not already in the reading list.

    The endpoint checks for:
    - Validity of the provided book ID.
    - Correctness of the email format.
    - Validity of the username, ensuring it meets specific criteria.

Args:
    user_id (int): The ID of the user adding the book to the reading list.

Optional parameters in the JSON body:
    - book_id (int): The ID of the book to add to the reading list (required).
    - username (string): The username of the user (required).
    - email (string): The email address of the user (required).

HTTP Status Codes:
    400 Bad Request
    404 Not Found
    201 Created
    409 Conflict

Errors:
- Invalid or missing book ID, username, or email.
- User not found.
- Book not found.
- User has not borrowed the book or has not returned it.
- Book is already in the reading list.
- Validation errors for username or email format.

Returns:
    JSON: A JSON object containing the newly created reading list entry if successful; otherwise, an error message.
"""
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    try:
        data = request.get_json()
    except BadRequest as e:
         return jsonify({'error': 'Invalid JSON', 'message': str(e)}), 400

    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    required_fields = ['book_id', 'username', 'email']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'})
        
    book_id = data.get('book_id')
    user_name = data.get('username')
    email = data.get('email')

    if not book_id or not user_name or not email:
        return jsonify({'error': 'book_id, username, email is required to add a book tp rading list'}), 400
    
    try:
        if type(book_id) == str:
            book_id = user_id.strip()
            if not book_id.isdigit():
                raise ValueError()
            book_id=int(book_id)
        book_id = int(book_id)
        if book_id <= 0:
            raise ValueError()
    except Exception as e:
        return jsonify({'error': f'Invalid book_id: book_id must be an integer and greater than 0 {e}'}), 400
    
    try:
        if not isinstance(email, str):
            raise TypeError('Email must be a valid and enclosed in string')
        if email.isdigit():
            raise ValueError('Email must not be a numeric string')
        email = email.strip()
        validate_email(email)
    except EmailNotValidError as e:
        return jsonify({'error' : f'Invalid email address: {e}'}), 400
    except TypeError as e:
        return jsonify({'error' : str(e)}), 400
    except Exception as e:
        return jsonify({'error' : str(e)}), 400
    
    try:
        if type(user_name) != str:
            raise TypeError('User name must be a string')
        if user_name.isdigit():
            raise ValueError('User name must not be a string digit')
        user_name = user_name.strip()
        nameformat = r'^[a-zA-Z][a-zA-Z0-9]*$'
        if not re.match(nameformat, user_name):
            raise ValueError('Username must only contain alphanumeric characters and start with a letter')
        if ' ' in user_name:
            raise ValueError('Username cannot contain spaces')
        if len(user_name) < 5 or len(user_name) > 15:
            raise ValueError('Username must be between 5 and 15 characters long')
    except Exception as e:
        return jsonify({'error' : str(e)}), 400
    
    if not User.query.get(user_id):
        return jsonify({'error': 'user not found'}), 404
    
    reader = User.query.filter_by(username=user_name, id=user_id, email_address=email).first()
    if not reader:
        return jsonify({'error': 'user not found: id, username,and / or email do not match'}), 404
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    borrowed_entry = Borrowed.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not borrowed_entry:
         return jsonify({'error': 'You never borrowed the book, so you can\'t add it to the reading list.'}), 400
    if borrowed_entry and borrowed_entry.return_date is None:
        return jsonify({"message": "You must return the book before adding it to your reading list."}), 409

    
    existing_entry = ReadingList.query.filter_by(user_id=user_id, book_id=book_id).first()
    if existing_entry:
        return jsonify({"message": "Book already in reading list."}), 409
    
    try:
        reading_list = ReadingList(user_id=user_id, book_id=book_id)
        db.session.add(reading_list)
        db.session.commit()

        return jsonify(reading_list.reading_serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@read_list_bp.route('/users/<int:user_id>/read', methods=['GET'])
def read_list(user_id):
    """
Summary:
    Retrieve a paginated list of books from a user's reading list, with optional filtering based on various parameters.

Description:
    This endpoint fetches a user's reading list and supports pagination and filtering by different criteria such as 
    title, author, category, publisher, language, and book ID. The results are returned in a paginated format, 
    allowing clients to specify the desired page number and the number of results per page.

    The endpoint performs validation checks on pagination parameters to ensure they are positive integers. 
    It applies filters based on the provided query parameters to narrow down the results.

Args:
    user_id (int): The ID of the user whose reading list is being requested.

Query Parameters:
    - page (int): The page number to retrieve (default is 1).
    - per_page (int): The number of items to return per page (default is 10).
    - title (string): Filter results to include books with titles matching this string (optional).
    - author (string): Filter results to include books by authors matching this string (optional).
    - category (string): Filter results to include books in this category (optional).
    - publisher (string): Filter results to include books published by this publisher (optional).
    - language (string): Filter results to include books in this language (optional).
    - book_id (int): Filter results to include only the book with this ID (optional).

HTTP Status Codes:
    200 OK
    400 Bad Request
    404 Not Found

Errors:
- Invalid pagination parameters (must be positive integers).
- Invalid or missing filtering criteria (e.g., invalid book ID).
- No books found matching the specified criteria.

Returns:
    JSON: A JSON object containing:
        - read_list: A list of books in the user's reading list matching the criteria.
        - total_result: The total number of books found.
        - page: The current page number.
        - per_page: The number of results per page.
        - total_pages: The total number of pages available.
"""
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)

    title = request.args.get('title', None)
    author = request.args.get('author', None)
    category = request.args.get('category', None)
    publisher = request.args.get('publisher', None)
    language = request.args.get('language', None)
    book_id = request.args.get('book_id', None)
    
    try:
        page = int(page)
        per_page = int(per_page)
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Page and per_page parameters must be positive integers'}), 400
    except Exception as e:
        return jsonify({'error': f'Page and per_page parameters must be integers {e}'}), 400
    
    query = ReadingList.query.join(Book).filter(ReadingList.user_id == user_id)
    
    if book_id:
        try:
            book_id = int(book_id)
            if book_id <= 0:
                raise ValueError()
            query = query.filter(ReadingList.book_id==book_id)
        except Exception as e:
            return jsonify({'error': f'Invalid book_id: book_id must be an integer and must be greater than 0 {e}'}), 400
        
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))

    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))

    if category:
        query = query.filter(Book.category.ilike(f'%{category}%'))

    if publisher:
        query = query.filter(Book.publisher.ilike(f'%{publisher}%'))

    if language:
        query = query.filter(Book.language.ilike(f'%{language}%'))


    paginated_query = query.paginate(page=page, per_page=per_page, error_out=False)
    
    if (book_id or title or author or category or language or publisher) and not paginated_query.items:
        return jsonify({'error': 'No Read books found matching the specified criteria'}), 404
    
    if not (book_id or title or author or category or language or publisher):
        if not paginated_query.items:
            return jsonify({'error': 'No read books found'}), 200
        
    total_books = paginated_query.total
     
    books = [{
        'book_id': entry.book.id,
        'title': entry.book.title,
        'author': entry.book.author,
        'category': entry.book.category
    } for entry in paginated_query.items]

    return jsonify({
         'read_list': books,
         'total_result': total_books,
         'page': page,
         'per_page': per_page,
         'total_pages': paginated_query.pages
    }), 200
         
@read_list_bp.route('/users/<int:user_id>/read/<int:book_id>', methods=['DELETE'])
def remove_from_read_list(user_id, book_id):
    """
Summary:
    Remove a specified book from a user's reading list based on their ID and provided credentials.

Description:
    This endpoint allows a user to delete a book from their reading list. 
    The request must contain a JSON body with the username and email to verify the user's identity.
    The endpoint checks if the specified book is in the user's reading list and validates the provided user credentials 
    against the stored data.

    The endpoint performs the following validations:
    - Ensures the request body is in JSON format.
    - Validates the presence and correctness of required fields (username, email).
    - Checks the validity of user ID and book ID to ensure they are integers greater than zero.
    - Confirms that the specified user exists and matches the provided username and email.
    - Checks if the book exists in the database.

Args:
    user_id (int): The ID of the user from whose reading list the book will be removed.
    book_id (int): The ID of the book to be removed from the reading list.

HTTP Status Codes:
    200 OK
    400 Bad Request
    404 Not Found
    500 Internal Server Error

Errors:
- Invalid or missing data.
- User not found or credentials do not match.
- Book not found in the reading list.
- Database errors during deletion.

Returns:
    JSON: A JSON object indicating success or failure of the deletion operation.
"""
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    try:
        data = request.get_json()
    except BadRequest as e:
         return jsonify({'error': 'Invalid JSON', 'message': str(e)}), 400
    
    required_fields = ['username', 'email']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'})
        
    user_name = data.get('username')
    email = data.get('email')

    if not user_name or not email:
        return jsonify({'error': 'username, email is required to delete a book tp rading list'}), 400
    
    try:
        if type(book_id) == str:
            book_id = user_id.strip()
            if not book_id.isdigit():
                raise ValueError()
            book_id=int(book_id)
        book_id = int(book_id)
        if book_id <= 0:
            raise ValueError()
    except Exception as e:
        return jsonify({'error': f'Invalid book_id: book_id must be an integer and greater than 0 {e}'}), 400
    
    try:
        if type(user_id) == str:
            user_id = user_id.strip()
            if not user_id.isdigit():
                raise ValueError()
            user_id=int(book_id)
        user_id = int(book_id)
        if user_id <= 0:
            raise ValueError()
    except Exception as e:
        return jsonify({'error': f'Invalid user_id: user_id must be an integer and greater than 0 {e}'}), 400
    
    try:
        if not isinstance(email, str):
            raise TypeError('Email must be a valid and enclosed in string')
        if email.isdigit():
            raise ValueError('Email must not be a numeric string')
        email = email.strip()
        validate_email(email)
    except EmailNotValidError as e:
        return jsonify({'error' : f'Invalid email address: {e}'}), 400
    except TypeError as e:
        return jsonify({'error' : str(e)}), 400
    except Exception as e:
        return jsonify({'error' : str(e)}), 400
    
    try:
        if type(user_name) != str:
            raise TypeError('User name must be a string')
        if user_name.isdigit():
            raise ValueError('User name must not be a string digit')
        user_name = user_name.strip()
        nameformat = r'^[a-zA-Z][a-zA-Z0-9]*$'
        if not re.match(nameformat, user_name):
            raise ValueError('Username must only contain alphanumeric characters and start with a letter')
        if ' ' in user_name:
            raise ValueError('Username cannot contain spaces')
        if len(user_name) < 5 or len(user_name) > 15:
            raise ValueError('Username must be between 5 and 15 characters long')
    except Exception as e:
        return jsonify({'error' : str(e)}), 400
    
    reader = User.query.filter_by(id=user_id).first()
    if not reader:
        return jsonify({'error': 'User not found'}), 404
        
    reader = User.query.filter_by(username=user_name, id=user_id, email_address=email).first()
    if not reader:
        return jsonify({'error': 'user not found: id, username,and / or email do not match'}), 404
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    title = book.title
    reading_list = ReadingList.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not reading_list:
        return jsonify({'error': 'Book not found in reading list'}), 404
    try:
        db.session.delete(reading_list)
        db.session.commit()
        return jsonify({'message': 'Book removed from reading list successfully', "title": title}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting book from reading list: {e}'}), 500

@read_list_bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    """
    Summary:
        Handle all unmatched routes and return a 404 error message.

    Description:
        This endpoint serves as a catch-all handler for any requests that do not match the explicitly defined routes within the `read_list_bp` blueprint.
        It is invoked for any HTTP method (GET, POST, PUT, DELETE) and any path that is not explicitly defined in the blueprint.
        It returns a 404 Not Found error with a message indicating that the requested URL was not found on the server.

    Args:
        path (str): The unmatched path part of the URL that was requested.

    HTTP Response Codes:
        404 Not Found: Returned when the requested URL does not match any defined route in the blueprint.

    Returns:
        JSON: A JSON object containing an error message.
    """
    return jsonify({
        "error": "The requested URL was not found on the server. Please check your spelling and try again."}), 404