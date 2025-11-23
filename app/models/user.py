import logging

from flask import flash
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    """
    A class to represent the relational database table used to store the credentials and other information of users for the web application

    Columns
    -------------------
    id: Integer
        user id
    first_name: VARCHAR(150)
        User's first name
    last_name: VARCHAR(150)
        User's last name
    email: VARCHAR(150)
        User's email address
    password: VARCHAR(20)
        Password for accessing the application
    is_admin: Boolean
        Stores if this user has an admin role. True = user has admin privileges
    """

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    failed_attempts = db.Column(db.Integer, default=0, nullable=False)

    @staticmethod
    def find_user_by_email(email):
        """Finds a user in the User table by their email address"""
        try:
            user = User.query.filter_by(email=email).first()
            return user
        except SQLAlchemyError as err:
            logging.error('An error was encountered whilst filtering the User table by email: %s', email)
            logging.error(err)

    @staticmethod
    def add_user(email, first_name, last_name, password, is_admin):
        """Add user to User table"""
        try:
            new_user = User(email=email, first_name=first_name, last_name=last_name,
                            password=generate_password_hash(password, method='scrypt'), is_admin=is_admin)
            db.session.add(new_user)
            db.session.commit()
        except SQLAlchemyError as err:
            db.session.rollback()
            logging.error('Unable to register user: %s', email)
            logging.error(err)
            flash('Unable to register user', category='error')
        else:
            logging.info('%s account created successfully', email)
            flash('Account created successfully!', category='success')

    @staticmethod
    def update_password(email, password):
        """Updates users password"""
        try:
            user = User.find_user_by_email(email)
            user.password = generate_password_hash(password, method='scrypt')
            db.session.commit()
        except SQLAlchemyError as err:
            db.session.rollback()
            logging.error('Unable to update password for user: %s', email)
            logging.error(err)
            flash('Unable to update password', category='error')
        else:
            logging.info('%s password updated successfully', email)
            flash('Password updated successfully!', category='success')