from flask import Blueprint,jsonify, request
from models import *
from dateutil import parser
import phonenumbers
from phonenumbers import NumberParseException, is_valid_number, format_number, PhoneNumberFormat

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def create_user():
    """
    Summary:
        Registers a new user in the system.
    
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
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400
    
    if not data.get('username') or not data.get('password') or not data.get('email') or not data.get('first_name') or not data.get('last_name') or not data.get('phone_number') or not data.get('date_of_birth') or not data.get('address') or not data.get('guarantor_fullname') or not data.get('guarantor_phone_number') or not data.get('guarantor_address') or not data.get('guarantor_relationship'):
        return jsonify({'error': 'Missing required fields'}), 400
    
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

    Args:
        id (int): The id of the user to get

    Return:
        JSON : A json object containing the user's details if the user exists, or an error message otherwise
    """
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    results ={
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
        Get all users in the database or get specific user by username or email address provided as parameter and return a list of users or specified user

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

    if page < 1 or per_page < 1:
        return jsonify({'error': 'Page and per_page parameters must be positive integers'}), 400
    
    query = User.query

    if username_filter:
        query = query.filter(User.username.like(f'%{username_filter}%'))

    if email_filter:
        query = query.filter(User.email.like(f'%{email_filter}%'))
    
    total = query.count()

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

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
        Update a user by id and return the updated user object if successful otherwise return an error message

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
    
    data = request.get_json()
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
            return jsonify({'error': 'Username is the same as the current username'})

    if data.get('old_password') and data.get('new_password'):
        try:
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            user.update_password(old_password, new_password)
            updated_fields['password'] = data['new_password']
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
        return jsonify({'error': 'Email is the same as the current email'})
    
    if data.get('first_name'):
        if data.get('first_name') != user.first_name:
            user.first_name = data['first_name']
            updated_fields['first_name'] = data.get('first_name')
        else:
            return jsonify({'error': 'First name is the same as the current first name'})
    
    if data.get('last_name'):
        if data.get('last_name') != user.last_name:
            user.last_name = data['last_name']
            updated_fields['last_name'] = data.get('last_name')  # Update last name if provided in JSON data
        else:
            return jsonify({'error': 'Last name is the same as the current last name'})
    
    if data.get('phone_number'):
        if data.get('phone_number') != user.phone_number:
            try:
                user.phone_number = data['phone_number']
                updated_fields['phone_number'] = data.get('phone_number')  # Update phone number if provided in JSON data
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': 'Phone number is the same as the current phone number'})

    if data.get('address'):
        if data.get('address') != user.address:
            user.address = data['address']
            updated_fields['address'] = data.get('address')  # Update address if provided in JSON data
        else:
            return jsonify({'error': 'Address is the same as the current address'})
    
    if data.get('guarantor_fullname'):
        if data.get('guarantor_fullname') != user.guarantor_fullname:
            user.guarantor_fullname = data['guarantor_fullname']
            updated_fields['guarantor_fullname'] = data.get('guarantor_fullname')  # Update guarantor's fullname if provided in JSON data
        else:
            return jsonify({'error': "Guarantor's full name is the same as the current guarantor's full name"})
    
    if data.get('guarantor_phone_number'):
        if data.get('guarantor_phone_number') != user.guarantor_phone_number:
            try:
                user.guarantor_phone_number = data['guarantor_phone_number']
                updated_fields['guarantor_phone_number'] = data.get('guarantor_phone_number')
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': "Guarantor's phone number is the same as the current guarantor's phone number"})

    if data.get('guarantor_address'):
        if data.get('guarantor_address') != user.guarantor_address:
            user.guarantor_address = data['guarantor_address']
            updated_fields['guarantor_address'] = data.get('guarantor_address')  # Update guarantor's address if provided in JSON data
        else:
            return jsonify({'error': "Guarantor's address is the same as the current guarantor's address"})

    if data.get('guarantor_relationship'):
        if data.get('guarantor_relationship')!= user.guarantor_relationship:
            user.guarantor_relationship = data['guarantor_relationship']
            updated_fields['guarantor_relationship'] = data.get('guarantor_relationship')  # Update guarantor's relationship if provided in JSON data
        else:
            return jsonify({'error': "Guarantor's relationship is the same as the current guarantor's relationship"})
            
    updated_fields["user_id"] = user.id

    db.session.commit()
    return jsonify({
        "a_message": "Details updated successfully",
        "updated_fields": updated_fields
    })

@users_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    """
    Summary:
        Delete a user from the database with the given id and return a JSON response indicating the success or failure of the operation.

    Args:
        id (int): The id of the user to be deleted.

    Returns:
        JSON: A JSON response indicating the success or failure of the operation.
    """
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"})
    else:
        return jsonify({"error": "User not found"}), 404