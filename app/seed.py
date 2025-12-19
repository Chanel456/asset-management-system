import os

from werkzeug.security import generate_password_hash

from app import db
from app.models.user import User


def seed_users():
    users_to_seed = [
        {
            'email': os.environ.get('ADMIN_EMAIL'),
            'password': os.environ.get('ADMIN_PASSWORD'),
            'first_name': 'Admin',
            'last_name': 'Admin',
            'is_admin': True,
        },
        {
            'email': os.environ.get('REGULAR_EMAIL'),
            'password': os.environ.get('REGULAR_PASSWORD'),
            'first_name': 'Regular',
            'last_name': 'Regular',
            'is_admin': False,
        },
    ]

    for user_data in users_to_seed:
        email = user_data['email']
        password = user_data['password']

        # Skip if environment variables are not set
        if not email or not password:
            continue

        existing_user = User.find_user_by_email(email)

        if existing_user:
            continue

        new_user = User(email=email, first_name=user_data['first_name'], last_name=user_data['last_name'],
                        password=generate_password_hash(password, method='scrypt'), is_admin=user_data['is_admin'])
        db.session.add(new_user)
        db.session.commit()