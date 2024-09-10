from flask import Blueprint,jsonify, request
from models import *
from dateutil import parser
import phonenumbers
from phonenumbers import NumberParseException, is_valid_number, format_number, PhoneNumberFormat

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def create_user():
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