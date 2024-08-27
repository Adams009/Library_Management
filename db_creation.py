from app import db, app

with app.app_context():
    db.create_all() # create the tables in the database