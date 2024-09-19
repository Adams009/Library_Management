from flask import Blueprint,jsonify, request
from models import *
from dateutil import parser
from werkzeug.exceptions import BadRequest

return_bp = Blueprint('return', __name__)

@return_bp.route('/books/<int:book_id>/return', methods=['POST'])
def return_book(book_id):
    """
    Summary:
        Return a borrowed book by its ID and update the borrow record in JSON format if successful; otherwise, return an error.

    Description:
        This endpoint processes the return of a borrowed book for a specific user.
        It expects a JSON request body containing the return details such as `user_id`, `username`, `email`, and `damage`.
        The endpoint performs several validations and checks:
        - If the `Content-Type` is not `application/json`, it returns a 400 error.
        - If the JSON body is invalid or missing, it returns a 400 error.
        - If `user_id`, `username`, `email`, or `damage` is missing or invalid, it returns a 400 error.
        - If `damage` is not a valid boolean value (`true` or `false`), it returns a 400 error.
        - If the email is invalid, it returns a 400 error.
        - If the user cannot be found with the provided `user_id`, `username`, and `email`, it returns a 404 error.
        - If the book was not borrowed by the user, or if it has already been returned, it returns a 404 or 409 error.
        - On successful return of the book, it returns a 200 status code with the updated borrow record in JSON format.
        - If there is any error during the return process, it returns a 500 error with a generic error message.

    Request Body (JSON):
        - `user_id` (int): The ID of the user returning the book.
        - `username` (str): The username of the user returning the book.
        - `email` (str): The email address of the user returning the book.
        - `damage` (str): The damage status of the book, should be "true" or "false".

    Args:
        book_id (int): The ID of the book being returned.

    HTTP Response Codes:
        200 OK: If the book is successfully returned and the borrow record is updated.
        400 Bad Request: If the request body is missing required fields or contains invalid data.
        404 Not Found: If the user or borrow record cannot be found.
        409 Conflict: If the book has already been returned or if the record was not found.
        500 Internal Server Error: For any unexpected errors during the return process.

    Returns:
        JSON: The updated borrow record in JSON format if the return is successful otherwise, an error message.
    """  
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    try:
        data = request.get_json()
    except BadRequest as e:
        return jsonify({'error': 'Invalid JSON', 'message': str(e)}), 400
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['user_id', 'username', 'email', 'damage']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    user_id = data.get('user_id')
    user_name = data.get('username')
    email = data.get('email')
    damage = data.get('damage')
    
    if not user_id or not user_name or not email or not damage:
        return jsonify({'error': 'user_id, username, email, damage is required to return a book'}), 400
    
    try:
        if type(user_id) == str:
            user_id = user_id.strip()
            if not user_id.isdigit():
                raise ValueError()
        user_id = int(user_id)
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
    
    try:
        if type(damage) != str:
            raise ValueError('damage must be a boolean value (true or false) enclosed in a string')
        damage = damage.strip()
        if damage.lower() not in ["true", "false"]:
            raise ValueError('error: damage must be true or false to return a book.')
        damage = damage.lower() == 'true'
    except ValueError as e:
        return jsonify({'error' : str(e)}), 400
    
    if not User.query.get(user_id):
        return jsonify({'error': 'User not found.'}), 404
    
    if not Book.query.get(book_id):
        return jsonify({'error': 'Book not found.'}), 404
    
    returner = User.query.filter_by(username=user_name, id=user_id, email_address=email).first()
    if not returner:
        return jsonify({'error': 'user not found: id, username, and/or email do not match'}), 404
    
    borrowed = Borrowed.query.filter_by(book_id=book_id, user_id=user_id, return_date=None).first()

    if not borrowed:
        returned = Borrowed.query.filter_by(book_id=book_id, user_id=user_id).first()
        if returned and returned.return_date is not None:
            return jsonify({'error': 'Book already returned.'}), 409
        return jsonify({'error': 'Borrowed record not found or not borrowed by this user.'}), 404
    
    try:
        borrowed.return_book(damage)
        return jsonify({
            "a_message": "Book returned succesfully",
            "id": borrowed.id,
            "user_id": borrowed.user_id,
            "book_id": borrowed.book_id,
            "borrow_date": borrowed.borrow_date.date().isoformat(),
            "due_date": borrowed.due_date.date().isoformat(),
            "returned_date": borrowed.return_date.date().isoformat(),
            "book_title": borrowed.book.title,
            "damage_status": borrowed.damage,
            "damage_fine": borrowed.damage_fine,
            "fine_amount": borrowed.fine_amount,
            "total_fine": borrowed.total_fine
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error' : 'An unexpected error occurred', 'message': str(e)}), 500

@return_bp.route('/return', methods=['GET'])
def get_all_returns():
    """
    Summary:
        Retrieve a paginated list of all returned books with optional filtering.

    Description:
        This endpoint returns a list of all books that have been returned.
        The results can be filtered based on various criteria, including book and user details, as well as date ranges.
        It also supports pagination through query parameters.
        The endpoint performs several validations and checks:
        - If `page` or `per_page` parameters are invalid (not positive integers), it returns a 400 error.
        - If filtering parameters (such as `user_id`, `book_id`, `borrow_date`, `due_date`, `return_date`) are invalid, it returns a 400 error.
        - If no results are found matching the specified criteria, it returns a 404 error.
        - If no filters are applied and no returned books are found, it returns a 200 status with an empty list.
        - On successful retrieval, it returns a 200 status code with a paginated list of returned books and metadata.

    Query Parameters:
        - `page` (int): The page number for pagination (default is 1).
        - `per_page` (int): The number of items per page (default is 10).
        - `title` (str): Filter by book title (partial match).
        - `author` (str): Filter by book author (partial match).
        - `category` (str): Filter by book category (partial match).
        - `publisher` (str): Filter by book publisher (partial match).
        - `language` (str): Filter by book language (partial match).
        - `user_id` (int): Filter by the ID of the user who borrowed the book.
        - `book_id` (int): Filter by the ID of the book.
        - `borrow_date` (str): Filter by the borrow date, must be in YYYY-MM-DD format.
        - `due_date` (str): Filter by the due date, must be in YYYY-MM-DD format.
        - `return_date` (str): Filter by the return date, must be in YYYY-MM-DD format.

    HTTP Response Codes:
        200 OK: If the request is successful and the returned books are retrieved.
        400 Bad Request: If the query parameters are invalid or in the wrong format.
        404 Not Found: If no books are found matching the specified criteria.
        
    Returns:
        JSON: A paginated list of returned books including the total count, current page, items per page, and total pages.
        If no books match the criteria or if no filters are applied and no books are found, the response will include appropriate messages.
    """
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    
    title = request.args.get('title', None)
    author = request.args.get('author', None)
    category = request.args.get('category', None)
    publisher = request.args.get('publisher', None)
    language = request.args.get('language', None)
    user_id = request.args.get('user_id', None)
    book_id = request.args.get('book_id', None)
    borrow_date = request.args.get('borrow_date', None)
    due_date = request.args.get('due_date', None)
    return_date = request.args.get('return_date', None)

    try:
        page = int(page)
        per_page = int(per_page)
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Page and per_page parameters must be positive integers'}), 400
    except Exception as e:
        return jsonify({'error': f'Page and per_page parameters must be integers {e}'}), 400
    
    query = Borrowed.query.join(Book, Borrowed.book_id==Book.id).filter(Borrowed.return_date.isnot(None))

    if user_id:
        try:
            user_id = int(user_id)
            if user_id <= 0:
                raise ValueError()
            query = query.filter(Borrowed.user_id==user_id)
        except Exception as e:
            return jsonify({'error': f'Invalid user_id: user_id must be an integer and must be greater than 0 {e}'}), 400
        
    if book_id:
        try:
            book_id = int(book_id)
            if book_id <= 0:
                raise ValueError()
            query = query.filter(Borrowed.book_id==book_id)
        except Exception as e:
            return jsonify({'error': f'Invalid book_id: book_id must be an integer and must be greater than 0 {e}'}), 400
    
    if borrow_date:
        try:
            if not re.match(date_check, borrow_date) and not re.match(date_check2, borrow_date):
                raise ValueError("Date must be in the format YYYY-MM-DD or YYYY/MM/DD.")
            borrow_date = parser.parse(borrow_date)
            if not (borrow_date.day and borrow_date.month and borrow_date.year):
                raise ValueError("Date must include day, month, and year.")
            query = query.filter(Borrowed.borrow_date >= borrow_date)
        except Exception as e:
            return jsonify({'error': f'Invalid borrow_date: borrow_date must be in YYYY-MM-DD format {e}'}), 400
        
    if due_date:
        try:
            if not re.match(date_check, due_date) and not re.match(date_check2, due_date):
                raise ValueError("Date must be in the format YYYY-MM-DD or YYYY/MM/DD.")
            due_date = parser.parse(due_date)
            if not (due_date.day and due_date.month and due_date.year):
                raise ValueError("Date must include day, month, and year.")
            query = query.filter(Borrowed.due_date >= due_date)
        except Exception as e:
            return jsonify({'error': f'Invalid due_date: due_date must be in YYYY-MM-DD format {e}'}), 400
    
    if return_date:
        try:
            if not re.match(date_check, return_date) and not re.match(date_check2, return_date):
                raise ValueError("Date must be in the format YYYY-MM-DD or YYYY/MM/DD.")
            return_date = parser.parse(return_date)
            if not (return_date.day and return_date.month and return_date.year):
                raise ValueError("Date must include day, month, and year.")
            query = query.filter(Borrowed.return_date >= return_date)
        except ValueError:
            return jsonify({'error': 'Invalid returned_date: return_date must be in YYYY-MM-DD format'}), 400
        
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
        
    query = query.order_by(Borrowed.return_date.desc())

    paginated_query = query.paginate(page=page, per_page=per_page, error_out=False)

    if (user_id or book_id or borrow_date or due_date or return_date or title or author or category or language or publisher) and not paginated_query.items:
        return jsonify({'error': 'No Returned books found matching the specified criteria'}), 404
    
    if not (user_id or book_id or borrow_date or due_date or return_date or title or author or category or language or publisher):
        if not paginated_query.items:
            return jsonify({'error': 'No Returned books found'}), 200
        
    total_books = paginated_query.total

    returned_books =[
        {
            "id": returned.id,
            "user_id": returned.user_id,
            "book_id": returned.book_id,
            "borrow_date": returned.borrow_date.date().isoformat(),
            "due_date": returned.due_date.date().isoformat(),
            "returned_date": returned.return_date.date().isoformat(),
            "book_title": returned.book.title,
            "damage_status": returned.damage,
            "damage_fine": returned.damage_fine,
            "fine_amount": returned.fine_amount,
            "total_fine": returned.total_fine
            
        } for returned in paginated_query.items
    ]

    return jsonify({
        'returned_books': returned_books,
        'total_result': total_books,
        'page': page,
        'per_page': per_page,
        'total_pages': paginated_query.pages
    }), 200

@return_bp.route('/return/<int:book_id>', methods=['GET'])
def get_specific_return(book_id):
    """
    Summary:
        Retrieve a paginated list of all returns for a specific book with optional filtering.

    Description:
        This endpoint retrieves a list of all returned instances of a specific book, identified by its `book_id`.
        The results can be filtered based on optional criteria such as user ID and date ranges.
        The endpoint also supports pagination through query parameters.
        The endpoint performs several validations and checks:
        - If `page` or `per_page` parameters are invalid (not positive integers), it returns a 400 error.
        - If filtering parameters (such as `user_id`, `borrow_date`, `due_date`, `return_date`) are invalid, it returns a 400 error.
        - If no results are found matching the specified criteria, it returns a 404 error.
        - If no filters are applied and no returns are found, it returns a 200 status with an empty list.
        - On successful retrieval, it returns a 200 status code with a paginated list of returned instances and metadata.
        
    Args:
        - `book_id` (int): The ID of the book whose returned instances are to be retrieved.

    Query Parameters:
        - `page` (int): The page number for pagination (default is 1).
        - `per_page` (int): The number of items per page (default is 10).
        - `user_id` (int): Filter by the ID of the user who borrowed the book.
        - `borrow_date` (str): Filter by the borrow date, must be in YYYY-MM-DD format.
        - `due_date` (str): Filter by the due date, must be in YYYY-MM-DD format.
        - `return_date` (str): Filter by the return date, must be in YYYY-MM-DD format.

    HTTP Response Codes:
        200 OK: If the request is successful and the returned book instances are retrieved.
        400 Bad Request: If the query parameters are invalid or in the wrong format.
        404 Not Found: If no returned instances are found matching the specified criteria.

    Returns:
        JSON: A paginated list of returned book including the total count, current page, items per page, and total pages.
        If no returned instances match the criteria or if no filters are applied and no returned books are found, the response will include appropriate messages.
    """
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    
    user_id = request.args.get('user_id', None)
    borrow_date = request.args.get('borrow_date', None)
    due_date = request.args.get('due_date', None)
    return_date = request.args.get('return_date', None)

    try:
        page = int(page)
        per_page = int(per_page)
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Page and per_page parameters must be positive integers'}), 400
    except Exception as e:
        return jsonify({'error': f'Page and per_page parameters must be integers {e}'}), 400
    
    query = Borrowed.query.filter_by(book_id=book_id).filter(Borrowed.return_date.isnot(None))

    if user_id:
        try:
            user_id = int(user_id)
            query = query.filter_by(user_id=user_id)
        except ValueError:
            return jsonify({'error': 'Invalid user_id: user_id must be an integer'}), 400
    
    if borrow_date:
        try:
            if not re.match(date_check, borrow_date) and not re.match(date_check2, borrow_date):
                raise ValueError("Date must be in the format YYYY-MM-DD or YYYY/MM/DD.")
            borrow_date = parser.parse(borrow_date)
            if not (borrow_date.day and borrow_date.month and borrow_date.year):
                raise ValueError("Date must include day, month, and year.")
            query = query.filter(Borrowed.borrow_date >= borrow_date)
        except Exception as e:
            return jsonify({'error': f'Invalid borrow_date: borrow_date must be in YYYY-MM-DD format {e}'}), 400
        
    if due_date:
        try:
            if not re.match(date_check, due_date) and not re.match(date_check2, due_date):
                raise ValueError("Date must be in the format YYYY-MM-DD or YYYY/MM/DD.")
            due_date = parser.parse(due_date)
            if not (due_date.day and due_date.month and due_date.year):
                raise ValueError("Date must include day, month, and year.")
            query = query.filter(Borrowed.due_date >= due_date)
        except Exception as e:
            return jsonify({'error': f'Invalid due_date: due_date must be in YYYY-MM-DD format {e}'}), 400
        
    if return_date:
        try:
            if not re.match(date_check, return_date) and not re.match(date_check2, return_date):
                raise ValueError("Date must be in the format YYYY-MM-DD or YYYY/MM/DD.")
            return_date = parser.parse(return_date)
            if not (return_date.day and return_date.month and return_date.year):
                raise ValueError("Date must include day, month, and year.")
            query = query.filter(Borrowed.return_date >= return_date)
        except Exception as e:
            return jsonify({'error': f'Invalid returned_date: return_date must be in YYYY-MM-DD format {e}'}), 400
        
    query = query.order_by(Borrowed.return_date.desc())
    
    paginated_query = query.paginate(page=page, per_page=per_page, error_out=False)

    if (user_id or borrow_date or due_date or return_date) and not paginated_query.items:
        return jsonify({'error': 'No Returned books found matching the specified criteria'}), 404
    
    if not (user_id or borrow_date or due_date or return_date):
        if not paginated_query.items:
            return jsonify({'error': 'No Returned books found'}), 200

    total_books = paginated_query.total   
    returned_books =[
        {
            "id": returned.id,
            "user_id": returned.user_id,
            "book_id": returned.book_id,
            "borrow_date": returned.borrow_date.date().isoformat(),
            "due_date": returned.due_date.date().isoformat(),
            "returned_date": returned.return_date.date().isoformat(),
            "book_title": returned.book.title,
            "damage_status": returned.damage,
            "damage_fine": returned.damage_fine,
            "fine_amount": returned.fine_amount,
            "total_fine": returned.total_fine
            
        } for returned in paginated_query.items
    ]

    return jsonify({
        'returned_books': returned_books,
        'total_result': total_books,
        'page': page,
        'per_page': per_page,
        'total_pages': paginated_query.pages
    }), 200

@return_bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    """
    Summary:
        Handle all unmatched routes and return a 404 error message.

    Description:
        This endpoint acts as a catch-all handler for any requests that do not match defined routes within the `return_bp` blueprint.
        It will respond to any HTTP methods (GET, POST, PUT, DELETE) for any path that is not explicitly defined in the blueprint.
        If a request is made to a URL that does not exist, it returns a 404 error with a message indicating that the requested URL was not found on the server.

    Args:
        path (str): The unmatched path part of the URL that was requested.

    HTTP response codes:
        404 NOT FOUND: The requested URL

    Returns:
        JSON: A JSON object containing an error message.
    """
    return jsonify({
        "error": "The requested URL was not found on the server. Please check your spelling and try again."
    }), 404