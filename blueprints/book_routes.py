from flask import Blueprint,jsonify, request
from models import *
from werkzeug.exceptions import BadRequest

books_bp = Blueprint('books', __name__)

@books_bp.route('/books', methods=['GET'])
def get_books():
    """
    Summary:
         Retrieves a list of books from the database, with optional filtering and pagination. If no specific parameters are provided, returns all books. If filtering parameters are provided, returns books that match those criteria.

    Description:
        This endpoint fetches all books or a specific book based on the parameters provided. It returns a paginated list of books in JSON format. If no books are found or if there is an error in the provided parameters, an appropriate error message is returned.    
    
    Optional Query Parameters:
        page: The page number of the books to be returned
        per_page: The number of books per page to be returned
        title: The title of the book to be returned
        author: The author of the book to be returned
        year: The year of publication of the book to be returned
        isbn: The ISBN of the book to be returned
        available: Whether the book is available for borrowing (true/false)
        language: The language of the book to be returned
        category: The category of the book to be returned
        publisher: The publisher of the book to be returned
        
    HTTP response codes:
        - 200: If successful, returns a paginated list of books in JSON format
        - 400: If the request parameters are invalid, returns an error message

    Errors:
       If parameters are invalid
    
    Returns:
        JSON: A JSON representation of the book or books in the database or a specific book in JSON format if successful otherwise returns an error
    """

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    title = request.args.get('title', None)
    author = request.args.get('author', None)
    year = request.args.get('year', None)
    isbn = request.args.get('isbn', None)
    available = request.args.get('available', None)
    language = request.args.get('language', None)
    category = request.args.get('category', None)
    publisher = request.args.get('publisher', None)

    try:
        page = int(page)
        per_page = int(per_page)
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Page and per_page parameters must be positive integers'}), 400
    except ValueError:
        return jsonify({'error': 'Page and per_page parameters must be integers'}), 400

    query = Book.query

    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))

    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))

    if year:
        try:
            query = query.filter(Book.year == int(year))
        except ValueError:
            return jsonify({'error': 'Year must be an integer'}), 400

    if isbn:
        query = query.filter(Book.isbn == isbn)

    if available:
        if available.lower() in ['true', 'false']:
            query = query.filter(Book.available == (available.lower() == 'true'))
        else:
            return jsonify({'error': 'Available must be true or false'}), 400
    
    if language:
        query = query.filter(Book.language.ilike(f'%{language}%'))

    if category:
        query = query.filter(Book.category.ilike(f'%{category}%'))

    if publisher:
        query = query.filter(Book.publisher.ilike(f'%{publisher}%'))

    books = query.paginate(page=page, per_page=per_page, error_out=False)

    if (title or author or year or isbn or available or language or category or publisher) and not books.items:
        return jsonify({'message': 'No books found matching the given criteria'}), 200
    
    if not (title or author or year or isbn or available or language or category or publisher):
        if not books.items:
            return jsonify({'message': 'No books found'}), 200
        
    total = query.count()
    data = [book.book_serialize() for book in books.items]
    return jsonify({'total_result': total, 'page': page, 'per_page': per_page, 'books': data, 'total_pages': books.pages}), 200


@books_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    Summary:
       Retrieves a specific book by its ID from the database and returns its details in JSON format.

     Description:
        This endpoint fetches a book from the database using the provided book ID. If the book exists, it returns the book's details in JSON format with a 200 status code. If the book is not found, it returns a 404 error with an appropriate message.

    Args:
        book_id (int): The ID of the book to retrieve.

    HTTP response codes:
    - 200: If successful, returns the book's details in JSON format
    - 404: If the book is not found, returns a 404 error with an appropriate message

    Errors:
        Book not found

    Returns:
        JSON: The book's details in JSON format if it exists otherwise error message.
    """
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(book.book_serialize()), 200

@books_bp.route('/books', methods=['POST'])
def add_book():
    """
    Summary:
        Adds a new book to the database and returns the book's details in JSON format if successful. 

    Description:
        This endpoint allows the addition of a new book to the database. It expects a JSON request body containing the book's details, including title, author, year, ISBN, available copies, total copies, publisher, language, and category. Optionally, a cover image URL can also be provided. 

        - If any required fields are missing or the data is invalid, it returns a 400 error with a specific message indicating the issue.
        - If the book already exists in the database (based on ISBN), it returns a 409 error indicating the conflict.
        - If the book is successfully added, it returns a 201 status code with the book's details in JSON format.
        - In case of other errors, it returns a 500 error with a generic error message.

    Rquest Body:
        JSON Body:
        - title (str): The title of the book.
        - author (str): The author of the book.
        - year (int): The publication year of the book.
        - isbn (str): The ISBN of the book.
        - available_copies (int): The number of available copies of the book.
        - total_copies (int): The total number of copies of the book.
        - language (str): The language of the book.
        - category (str): The category of the book.
        - publisher (str): The publisher of the book.
        - cover_image_url (str, optional): The URL of the book's cover image.

    HTTP response codes:
        201 Created
        400 Bad Request
        409 Conflict
        500 Internal Server Error

    Returns:
        JSON: The book's details in JSON format if it exists otherwise error message.
    """
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    try:
        data = request.get_json()
    except BadRequest as e:
        return jsonify({'error': 'Invalid JSON', 'message': str(e)}), 400
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['title', 'author', 'year', 'isbn', 'available_copies', 'total_copies', 'publisher', 'language', 'category']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
        
    title = data.get('title')
    author = data.get('author')
    year = data.get('year')
    isbn = data.get('isbn')
    available = data.get('available', None)
    available_copies = data.get('available_copies')
    total_copies = data.get('total_copies')
    language = data.get('language')
    category = data.get('category')
    publisher = data.get('publisher')
    cover_image_url = data.get('cover_image_url', None)
    
    try:
        year = int(year)
        available_copies = int(available_copies)
        total_copies = int(total_copies)
    except ValueError:
        return jsonify({'error': 'Year, available_copies, and total_copies must be integers'}), 400
    
    if available:
        if available.lower() in ['true', 'false']:
            available = available.lower() == 'true'
        else:
            return jsonify({'error': 'Available must be true or false'}), 400
    
    if total_copies < available_copies:
        return jsonify({'error': 'Total copies must be greater than or equal to available copies'}), 400
    
    if Book.query.filter_by(isbn=data['isbn']).first():
        return jsonify({'error': 'Book already exists'}), 409
    
    book = Book(title=title, author=author, year=year, isbn=isbn, available=available, available_copies=available_copies, total_copies=total_copies, language=language, category=category, publisher=publisher, cover_image_url=cover_image_url)
    book.update_availability()

    try:
        db.session.add(book)
        db.session.commit()

        message = book.book_serialize()
        message['a_message'] = "Book added successfully"

        return jsonify(message), 201
    except Exception as e:
        db.session.rollback()  # Rollback session on error
        return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500


@books_bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Summary:
       Updates an existing book in the database and returns the updated book details in JSON format if successful.

    Description:
        This endpoint allows updating the details of an existing book in the database. It expects a JSON request body containing the details to be updated, including title, author, year, ISBN, available status, available copies, total copies, language, category, and publisher. Optionally, a cover image URL can also be updated.

        - If any of the provided fields are the same as the current values, it returns a 409 error indicating no changes were made for those fields.
        - If the book is not found by the provided ID, it returns a 404 error.
        - If the updated available copies exceed the total copies, it returns a 400 error.
        - On successful update, it returns a 200 status code with the updated book details.
        - If there is an error during the update process, it returns a 500 error with a generic error message. 
    
    Request Body (JSON):
        - title (str, optional): The new title of the book.
        - author (str, optional): The new author of the book.
        - year (int, optional): The new publication year of the book.
        - isbn (str, optional): The new ISBN of the book.
        - available (bool, optional): The new availability status of the book (true/false).
        - available_copies (int, optional): The new number of available copies of the book.
        - total_copies (int, optional): The new total number of copies of the book.
        - language (str, optional): The new language of the book.
        - category (str, optional): The new category of the book.
        - publisher (str, optional): The new publisher of the book.
        - cover_image_url (str, optional): The new URL of the book's cover image.

    Args:
        book_id (int): The ID of the book to update.

    HTTP response codes:
        200 OK
        400 Bad Request
        409 Conflict
        500 Internal Server Error
    
    Returns:
        JSON: The updated book's details in JSON format if it exists otherwise error message.
    """
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    try:
        data = request.get_json()
    except BadRequest as e:
        return jsonify({'error': 'Invalid JSON', 'message': str(e)}), 400
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    updated_details = {}
    
    if data.get('title'):
        if data.get('title') != book.title:
            book.title = data['title']
            updated_details['title'] = book.title
        else:
            return jsonify({'error': 'New Book title is the same as the current book title'}), 409

    if data.get('author'):
        if data.get('author') != book.author:
            book.author = data['author']
            updated_details['author'] = book.author
        else:
            return jsonify({'error': 'New Book author is the same as the current book author'}), 409

    if data.get('year'):
        try:
            year = int(data['year'])
            if year != book.year:
                book.year = year
                updated_details['year'] = year
            else:
                return jsonify({'error': 'New Book year is the same as the current book year'}), 409
        except ValueError:
            return jsonify({'error': 'Year must be an integer'}), 400

    if data.get('isbn'):
        if data.get('isbn') != book.isbn:
            book.isbn = data['isbn']
            updated_details['isbn'] = book.isbn
        else:
            return jsonify({'error': 'New Book ISBN is the same as the current book ISBN'}), 409

    if data.get('available'):
        availability = data['available']
        
        if availability != book.available:
            if availability.lower() in ["true", "false"]:
                book.available = availability.lower() == 'true'
                updated_details['available'] = availability.lower() == 'true'
            else:
                return jsonify({'error': 'Available must be true or false'}), 400
        else:
            return jsonify({'error': 'New Book availability is the same as the current book availability'}), 409

    if data.get('available_copies'):
        try:
            available_copy = int(data['available_copies'])
            if available_copy != book.available_copies:
                book.available_copies = available_copy
                updated_details['available_copies'] = available_copy
            else:
                return jsonify({'error': 'New Book available copies is the same as the current book available copies'}), 409

        except ValueError:
            return jsonify({'error': 'Available copies must be an integer'}), 400

    if data.get('total_copies'):
        try:
            total_copy = int(data['total_copies'])

            if total_copy != book.total_copies:
                book.total_copies = total_copy
                updated_details['total_copies'] = total_copy
            else:
                return jsonify({'error': 'New Book total copies is the same as the current book total copies'}), 409
                                                 
        except ValueError:
            return jsonify({'error': 'Total copies must be an integer'}), 400

    if data.get('language'):
        if data.get('language') != book.language:
            book.language = data['language']
            updated_details['language'] = book.language
        else:
            return jsonify({'error': 'New Book language is the same as the current book language'}), 409

    if data.get('category'):
        if data.get('category') != book.category:
            book.category = data['category']
            updated_details['category'] = book.category
        else:
            return jsonify({'error': 'New Book category is the same as the current book category'}), 409

    if data.get('publisher'):
        if data.get('publisher') != book.publisher:
            book.publisher = data['publisher']
            updated_details['publisher'] = book.publisher
        else:
            return jsonify({'error': 'New Book publisher is the same as the current book publisher'}), 409
    
    if data.get('cover_image_url'):
        if data.get('cover_image_url') != book.cover_image_url:
            book.cover_image_url = data['cover_image_url']
            updated_details['cover_image_url'] = book.cover_image_url
        else:
            return jsonify({'error': 'cover_image_url is the same as current cover_image_url'}), 409

    if updated_details is None:
        return jsonify({'mesaage': 'No changes made'}), 200
    
    if 'available_copies' in updated_details or 'total_copies' in updated_details:
        if book.total_copies < book.available_copies:
            return jsonify({'error': 'Total copies must be greater than or equal to available copies'}), 400
        else:
            book.update_availability()
    
    updated_details['book_id'] = book.id
    try:
        db.session.commit()
    
        return jsonify({
            "a_message": "Details updated successfully",
            "updated_fields": updated_details
        }), 200
    except Exception as e:
        db.session.rollback()  # Rollback session on error
        return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500

@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Summary:
        Deletes a book from the database by its ID and returns a confirmation message if successful.

    Description:
        This endpoint deletes a book identified by the given ID from the database. 
        If the book with the specified ID is not found, it returns a 404 error with a message indicating that the book was not found.
        If the deletion is successful, it returns a 200 status code with a confirmation message including the book's ID, title, and author.
        In case of any error during the deletion process, it returns a 500 error with a generic error message. 
    
    Args:
        book_id (int): The ID of the book to delete.

    HTTP response codes:
        200 OK
        404 Not Found
        500 Internal Server Error

    Returns:
        JSON: A confirmation message if the book is deleted successfully otherwise error message.
    """
    id = book_id
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    title = book.title
    author = book.author
    
    try:
        db.session.delete(book)
        db.session.commit()
    
        return jsonify({
            "book_id": id,
            "title": title,
            "author": author,
            "a_message": "Book deleted successfully"
        }), 200
    except Exception as e:
        db.session.rollback()  # Rollback session on error
        return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500

@books_bp.route('/books/<int:book_id>/availability', methods=['GET'])
def check_availability(book_id):
    """
    Summary:
        Checks the availability status of a book by its ID and returns the status in JSON format if successful.

    Description:
        This endpoint retrieves the availability status of a book identified by the given ID from the database.
        If the book with the specified ID is not found, it returns a 404 error with a message indicating that the book was not found.
        If the book is found, it returns a 200 status code with the availability status, including details such as ID, title, author, year, and ISBN, in JSON format.
        In case of any error retrieving the book, it returns a 500 error with a generic error message.

    Args:
        book_id (int): The ID of the book to check availability.

    HTTP response codes:
        200 OK
        404 Not Found

    Returns:
        JSON: The availability status of the book in JSON format if it exists otherwise error message.
    """
    book = Book.query.get(book_id)

    if not book:
        return jsonify({'error': 'Book not found.'}), 404
    
    availability_status = {
        'id': book.id,
        'title': book.title,
        'available': book.available,
        'author': book.author,
        'year': book.year,
        'isbn': book.isbn
        }
    
    return jsonify(availability_status), 200

@books_bp.route('/books/availability', methods=['GET'])
def all_availability():
    """
    Summary:
       Retrieve the availability status of all books or filter by specific criteria and return it in JSON format.

    Description:
        This endpoint retrieves the availability status of all books from the database or filters books based on provided parameters.
        If the request includes filters and no books match the criteria, it returns a 404 error with a message indicating no books were found.
        If no filters are provided and no books are found, it returns a 200 status code with a message indicating no books were found.
        If books are found, it returns a 200 status code with a JSON object containing the availability status of the books, along with pagination information. 

    Optional Query Parameters:
        - page: The page number to return (default is 1).
        - per_page: The number of books per page (default is 10).
        - title: Filter books by title.
        - author: Filter books by author.
        - year: Filter books by publication year.
        - isbn: Filter books by ISBN.
        - available: Filter books by availability (true/false).
        - language: Filter books by language.
        - category: Filter books by category.
        - publisher: Filter books by publisher.
        
    HTTP response codes:
        400 Bad Request
        200 OK

    Returns:
        JSON: A JSON object containing all books' availability status if successful otherwise error message.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    title = request.args.get('title', None)
    author = request.args.get('author', None)
    year = request.args.get('year', None)
    isbn = request.args.get('isbn', None)
    available = request.args.get('available', None)
    language = request.args.get('language', None)
    category = request.args.get('category', None)
    publisher = request.args.get('publisher', None)

    try:
        page = int(page)
        per_page = int(per_page)
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Page and per_page parameters must be positive integers'}), 400
    except ValueError:
        return jsonify({'error': 'Page and per_page parameters must be integers'}), 400

    query = Book.query

    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))

    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))

    if year:
        try:
            query = query.filter(Book.year == int(year))
        except ValueError:
            return jsonify({'error': 'Year must be an integer'}), 400

    if isbn:
        query = query.filter(Book.isbn == isbn)

    if available:
        if available.lower() in ['true', 'false']:
            query = query.filter(Book.available == (available.lower() == 'true'))
        else:
            return jsonify({'error': 'Available must be true or false'}), 400
    
    if language:
        query = query.filter(Book.language.ilike(f'%{language}%'))

    if category:
        query = query.filter(Book.category.ilike(f'%{category}%'))

    if publisher:
        query = query.filter(Book.publisher.ilike(f'%{publisher}%'))

    books = query.paginate(page=page, per_page=per_page, error_out=False)

    if (title or author or year or isbn or available or language or category or publisher) and not books.items:
        return jsonify({'message': 'No books found matching the given criteria'}), 200
    
    if not (title or author or year or isbn or available or language or category or publisher):
        if not books.items:
            return jsonify({'message': 'No books found'}), 200
        
    total = query.count()
    data = [
        {
            'id': book.id,
            'title': book.title,
            'available': book.available,
            'author': book.author,
            'year': book.year,
            'isbn': book.isbn
        } for book in books.items
    ]
    
    response = {
        'total_items': books.total,
        'page': page,
        'per_page': per_page,
        'total_pages': books.pages,
        'books': data
    }

    return jsonify(response), 200

@books_bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    """
    Summary:
        Handle all unmatched routes and return a 404 error message.

    Description:
        This endpoint acts as a catch-all handler for any requests that do not match defined routes within the `books_bp` blueprint.
        It will respond to any HTTP methods (GET, POST, PUT, DELETE) for any path that is not explicitly defined in the blueprint.
        If a request is made to a URL that does not exist, it returns a 404 error with a message indicating that the requested URL was not found on the server.

    Args:
        path (str): The unmatched path part of the URL that was requested.

    HTTP response codes:
        404 NOT FOUND: The requested URL

    Returns:
        JSON: A JSON object containing an error message with the following structure:
    """
    return jsonify({
        "error": "The requested URL was not found on the server. Please check your spelling and try again."
    }), 404