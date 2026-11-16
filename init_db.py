from app import create_app, db
from app.models import User, Property, Stand
from app.schema import upgrade_stand_locations
from pathlib import Path
from datetime import datetime, timezone
import sqlite3
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    # Back up legacy SQLite databases before adding the stand location columns.
    database_path = Path(db.engine.url.database)
    inspector = inspect(db.engine)
    if db.engine.dialect.name == 'sqlite' and database_path.is_file() and inspector.has_table('stands'):
        columns = {column['name'] for column in inspector.get_columns('stands')}
        if not {'latitude', 'longitude'}.issubset(columns):
            stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
            backup_path = database_path.with_name(f'{database_path.stem}.before-map-{stamp}.db')
            with sqlite3.connect(str(database_path)) as source, sqlite3.connect(str(backup_path)) as backup:
                source.backup(backup)
            print(f"Saved pre-map database backup at {backup_path}")
    # Build the database tables from the models
    db.create_all()
    upgrade_stand_locations()
    print(f"Database initialized/upgraded successfully at {db.engine.url.database}!")
