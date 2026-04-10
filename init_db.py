from app import create_app, db
from app.models import User, Property, Stand

app = create_app()

with app.app_context():
    # Build the database tables from the models
    db.create_all()
    print("Database created successfully at instance/hunting.db!")
