from app import app, db
from sqlalchemy import inspect

with app.app_context(): # needed to use the app context to access the database within the app
    inspector = inspect(db.engine) # needed to inspect the database
    tables = inspector.get_table_names() # needed to get the table names
    print(tables)