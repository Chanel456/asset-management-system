from flask import flash, current_app
from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError

from app import db

class Server (db.Model):
    """
        A class to represent the relational database table used to store the details of a department server

        Columns
        -------------------
        id: Integer
            user id
        name: VARCHAR(50)
            Name of the server
        CPU: Integer
            The amount of CPU the server has
        Memory: Integer
            The amount of memory the server has
        Location: VARCHAR(50)
            The location of the server
        applications:
            Convenient way to access all the applications related to a server
        """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique= True, nullable=False)
    cpu = db.Column(db.Integer, nullable=False)
    memory = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(50), nullable=False)
    applications = db.relationship('Application')

    @staticmethod
    def fetch_server_with_entity(entity):
        """Selects all entries for specified column in Server table"""
        try:
            result = Server.query.with_entities(entity)
            return result
        except SQLAlchemyError as err:
            current_app.logger.error(
                f'An error occurred whilst querying the server table with entity: {entity}',
                extra={
                    "error": str(err),
                    "error_type": type(err).__name__,
                })

    @staticmethod
    def find_server_by_id(server_id):
        """Find a server in the database using the server id"""
        try:
            retrieved_server = Server.query.get(server_id)
            return retrieved_server
        except SQLAlchemyError as err:
            current_app.logger.error(
                f'An error occurred whilst finding server by id: {server_id}',
                extra={
                    "error": str(err),
                    "error_type": type(err).__name__,
                })

    @staticmethod
    def find_server_by_name(name):
        """Finds a server in the database by the server name"""
        try:
            retrieved_server = Server.query.filter_by(name=name).first()
            return retrieved_server
        except SQLAlchemyError as err:
            current_app.logger.error(
                f'An error occurred whilst finding server by name: {name}',
                extra={
                    "error": str(err),
                    "error_type": type(err).__name__,
                })

    @staticmethod
    def fetch_all_servers():
        """Fetches all servers in the server table"""
        try:
            servers = db.session.query(Server).all()
            return servers
        except SQLAlchemyError as err:
            current_app.logger.error(
                'An error occurred whilst fetching all rows in the server table',
                extra={
                    "error": str(err),
                    "error_type": type(err).__name__,
                })

    @staticmethod
    def create_server(name, cpu, memory, location):
        """Creates a new server and adds it to the database"""
        try:
            new_server = Server(name=name, cpu=cpu, memory=memory, location=location)
            db.session.add(new_server)
            db.session.commit()
        except SQLAlchemyError as err:
            db.session.rollback()
            current_app.logger.error(
                f'Unable to create server: {name}',
                extra={
                    "error": str(err),
                    "error_type": type(err).__name__,
                })
            flash('Unable to create server', category='error')
        else:
            current_app.logger.info(f'Server {name} added successfully',)
            flash('Server added successfully', category='success')

    @staticmethod
    def update_server(server_id, updated_server):
        """Updates an existing server in the database"""
        try:
            db.session.query(Server).filter_by(id=server_id).update(updated_server)
            db.session.commit()
        except SQLAlchemyError as err:
            db.session.rollback()
            current_app.logger.error(
                f'An error was encountered when updating server with id: {server_id}',
                extra={
                    "error": str(err),
                    "error_type": type(err).__name__,
                })
            flash('Unable to update server', category='error')
        else:
            current_app.logger.info(f'Server: {updated_server['name']} successfully updated',)
            flash('Server successfully updated', category='success')

    @staticmethod
    def delete_server(server):
        """Deletes a server from the database"""
        try:
            db.session.delete(server)
            db.session.commit()
        except SQLAlchemyError as err:
            db.session.rollback()
            current_app.logger.error(
                f'An error was encountered when deleting server with id: {server.id}',
                extra={
                    "error": str(err),
                    "error_type": type(err).__name__,
                })
            flash('Unable to delete server', category='error')
        else:
            current_app.logger.info(f'Server: {server.name} deleted successfully',)
            flash('Server deleted successfully', category='success')



@event.listens_for(Server.__table__, 'after_create')
def create_servers(*args, **kwargs):
    """Inserting 10 rows of data into server table on after database creation"""
    try:
        db.session.add(Server(name='ab-0001', cpu=123, memory=123, location='Walthamstow'))
        db.session.add(Server(name='ab-0002', cpu=234, memory=234, location='Harrow'))
        db.session.add(Server(name='ab-0003', cpu=345, memory=345, location='Walthamstow'))
        db.session.add(Server(name='ab-0004', cpu=456, memory=456, location='Walthamstow'))
        db.session.add(Server(name='ab-0005', cpu=567, memory=567, location='Harrow'))
        db.session.add(Server(name='ab-0006', cpu=678, memory=678, location='Walthamstow'))
        db.session.add(Server(name='ab-0007', cpu=789, memory=789, location='Walthamstow'))
        db.session.add(Server(name='ab-0008', cpu=890, memory=890, location='Harrow'))
        db.session.add(Server(name='ab-0009', cpu=901, memory=901, location='Walthamstow'))
        db.session.add(Server(name='ab-0010', cpu=184, memory=184, location='Walthamstow'))
        db.session.commit()
    except SQLAlchemyError as err:
        db.session.rollback()
        current_app.logger.error(
            'Unable to add dummy data to Server table on database creation',
            extra={
                "error": str(err),
                "error_type": type(err).__name__,
            })