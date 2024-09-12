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
        This endpoint adds a new user to the database. It expects a JSON request body containing the user details. 
        Registers a new user in the system. The request should contain the user's details in JSON format.
        if the request is not a JSON request, it returns an error message.
        if no data is passed in the JSON request, it returns an error message.
        if one of the required fields is missing, it returns an error message.
        if the password is not strong enough, it returns an error message. The password must be at least 8 characters long.
        if the email is not valid, it returns an error message.
        if the date of birth is not a valid date, it returns an error message.
        if the phone number is not valid, it returns an error message.
        if the username or email already exists in the system, it returns an error message. The username and email must be unique.
        if the user's phone number is the same with the guarantor's phone number, it returns an error message.
    
    Required Datas: The request should be a JSON object with the following fields:
        - username: A unique username for the user (string, required)
        - password: The user's password (string, required)
        - email: A unique email for the user (string, required)

                - first_name: The user's first name (string, required)
        - last_name: The user's last name (string, required)
        - phone_number: The user's phone number (string, required)
        - date_of_birth: The user's date of birth (string, required)
        - address: The user's address (string, required)
        - guarantor_fullname: The name of the user's guarantor (string, required)
        - guarantor_phone_number: The phone number of the user's guarantor (string, required)
        - guarantor_address: The address of the user's guarantor (string, required)
        - guarantor_relationship: The relationship between the user and the guarantor (string, required)
    
    Returns:
        JSON: A JSON object with the user's ID and details if the registration is successful, or an error message if not successful.
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
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    
    try:
        user = User(
        username=data['username'],
        password=data['password'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone_number=data['phone_number'],
        date_of_birth=parser.parse(data['date_of_birth']),
        address=data['address'],
        guarantor_fullname=data['guarantor_fullname'],
        guarantor_phone_number=data['guarantor_phone_number'],
        guarantor_address=data['guarantor_address'],
        guarantor_relationship=data['guarantor_relationship']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(user.user_serialize()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@users_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """
    Summary:
        Get a user by id from the database and return the corresponding user object if it exists and not None otherwise return error message
            Description:
        This endpoint will retrieve a specific user from the database by its ID and return it in JSON format
        Retrieves a user by id from the database and returns the corresponding user object if it exists and not None otherwise returns an error message.
        If the user does not exist, it returns an error message. If the user exists, it returns the user object with the specified id.

    Args:
        id (int): The id of the user to get

    Return:
        JSON : A json object containing the user's details if the user exists, or an error message otherwise
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
        Get all users in the database or get specific user by username or email address provided as parameter and return a list of users or specified user.
            Description:
        This endpoint will return all users in the database or get specific user by username or email address and return a JSON list of users or specified user
        Retrieves all users in the database or a specific user by username or email address provided as parameter and returns a list of users or specified user.
        it accepts page parameters to retrieve all users in a particular page
        it accepts per page parameters to decide number of users to retrieve per page
        If no parameters are provided, it retrieves all users.
        If a username or email is provided, it retrieves the user(s) matching that criteria.
        If a username or email is provided but no matching user is found, it returns an error message.
        If a username or email is provided and multiple users are found, it returns a list of users matching that criteria.
        If a username or email is provided and only one user is found, it returns the user object.


    Optional parameters:
        - page (int): The page number to retrieve (default: 1)
        - per_page (int): The number of users per page (default: 10)
        - username (string): The username of the user to get (optional)
        - email (string): The email address of the user to get (optional)
    
    Returns:
        JSON : A json object containing a list of all users in the database
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    username_filter = request.args.get('username', None)
    email_filter = request.args.get('email', None)

    try:
        page = int(page)
        per_page = int(per_page)
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Page and per_page parameters must be positive integers'}), 400
    except ValueError:
        return jsonify({'error': 'Page and per_page parameters must be integers'}), 400
    
    query = User.query

    if username_filter:
        query = query.filter(User.username.ilike(f'%{username_filter}%'))

    if email_filter:
        query = query.filter(User.email_address.ilike(f'%{email_filter}%'))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    if (username_filter or email_filter) and not pagination.items:
        return jsonify({'error': 'No user found matching the provided filter(s)'}), 404
    
    if not (username_filter or email_filter):
        if not pagination.items:
            return jsonify({'message' : 'No users found'}), 200
        
    total = query.count()

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
        Update a user by id and return the updated user object if successful otherwise return an error message.
            Description:
        This endpoint will update the user object by the given ID and given details about to be updated
        Updates a user by id and returns the updated user object if successful, otherwise returns an error message.
        If the user does not exist, it returns an error message.
        If the user exists, it updates the user object with the provided data and returns the updated user object.
        if the username is same with the provided new username, it returns an error message.
        if the username exists in the database and it is not the same with the old username, it returns an error message
        if the password is same with the provided new password, it returns an error message.
        if the the old password is not provided, it returns an error message.
        if the old password is provided but not correct, it returns an error message.
        if the new password is provided but it is not strong enough, it returns an error message.
        if the new password and old password are provided, it validates the old password before updating the password.
        if the new email address is provided but it is not valid, it returns an error message.
        if the new email address is provided and it is the same with the old email address, it returns an error message.
        if the new email exists in the database and it is not the same with the old email and it is valid, it returns an error message.
        if the new number is provided and it is not valid, it returns an error message.
        if the new number is provided and it is the same with the old number, it returns an error message.
        if the new first name is provided and it is the same with the old first name, it returns an error message.
        if the new last name is provided and it is the same with the old last name, it returns an error message.
        if the new address is provided and it is the same with the old address, it returns an error
        if the new guarantor address is provided and it is the same with the old guarantor address, it returns an error message.
        if the new guarantor relationship is provided and it is the same with the old guarantor relationship, it returns an error message.
        if the new guarantor phone number is provided and it is the same with the old guarantor phone number, it returns an error message.
        if the new guarantor phone number is provided and it is the same with the user's phone number, it returns an error message.
        if the new guarantor phone number is provided and it is not valid, it returns an error message.

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
    
    # user_id = data.get('id')
    # if not user_id:
    #     return jsonify({'error': 'user_id is required'}), 400
    
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update user fields based on JSON data
    updated_fields = {}
    
    if data.get('username'):
        new_username = data['username']
        if new_username != user.username:
            if User.query.filter_by(username=new_username).first():
                return jsonify({'error': 'Username already exists'}), 400
            user.username = new_username
            updated_fields['username'] = new_username
        else:
            return jsonify({'error': 'New Username is the same as the current username'}), 400

    if data.get('old_password') and data.get('new_password'):
        try:
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            if old_password != new_password:
                user.update_password(old_password, new_password)
                updated_fields['password'] = data['new_password']
            else:
                return jsonify({'error': 'New password is the same as the current password'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    
    if data.get('email'):
        new_email = data['email']
        if new_email != user.email_address:  
            if User.query.filter_by(email=new_email).first():
                return jsonify({'error': 'Email already exists'}), 400
            try:    
                user.email = new_email
                updated_fields['email'] = new_email
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        return jsonify({'error': 'New Email is the same as the current email'}), 400
    
    if data.get('first_name'):
        if data.get('first_name') != user.first_name:
            user.first_name = data['first_name']
            updated_fields['first_name'] = data.get('first_name')
        else:
            return jsonify({'error': 'New First name is the same as the current first name'}), 400
    
    if data.get('last_name'):
        if data.get('last_name') != user.last_name:
            user.last_name = data['last_name']
            updated_fields['last_name'] = data.get('last_name')
        else:
            return jsonify({'error': 'New Last name is the same as the current last name'}), 400
    
    if data.get('phone_number'):
        if data.get('phone_number') != user.phone_number:
            try:
                user.phone_number = data['phone_number']
                updated_fields['phone_number'] = data.get('phone_number')
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': 'New Phone number is the same as the current phone number'}), 400

    if data.get('address'):
        if data.get('address') != user.address:
            user.address = data['address']
            updated_fields['address'] = data.get('address')
        else:
            return jsonify({'error': 'New Address is the same as the current address'}), 400
    
    if data.get('guarantor_fullname'):
        if data.get('guarantor_fullname') != user.guarantor_fullname:
            user.guarantor_fullname = data['guarantor_fullname']
            updated_fields['guarantor_fullname'] = data.get('guarantor_fullname')
        else:
            return jsonify({'error': "New Guarantor's full name is the same as the current guarantor's full name"}), 400
    
    if data.get('guarantor_phone_number'):
        if data.get('guarantor_phone_number') != user.guarantor_phone_number:
            try:
                user.guarantor_phone_number = data['guarantor_phone_number']
                updated_fields['guarantor_phone_number'] = data.get('guarantor_phone_number')
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': "New Guarantor's phone number is the same as the current guarantor's phone number"}), 400

    if data.get('guarantor_address'):
        if data.get('guarantor_address') != user.guarantor_address:
            user.guarantor_address = data['guarantor_address']
            updated_fields['guarantor_address'] = data.get('guarantor_address')
        else:
            return jsonify({'error': "New Guarantor's address is the same as the current guarantor's address"}), 400

    if data.get('guarantor_relationship'):
        if data.get('guarantor_relationship')!= user.guarantor_relationship:
            user.guarantor_relationship = data['guarantor_relationship']
            updated_fields['guarantor_relationship'] = data.get('guarantor_relationship')
        else:
            return jsonify({'error': "New Guarantor's relationship is the same as the current guarantor's relationship"}), 400
        
    if updated_fields is None:
        return jsonify({'error': 'No changes is provided to be made to the user'}), 400
            
    updated_fields["user_id"] = user.id

    db.session.commit()
    return jsonify({
        "a_message": "Details updated successfully",
        "updated_fields": updated_fields
    }), 200

@users_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    """
    Summary:
        Delete a user from the database with the given id and return a JSON response indicating the success or failure of the operation.
            Description:
        This endpoint deletes a user from the database with the given ID
        The user will be removed from the database, along with all associated records and returns a successful response.
        if user is not found, a 404 error will be returned.
    Args:
        id (int): The id of the user to be deleted.

    Returns:
        JSON: A JSON response indicating the success or failure of the operation.
    """
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"a_message": "User deleted successfully"}), 200
    else:
        return jsonify({"error": "User not found"}), 404