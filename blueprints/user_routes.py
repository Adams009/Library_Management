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