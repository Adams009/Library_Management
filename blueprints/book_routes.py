from flask import Blueprint,jsonify, request
from models import *
from dateutil import parser
from datetime import datetime, timedelta
from werkzeug.exceptions import BadRequest

books_bp = Blueprint('books', __name__)

@books_bp.route('/books', methods=['GET'])
def get_books():
    """
    Summary:
        Get all books in the database or a specific book by parameter provided and return a list of books or book in JSON format if successful otherwise returns an error
            Description:
        This endpoint retrieves a all books or a specific book by its given parameter from the database and returns it in JSON format.
    Optional Parameters:
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
        return jsonify({'error': 'No books found matching the given criteria'}), 404
    
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
        Get a specific book by ID and return it in JSON format if successful otherwise returns an error
            Description:
        This endpoint retrieves a specific book by its ID from the database and returns it in JSON format.
        If the book is not found, it returns a 404 error with a message indicating that the book was not found.
        If the book is found, it returns a 200 status code with the book's details in JSON format.

    Args:
        book_id (int): The ID of the book to retrieve.

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
        Add a new book to the database and return it in JSON format if successful otherwise returns an error
            Description:
        This endpoint adds a new book to the database. It expects a JSON request body containing the book details.
        The book details include title, author, year, isbn, available, language, category, and publisher.
        If any of the required fields are missing, it returns a 400 error with a message indicating the missing field.
        If the book is successfully added, it returns a 201 status code with the book's details in JSON format.
        If the book already exists in the database, it returns a 409 error with a message indicating that the book already exists.
        If there is an error adding the book, it returns a 500 error with a generic error message.
    
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

    db.session.add(book)
    db.session.commit()

    message = book.book_serialize()
    message['a_message'] = "Book added successfully"

    return jsonify(message), 201

@books_bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Summary:
        Update an existing book in the database and return it in JSON format if successful otherwise returns an error
            Description:
        This endpoint updates an existing book in the database. It expects a JSON request body containing the book details to update.
        The book details to update include title, author, year, isbn, available, language, category, and publisher.
        If any of the required fields are missing, it returns a 400 error with a message indicating the missing field.
        If the book is not found, it returns a 404 error with a message indicating that the book was not found.
        If the book is successfully updated, it returns a 200 status code with the updated book's details in JSON format.
        If there is an error updating the book, it returns a 500 error with a generic error message.
    
    Args:
        book_id (int): The ID of the book to update.

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
            return jsonify({'error': 'New Book title is the same as the current book title'})

    if data.get('author'):
        if data.get('author') != book.author:
            book.author = data['author']
            updated_details['author'] = book.author
        else:
            return jsonify({'error': 'New Book author is the same as the current book author'})

    if data.get('year'):
        try:
            year = int(data['year'])
            if year != book.year:
                book.year = year
                updated_details['year'] = year
            else:
                return jsonify({'error': 'New Book year is the same as the current book year'})
        except ValueError:
            return jsonify({'error': 'Year must be an integer'}), 400

    if data.get('isbn'):
        if data.get('isbn') != book.isbn:
            book.isbn = data['isbn']
            updated_details['isbn'] = book.isbn
        else:
            return jsonify({'error': 'New Book ISBN is the same as the current book ISBN'})

    if data.get('available'):
        availability = data['available']
        
        if availability != book.available:
            if availability.lower() in ["true", "false"]:
                book.available = availability.lower() == 'true'
                updated_details['available'] = availability.lower() == 'true'
            else:
                return jsonify({'error': 'Available must be true or false'}), 400
        else:
            return jsonify({'error': 'New Book availability is the same as the current book availability'})

    if data.get('available_copies'):
        try:
            available_copy = int(data['available_copies'])
            if available_copy != book.available_copies:
                book.available_copies = available_copy
                updated_details['available_copies'] = available_copy
            else:
                return jsonify({'error': 'New Book available copies is the same as the current book available copies'})

        except ValueError:
            return jsonify({'error': 'Available copies must be an integer'}), 400

    if data.get('total_copies'):
        try:
            total_copy = int(data['total_copies'])

            if total_copy != book.total_copies:
                book.total_copies = total_copy
                updated_details['total_copies'] = total_copy
            else:
                return jsonify({'error': 'New Book total copies is the same as the current book total copies'})
                                                 
         except ValueError:
            return jsonify({'error': 'Total copies must be an integer'}), 400

    if data.get('language'):
        if data.get('language') != book.language:
            book.language = data['language']
            updated_details['language'] = book.language
        else:
            return jsonify({'error': 'New Book language is the same as the current book language'})

    if data.get('category'):
        if data.get('category') != book.category:
            book.category = data['category']
            updated_details['category'] = book.category
        else:
            return jsonify({'error': 'New Book category is the same as the current book category'})

    if data.get('publisher'):
        if data.get('publisher') != book.publisher:
            book.publisher = data['publisher']
            updated_details['publisher'] = book.publisher
        else:
            return jsonify({'error': 'New Book publisher is the same as the current book publisher'})
    
    if data.get('cover_image_url'):
        if data.get('cover_image_url') != book.cover_image_url:
            book.cover_image_url = data['cover_image_url']
            updated_details['cover_image_url'] = book.cover_image_url
        else:
            return jsonify({'error': 'cover_image_url is the same as current cover_image_url'})

    if updated_details is None:
        return jsonify({'error': 'No updated details provided'}), 400
    
    if 'available_copies' in updated_details or 'total_copies' in updated_details:
        if book.total_copies < book.available_copies:
            return jsonify({'error': 'Total copies must be greater than or equal to available copies'}), 400
        else:
            book.update_availability()
    
    updated_details['book_id'] = book.id
    db.session.commit()
    
    return jsonify({
        "a_message": "Details updated successfully",
        "updated_fields": updated_details
    }), 200

@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Summary:
        Delete a book from the database by its ID and return a confirmation message if successful otherwise returns an error
            Description:
        This endpoint deletes a book from the database by its ID.
        If the book is not found, it returns a 404 error with a message indicating that the book was not found.
        If the book is successfully deleted, it returns a 200 status code with a confirmation message.
        If there is an error deleting the book, it returns a 500 error with a generic error message.
    
    Args:
        book_id (int): The ID of the book to delete.

    Returns:
        JSON: A confirmation message if the book is deleted successfully otherwise error message.
    """

    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({
        "a_message": "Book deleted successfully"
    }), 200

@books_bp.route('/books/<int:book_id>/availability', methods=['GET'])
def check_availability(book_id):
    """
    Summary:
        Check the availability of a book by its ID and return its availability status in JSON format if successful otherwise returns an error
            Description:
        This endpoint retrieves the availability status of a book from the database by its ID.
        If the book is not found, it returns a 404 error with a message indicating that the book was not found.
        If the book is successfully retrieved, it returns a 200 status code with the availability status in JSON format.
        If there is an error retrieving the book, it returns a 500 error with a generic error message.

    Args:
        book_id (int): The ID of the book to check availability.

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
        Retrieve all books' availability status in JSON format and return them if successful otherwise returns an error
            Description:
        This endpoint retrieves all books' availability status or specific book according to the parameter provided from the database.
        If there are no books, it returns an empty JSON object.
        If the books are successfully retrieved, it returns a 200 status code with the availability status in JSON format.

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
        return jsonify({'error': 'No books found matching the given criteria'}), 404
    
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