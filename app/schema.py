"""Additive upgrade for SQLite databases created before stand map locations existed."""

from sqlalchemy import inspect, text
from app import db


def upgrade_stand_locations():
    """Preserve existing rows and add only missing, nullable location columns."""
    with db.engine.begin() as connection:
        inspector = inspect(connection)
        if not inspector.has_table('stands'):
            return
        columns = {column['name'] for column in inspector.get_columns('stands')}
        for name in ('latitude', 'longitude'):
            if name not in columns:
                connection.execute(text(f'ALTER TABLE stands ADD COLUMN {name} FLOAT'))
