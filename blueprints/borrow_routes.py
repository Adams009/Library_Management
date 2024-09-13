from flask import Blueprint,jsonify, request
from models import *
from dateutil import parser
from werkzeug.exceptions import BadRequest
from sqlalchemy.sql import and_, or_
from email_validator import validate_email, EmailNotValidError

borrow_bp = Blueprint('borrow', __name__)

@borrow_bp.route('/books/<int:book_id>/borrow', methods=['POST'])
def borrow_book(book_id):
    """
    Summary:
        Borrow a book by its ID and return the borrow record in JSON format if successful; otherwise, return an error.

    Description:
        This endpoint creates a new borrow record for a specific book. It expects a JSON request body containing borrower details such as `user_id`, `username`, and `email`. The endpoint performs several validations and checks:
        
        - If the book is not found, it returns a 404 error indicating the book was not found.
        - If the book is not available for borrowing, it returns a 409 error indicating the book is already borrowed.
        - If the `user_id` is not provided or is invalid (not a positive integer), it returns a 400 error.
        - If the `username` is missing or does not match the provided `user_id`, it returns a 400 or 404 error.
        - If the `email` is missing or invalid, it returns a 400 error.
        - If the borrower's information does not match, it returns a 404 error.
        - On successful borrowing, it returns a 201 status code with the borrow record in JSON format.
        - If there is any error during the borrowing process, it returns a 500 error with a generic error message.

    Request Body (JSON):
        - `user_id` (int): The ID of the user borrowing the book.
        - `username` (str): The username of the user borrowing the book.
        - `email` (str): The email address of the user borrowing the book.

    Args:
        book_id (int): The ID of the book to borrow.

    HTTP Response Codes:
        201 Created: If the book is successfully borrowed and the borrow record is created.
        400 Bad Request: If the request body is missing required fields, or if the `user_id`, `username`, or `email` are invalid.
        404 Not Found: If the book or the borrower cannot be found.
        409 Conflict: If the book is not available or if the user has already borrowed the book without returning it.
        500 Internal Server Error: For any unexpected errors during the borrowing process.

    Returns:
        JSON: The borrow record in JSON format if the borrowing is successful; otherwise, an error message.
    """
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    try:
        data = request.get_json()
    except BadRequest as e:
         return jsonify({'error': 'Invalid JSON', 'message': str(e)}), 400
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    try:
        user_id = int(data.get('user_id'))
        if user_id <= 0:
            raise ValueError()
    except ValueError:
        return jsonify({'error': 'Invalid user_id: user_id must be an integer and greater than 0'}), 400
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'user not found'}), 404
    
    user_name = data.get('username')
    if not user_name:
        return jsonify({'error': 'username is required'}), 400
    
    borrower = User.query.filter_by(username=user_name, id=user_id).first()
    if not borrower:
        return jsonify({'error': 'user not found: id and username not tally'}), 404
    
    try:
        validate_email(data.get('email'))
        borrower_email = data.get('email')
    except EmailNotValidError as e:
        return jsonify({f'error : Invalid email address: {e}'}), 400
    
    if not borrower_email:
        return jsonify({'error': 'email is required'}), 400
    
    borrower = User.query.filter_by(username=user_name, id=user_id, email_address=borrower_email).first()
    if not borrower:
        return jsonify({'error': 'user not found: id, username, and email not tally'}), 404
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    if not book.available:
        return jsonify({'error': 'Book is not available'}), 409
    
    check = Borrowed.query.filter_by(user_id=user_id, book_id=book_id, returned_date=None).first()
    
    if check:
        return jsonify({'error': 'You already borrowed this book and have not returned it'}), 409
    
    borrow_record = Borrowed(book_id=book_id, user_id=user_id)
    book.available_copies -= 1
    book.update_availability()
    
    db.session.add(borrow_record)
    db.session.commit()
    
    return jsonify(borrow_record.borrowed_serialize()), 201

@borrow_bp.route('/books/borrow', methods=['GET'])
def get_all_borrowed():
    """
    Summary:
        Retrieve a list of all borrowed books or a specific borrowed book based on provided parameters and return it in JSON format.

    Description:
        This endpoint retrieves information about borrowed books from the database. It can return either a list of all borrowed books or filter the results based on provided parameters. The response is in JSON format, including details about each borrowed book.

        Optional Query Parameters:
        - `page` (int): The page number to return (default is 1).
        - `per_page` (int): The number of borrowed books per page to return (default is 10).
        - `user_id` (int): Filter borrowed books by user ID.
        - `book_id` (int): Filter borrowed books by book ID.
        - `borrow_date` (string): Filter borrowed books by borrow date (format: YYYY-MM-DD).
        - `due_date` (string): Filter borrowed books by due date (format: YYYY-MM-DD).
        - `returned_date` (string): Filter borrowed books by returned date (format: YYYY-MM-DD).
        - `title` (string): Filter borrowed books by book title.
        - `author` (string): Filter borrowed books by book author.
        - `category` (string): Filter borrowed books by book category.
        - `publisher` (string): Filter borrowed books by book publisher.
        - `language` (string): Filter borrowed books by book language.

    HTTP Response Codes:
        200 OK: If borrowed books are found and returned successfully.
        400 Bad Request: If any of the parameters are invalid or incorrectly formatted.
        404 Not Found: If no borrowed books match the specified criteria.
    
    Returns:
        JSON: A JSON object containing a list of borrowed books with details such as book ID, user ID, borrow date, due date, returned date, book title, author, and other relevant details. Includes pagination information if applicable.
    """

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
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
    except ValueError:
        return jsonify({'error': 'Page and per_page parameters must be integers'}), 400
        
    query = Borrowed.query.join(Book)
    
    if user_id:
        try:
            user_id = int(user_id)
            if user_id <= 0:
                raise ValueError()
            query = query.filter_by(user_id=user_id)
        except ValueError:
            return jsonify({'error': 'Invalid user_id: user_id must be an integer and must be greater than 0'}), 400
    
    if book_id:
        try:
            book_id = int(book_id)
            if book_id <= 0:
                raise ValueError()
            query = query.filter_by(book_id=book_id)
        except ValueError:
            return jsonify({'error': 'Invalid book_id: book_id must be an integer and must be greater than 0'}), 400
    
    if borrow_date:
        try:
            borrow_date = parser.parse(borrow_date)
            query = query.filter(Borrowed.borrow_date >= borrow_date)
        except ValueError:
            return jsonify({'error': 'Invalid borrow_date: borrow_date must be in YYYY-MM-DD format'}), 400
        
    if due_date:
        try:
            due_date = parser.parse(due_date)
            query = query.filter(Borrowed.due_date >= due_date)
        except ValueError:
            return jsonify({'error': 'Invalid due_date: due_date must be in YYYY-MM-DD format'}), 400
    
    if return_date:
        try:
            return_date = parser.parse(return_date)
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

    
    query = query.order_by(Borrowed.borrow_date.desc())
    
    paginated_query = query.paginate(page=page, per_page=per_page, error_out=False)

    if (user_id or book_id or borrow_date or due_date or return_date or title or author or category or language or publisher) and not paginated_query.items():
        return jsonify({'error': 'No borrowed books found matching the specified criteria'}), 404
    
    if not (user_id or book_id or borrow_date or due_date or return_date or title or author or category or language or publisher):
        if not paginated_query.items():
            return jsonify({'error': 'No borrowed books found'}), 200
    
    total_books = paginated_query.count()
    borrowed_books =[
        {
            'id': borrowed.id,
            'book_id': borrowed.book_id,
            'user_id': borrowed.user_id,
            'borrow_date': borrowed.borrow_date.strftime('%Y-%m-%d'),
            'due_date': borrowed.due_date.strftime('%Y-%m-%d'),
            'returned_date': borrowed.return_date.strftime('%Y-%m-%d') if borrowed.return_date else None,
            'title': borrowed.book.title,
            'author': borrowed.book.author,
            'year': borrowed.book.year,
            'isbn': borrowed.book.isbn,
            'language': borrowed.book.language,
            'category': borrowed.book.category,
            'publisher': borrowed.book.publisher,
            'available': borrowed.book.available,
            'cover_image_url': borrowed.book.cover_image_url
        } for borrowed in paginated_query.items()
    ]

    return jsonify({
        'borrowed_books': borrowed_books,
        'total_result': total_books,
        'page': page,
        'per_page': per_page,
        'total_pages': paginated_query.pages
    })


@borrow_bp.route('books/<int:book_id>/borrow', methods=['GET'])
def get_specific_borrowed_book(book_id):
    """
    Summary:
        Retrieve a specific borrowed book by its book ID and return it in JSON format.

    Description:
        This endpoint retrieves information about a specific borrowed book based on the provided book ID. It can also filter the results based on additional query parameters such as user ID, borrow date, due date, and return date. The response is returned in JSON format, including details about the borrowed book.

    Optional Query Parameters:
        - `page` (int): The page number of results to return (default is 1).
        - `per_page` (int): The number of borrowed book records per page (default is 10).
        - `user_id` (int): Filter borrowed books by user ID.
        - `borrow_date` (string): Filter borrowed books by borrow date (format: YYYY-MM-DD).
        - `due_date` (string): Filter borrowed books by due date (format: YYYY-MM-DD).
        - `return_date` (string): Filter borrowed books by return date (format: YYYY-MM-DD).

    Args:
        book_id (int): The unique identifier for the book.

    HTTP Response Codes:
        200 OK: If borrowed books are found and returned successfully.
        400 Bad Request: If any of the parameters are invalid or incorrectly formatted.
        404 Not Found: If no borrowed books matching the specified criteria are found.

    Returns:
        JSON: A JSON object containing details about the borrowed book(s) including the book ID, user ID, borrow date, due date, returned date, and other relevant book details. Includes pagination information if applicable.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    user_id = request.args.get('user_id', None)
    borrow_date = request.args.get('borrow_date', None)
    due_date = request.args.get('due_date', None)
    return_date = request.args.get('return_date', None)

    try:
        page = int(page)
        per_page = int(per_page)
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Page and per_page parameters must be positive integers'}), 400
    except ValueError:
        return jsonify({'error': 'Page and per_page parameters must be integers'}), 400
    
    query = Borrowed.query.filter_by(book_id=book_id)
    
    if user_id:
        try:
            user_id = int(user_id)
            query = query.filter_by(user_id=user_id)
        except ValueError:
            return jsonify({'error': 'Invalid user_id: user_id must be an integer'}), 400
    
    if borrow_date:
        try:
            borrow_date = parser.parse(borrow_date)
            query = query.filter(Borrowed.borrow_date >= borrow_date)
        except ValueError:
            return jsonify({'error': 'Invalid borrow_date: borrow_date must be in YYYY-MM-DD format'}), 400
        
    if due_date:
        try:
            due_date = parser.parse(due_date)
            query = query.filter(Borrowed.due_date >= due_date)
        except ValueError:
            return jsonify({'error': 'Invalid due_date: due_date must be in YYYY-MM-DD format'}), 400
        
    if return_date:
        try:
            return_date = parser.parse(return_date)
            query = query.filter(Borrowed.return_date >= return_date)
        except ValueError:
            return jsonify({'error': 'Invalid returned_date: return_date must be in YYYY-MM-DD format'}), 400
        
    query = query.order_by(Borrowed.borrow_date.desc())
    
    paginated_query = query.paginate(page=page, per_page=per_page, error_out=False)

    if (user_id or borrow_date or due_date or return_date) and not paginated_query.items():
        return jsonify({'error': 'No borrowed books found matching the specified criteria'}), 404
    
    if not (user_id or borrow_date or due_date or return_date):
        if not paginated_query.items():
            return jsonify({'error': 'No borrowed books found'}), 200
        
    borrowed_books =[
        {
            'id': borrowed.id,
            'book_id': borrowed.book_id,
            'user_id': borrowed.user_id,
            'borrow_date': borrowed.borrow_date.strftime('%Y-%m-%d'),
            'due_date': borrowed.due_date.strftime('%Y-%m-%d'),
            'returned_date': borrowed.return_date.strftime('%Y-%m-%d') if borrowed.return_date else None,
            'title': borrowed.book.title,
            'author': borrowed.book.author,
            'year': borrowed.book.year,
            'isbn': borrowed.book.isbn,
            'language': borrowed.book.language,
            'category': borrowed.book.category,
            'publisher': borrowed.book.publisher,
            'available': borrowed.book.available,
            'cover_image_url': borrowed.book.cover_image_url
            } for borrowed in paginated_query.items()
            ]
    
    return jsonify({
        'borrowed_books': borrowed_books,
        'total_result': paginated_query.total,
        'page': page,
        'per_page': per_page,
        'total_pages': paginated_query.pages
    }), 200

borrow_bp.route('/books/borrow/unreturned/', methods=['GET'])
def get_unreturned_books():
    """
    Summary:
        Retrieve all unreturned borrowed books from the database and return them in JSON format.

    Description:
        This endpoint fetches all borrowed books that have not been returned yet. It supports filtering based on various optional query parameters such as title, author, category, publisher, language, user ID, book ID, borrow date, and due date. The results are returned in a paginated JSON format.

    Optional Query Parameters:
        - `page` (int): The page number of results to retrieve (default is 1).
        - `per_page` (int): The number of borrowed book records per page (default is 10).
        - `title` (string): Filter unreturned books by title.
        - `author` (string): Filter unreturned books by author.
        - `category` (string): Filter unreturned books by category.
        - `publisher` (string): Filter unreturned books by publisher.
        - `language` (string): Filter unreturned books by language.
        - `user_id` (int): Filter unreturned books by user ID.
        - `book_id` (int): Filter unreturned books by book ID.
        - `borrow_date` (string): Filter unreturned books by borrow date (format: YYYY-MM-DD).
        - `due_date` (string): Filter unreturned books by due date (format: YYYY-MM-DD).

    HTTP Response Codes:
        200 OK: If unreturned borrowed books are found and returned successfully.
        400 Bad Request: If any of the parameters are invalid or incorrectly formatted.
        404 Not Found: If no unreturned borrowed books matching the specified criteria are found.

    Returns:
        JSON: A JSON object containing details about the unreturned borrowed books, including the book ID, user ID, borrow date, due date, returned date (if applicable), and other relevant book details. Includes pagination information if applicable.
    """

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    title = request.args.get('title', None)
    author = request.args.get('author', None)
    category = request.args.get('category', None)
    publisher = request.args.get('publisher', None)
    language = request.args.get('language', None)
    user_id = request.args.get('user_id', None)
    book_id = request.args.get('book_id', None)
    borrow_date = request.args.get('borrow_date', None)
    due_date = request.args.get('due_date', None)

    try:
        page = int(page)
        per_page = int(per_page)
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Page and per_page parameters must be positive integers'}), 400
    except ValueError:
        return jsonify({'error': 'Page and per_page parameters must be integers'}), 400
        
    query = Borrowed.query.join(Book).filter(Borrowed.return_date.is_(None))
    
    if user_id:
        try:
            user_id = int(user_id)
            if user_id <= 0:
                raise ValueError()
            query = query.filter(Borrowed.user_id == user_id)
        except ValueError:
            return jsonify({'error': 'Invalid user_id: user_id must be an integer and must be greater than 0'}), 400
    
    if book_id:
        try:
            book_id = int(book_id)
            if book_id <= 0:
                raise ValueError()
            query = query.filter(Borrowed.book_id==book_id)
        except ValueError:
            return jsonify({'error': 'Invalid book_id: book_id must be an integer and must be greater than 0'}), 400
    
    if borrow_date:
        try:
            borrow_date = parser.parse(borrow_date)
            query = query.filter(Borrowed.borrow_date == borrow_date)
        except ValueError:
            return jsonify({'error': 'Invalid borrow_date: borrow_date must be in YYYY-MM-DD format'}), 400
        
    if due_date:
        try:
            due_date = parser.parse(due_date)
            query = query.filter(Borrowed.due_date == due_date)
        except ValueError:
            return jsonify({'error': 'Invalid due_date: due_date must be in YYYY-MM-DD format'}), 400
        
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

    query = query.order_by(Borrowed.borrow_date.desc())

    paginated_query = query.paginate(page=page, per_page=per_page, error_out=False)

    if not paginated_query.items():
        if any([user_id, book_id, borrow_date, due_date, title, author, category, publisher, language]):
             return jsonify({'error': 'No unreturned borrowed books found matching the specified criteria'}), 404
        else:
             return jsonify({'error': 'No unreturned borrowed books found'}), 200
        
    total_books = paginated_query.count()
    borrowed_books =[
        {
            'id': borrowed.id,
            'book_id': borrowed.book_id,
            'user_id': borrowed.user_id,
            'borrow_date': borrowed.borrow_date.strftime('%Y-%m-%d'),
            'due_date': borrowed.due_date.strftime('%Y-%m-%d'),
            'returned_date': borrowed.return_date.strftime('%Y-%m-%d') if borrowed.return_date else None,
            'title': borrowed.book.title,
            'author': borrowed.book.author,
            'year': borrowed.book.year,
            'isbn': borrowed.book.isbn,
            'language': borrowed.book.language,
            'category': borrowed.book.category,
            'publisher': borrowed.book.publisher,
            'available': borrowed.book.available,
            'cover_image_url': borrowed.book.cover_image_url
        } for borrowed in paginated_query.items()
    ]

    return jsonify({
        'borrowed_books': borrowed_books,
        'total_result': total_books,
        'page': page,
        'per_page': per_page,
        'total_pages': paginated_query.pages
    })
    
@borrow_bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    """
    Summary:
        Handle all unmatched routes and return a 404 error message.

    Description:
        This endpoint serves as a catch-all handler for any requests that do not match the explicitly defined routes within the `borrow_bp` blueprint. It is invoked for any HTTP method (GET, POST, PUT, DELETE) and any path that is not explicitly defined in the blueprint. It returns a 404 Not Found error with a message indicating that the requested URL was not found on the server.

    Args:
        path (str): The unmatched path part of the URL that was requested.

    HTTP Response Codes:
        404 Not Found: Returned when the requested URL does not match any defined route in the blueprint.

    Returns:
        JSON: A JSON object containing an error message with the following structure:
        - `error` (string): A message indicating that the requested URL was not found on the server and suggesting checking the spelling and trying again.
    """
    return jsonify({
        "error": "The requested URL was not found on the server. Please check your spelling and try again."
    }), 404
    # unreturned_books = Borrowed.query.filter_by(return_date=None).all()
