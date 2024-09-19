from flask import Blueprint,jsonify, request
from models import *
from dateutil import parser
from werkzeug.exceptions import BadRequest

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def create_user():
    """
    Summary:
        Registers a new user in the system.
           
    Description:
        This endpoint adds a new user to the database.
        It expects a JSON request body containing the user's details. 
        The request should contain the user's details in JSON format.
        The following validations are performed:
        - The request must be of type 'application/json'.
        - The request body must contain all required fields.
        - The password must be at least 8 characters long.
        - The email must be valid.
        - The date of birth must be a valid date.
        - The phone number must be valid.
        - The username and email must be unique.
        - The user's phone number must not match the guarantor's phone number.
    
    Required Fields(JSON):
        The request should be a JSON object with the following fields:
        - username (string, required): A unique username for the user.
        - password (string, required): The user's password (must be at least 8 characters long).
        - email (string, required): A unique email for the user.
        - first_name (string, required): The user's first name.
        - last_name (string, required): The user's last name.
        - phone_number (string, required): The user's phone number.
        - date_of_birth (string, required): The user's date of birth (must be a valid date).
        - address (string, required): The user's address.
        - guarantor_fullname (string, required): The name of the user's guarantor.
        - guarantor_phone_number (string, required): The phone number of the user's guarantor.
        - guarantor_address (string, required): The address of the user's guarantor.
        - guarantor_relationship (string, required): The relationship between the user and the guarantor.

    HTTP Status Codes:
        - 201 Created: Registration successful, returns user details.
        - 400 Bad Request: Invalid request data or validation errors.
        - 500 Internal Server Error: Unexpected server error.
        - 409 Conflict
        
    Errors:
        - Invalid JSON
        - Missing required fields
        - Non-unique username or email
        - Invalid password, email, phone number, or date of birth
        
    Returns:
        JSON: A JSON object with the user's ID and details if the registration is successful,
        or an error message if not successful.
    """
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    try:
        data = request.get_json()
    except BadRequest as e:
        return jsonify({'error': 'Invalid JSON', 'message': str(e)}), 400
    
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400
    
    required_fields = ['username', 'password', 'email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'address', 'guarantor_fullname', 'guarantor_phone_number', 'guarantor_address', 'guarantor_relationship']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email_address=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    
    try:
        user = User(
        password=data['password'],
        email=data['email'],
        phone_number=data['phone_number'],
        guarantor_phone_number=data['guarantor_phone_number']
        )
        user.validate_date_of_birth(data['date_of_birth'])
        user.validate_username(data['username'])
        user.address = user.validate_address(data['address'])
        user.guarantor_address = user.validate_address(data['guarantor_address'])
        user.first_name=user.validate_firstname(data['first_name'])
        user.last_name=user.validate_firstname(data['last_name'])
        user.guarantor_fullname=user.validate_fullname(data['guarantor_fullname'])
        user.guarantor_relationship=user.validate_relation(data['guarantor_relationship'])
        db.session.add(user)
        db.session.commit()
        return jsonify(user.user_serialize()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except AttributeError as e:
        return jsonify({'error': str(e)}), 400
    except TypeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()  # Rollback session on error
        return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500
    
@users_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """
    Summary:
        Retrieve a user by their ID from the database.

    Description:
        This endpoint fetches a specific user from the database using their ID
        and returns the user's details in JSON format. 
        If a user with the specified ID exists, their details are returned.
        If no user with the given ID is found, 
        an error message indicating that the user was not found is returned.

    Args:
        id (int): The unique identifier of the user to retrieve.

    HTTP Status Codes:
        - 200 OK: The request was successful, and the user details are returned.
        - 404 Not Found: The user with the specified ID was not found.

    Errors raised:
        - User not found: The user with the specified ID was not found.

    Return:
        JSON : A json object containing the user's details if the user exists,
        or an error message otherwise
    """
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    results ={
            "user_id": user.id,
            "phone_number": user.phone_number,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email_address,
        }
    return jsonify(results), 200

@users_bp.route('/users', methods=['GET'])
def get_all_users():
    """
    Summary:
        Retrieve a list of users from the database, with optional filtering by username or email, and pagination.
    
    Description:
        it endpoint fetches users from the database based on optional filters and pagination parameters. 
        It supports retrieving all users, or filtering by username or email address. 
        Pagination parameters allow you to control the number of users returned per page and the specific page of results. 

        - If no filters or pagination parameters are provided, it retrieves all users.
        - If filters are provided, it retrieves users that match the specified username or email criteria.
        - If no users match the provided filters, it returns a message indicating no matches were found.
        - If pagination parameters are used, it returns a paginated list of users.

    Optional parameters:
        - page (int): The page number to retrieve (default: 1)
        - per_page (int): The number of users per page (default: 10)
        - username (string): The username of the user to get (optional)
        - email (string): The email address of the user to get (optional)
    
    Errors:
        - invalid pagination parameters

    HTTP Status Codes:
        400 Bad Request
        200 OK

    Returns:
        JSON : A json object containing a list of all users in the database
    """
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)

    username_filter = request.args.get('username', None)
    email_filter = request.args.get('email', None)

    try:
        page = int(page)
        per_page = int(per_page)
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Page and per_page parameters must be positive integers'}), 400
    except Exception as e:
        return jsonify({'error': f'Page and per_page parameters must be integers {e}'}), 400
    
    query = User.query

    if username_filter:
        query = query.filter(User.username.ilike(f'%{username_filter}%'))

    if email_filter:
        query = query.filter(User.email_address.ilike(f'%{email_filter}%'))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    if (username_filter or email_filter) and not pagination.items:
        return jsonify({'message': 'No user found matching the provided filter(s)'}), 200
    
    if not (username_filter or email_filter):
        if not pagination.items:
            return jsonify({'message' : 'No users found'}), 200
        
    total = pagination.total

    users = pagination.items
    
    results = [
    {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email_address,
    } for user in users
    ]

    return jsonify({
        "users": results,
        "total_pages": pagination.pages,
        "total_results": total,
        "per_page": per_page,
        "page": page,
    }), 200

@users_bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    """
    Summary:
        Update a user’s details by their ID and return the updated user object if successful; otherwise, return an error message.
            
    Description:
        This endpoint updates the details of a user identified by their ID.
        It accepts a JSON request body with the fields to be updated. 
        The endpoint performs various checks to ensure that the updates meet the required criteria.
        It handles updates to fields including:
        - `username`
        - `password`
        - `email`
        - `first_name`
        - `last_name`
        - `phone_number`
        - `address`
        - `guarantor_fullname`
        - `guarantor_phone_number`
        - `guarantor_address`
        - `guarantor_relationship`

        The endpoint checks for:
        - Existing usernames and emails to ensure uniqueness.
        - Correctness of passwords, including validation of the old password.
        - Validity of provided phone numbers and email addresses.
        - If provided values are different from the existing ones.

    Optional parameters:
        - username (string): The new username of the user (optional)
        - password (string): The new password of the user (optional)
        - email (string): The new email address of the user (optional)
        - first_name (string): The new first name of the user (optional)
        - last_name (string): The new last name of the user (optional)
        - phone_number (string): The new phone number of the user (optional)
        - address (string): The new address of the user (optional)
        - guarantor_fullname (string): The new name of the user's guarantor (optional)
        - guarantor_phone_number (string): The new phone number of the user's guarantor (optional)
        - guarantor_address (string): The new address of the user's guarantor (optional)
        - guarantor_relationship (string): The new relationship between the user and the guarantor (optional)

    Args:
        id (int): The id of the user to update

    HTTP Status Codes:
        400 Bad Request
        404 Not Found
        200 OK
        500 Internal Server Error
        409 Conflict

    Errors:
    - Invalid or missing data.
    - User not found.
    - Existing username or email                
    - Password validation errors.

    Returns:
        JSON: A json object containing the updated user object if successful otherwise an error message
    """
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    try:
        data = request.get_json()
    except BadRequest as e:
        return jsonify({'error': 'Invalid JSON', 'message': str(e)}), 400
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update user fields based on JSON data
    updated_fields = {}
    
    if data.get('username'):
        new_username = data['username']
        if new_username != user.username:
            try:
                if User.query.filter_by(username=new_username).first():
                    return jsonify({'error': 'Username already exists'}), 409
                user.validate_username(new_username)
                updated_fields['username'] = user.username
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': 'New Username is the same as the current username'}), 409

    if data.get('old_password') or data.get('new_password'):
        try:
            for field in ['old_password', 'new_password']:
                if not field in data:
                    return jsonify({'error': 'old_password and new_password data is required'}), 400
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            hash = user.check_password(new_password)
            if hash != True:
                user.update_password(old_password, new_password)
                updated_fields['password'] = new_password
            else:
                return jsonify({'error': 'New password is the same as the current password'}), 409
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    
    if data.get('email'):
        new_email = data['email']
        if new_email != user.email_address:
            if User.query.filter_by(email_address=new_email).first():
                return jsonify({'error': 'Email already exists'}), 409
            try:    
                user.email = new_email
                updated_fields['email'] = user.email_address
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': 'New Email is the same as the current email'}), 409
    
    if data.get('first_name'):
        if data.get('first_name') != user.first_name:
            try:
                user.first_name = user.validate_firstname(data['first_name'])
                updated_fields['first_name'] = user.first_name
            except Exception as e:
                return jsonify({'errors': str(e)}), 400
        else:
            return jsonify({'error': 'New First name is the same as the current first name'}), 409
    
    if data.get('last_name'):
        if data.get('last_name') != user.last_name:
            try:
                user.last_name = user.validate_firstname(data['last_name'])
                updated_fields['last_name'] = user.last_name
            except Exception as e:
                return jsonify({"errors": str(e)}), 400
        else:
            return jsonify({'error': 'New Last name is the same as the current last name'}), 409
    
    if data.get('phone_number'):
        if data.get('phone_number') != user.phone_number:
            try:
                user.phone_number = data['phone_number']
                updated_fields['phone_number'] = user.moblie_number
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': 'New Phone number is the same as the current phone number'}), 409

    if data.get('address'):
        if data.get('address') != user.address:
            try:
                user.address = user.validate_address(data['address'])
                updated_fields['address'] = user.address
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': 'New Address is the same as the current address'}), 409
    
    if data.get('guarantor_fullname'):
        if data.get('guarantor_fullname') != user.guarantor_fullname:
            try:
                user.guarantor_fullname = user.validate_fullname(data['guarantor_fullname'])
                updated_fields['guarantor_fullname'] = user.guarantor_fullname
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        else:
            return jsonify({'error': "New Guarantor's full name is the same as the current guarantor's full name"}), 409
    
    if data.get('guarantor_phone_number'):
        if data.get('guarantor_phone_number') != user.guarantor_phone_number:
            try:
                user.guarantor_phone_number = data['guarantor_phone_number']
                updated_fields['guarantor_phone_number'] = user.guarantor_mobile.number
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': "New Guarantor's phone number is the same as the current guarantor's phone number"}), 409

    if data.get('guarantor_address'):
        if data.get('guarantor_address') != user.guarantor_address:
            try:
                user.guarantor_address = user.validate_address(data['guarantor_address'])
                updated_fields['guarantor_address'] = user.guarantor_address
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': "New Guarantor's address is the same as the current guarantor's address"}), 409

    if data.get('guarantor_relationship'):
        if data.get('guarantor_relationship') != user.guarantor_relationship:
            try:
                user.guarantor_relationship = user.validate_relation(data['guarantor_relationship'])
                updated_fields['guarantor_relationship'] = user.guarantor_relationship
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        else:
            return jsonify({'error': "New Guarantor's relationship is the same as the current guarantor's relationship"}), 409
        
    if not updated_fields:
        return jsonify({'message': 'No changes made'}), 200
            
    updated_fields["user_id"] = user.id

    try:
        db.session.commit()
        return jsonify({
            "a_message": "Details updated successfully",
            "updated_fields": updated_fields
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred while updating the user: {str(e)}"}), 500

@users_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    """
    Summary:
        Delete a user from the database with the given id and return a JSON response indicating the success
        or failure of the operation.

    Description:
        This endpoint deletes a user identified by their ID from the database.
        If the user is found, the user will be removed from the database,
        and a successful response will be returned.
        If the user does not exist, a 404 error will be returned. 
        If an error occurs during the deletion process, an error message will be returned.
            
    Args:
        id (int): The id of the user to be deleted.

    HTTP Response Status:
        404 Not Found
        500 Internal Server Error
        200 OK

    Errors:
        user does not exist.
        error occurred while deleting the user

    Returns:
        JSON: A JSON response indicatidng the success or failure of the operation.
    """
    user_id = id
    user = User.query.get(id)
    if user:
        user_name = user.username
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User deleted successfully", "user_id": user_id, "username": user_name}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An error occurred while deleting the user: {str(e)}"}), 500
    else:
        return jsonify({"error": "User not found"}), 404
    
@users_bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    """
    Summary:
        Handle all unmatched routes and return a 404 error message.

    Description:
        This endpoint acts as a catch-all handler for any requests that do not match defined routes within the `users_bp` blueprint.
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