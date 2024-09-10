from app import db, app

with app.app_context():
    """ create the tables in the database """
    db.create_all()