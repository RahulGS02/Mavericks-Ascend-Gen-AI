"""
Custom SQLAlchemy types for cross-database compatibility
"""
from sqlalchemy import TypeDecorator, CHAR, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID, JSONB as PostgreSQL_JSONB, ARRAY as PostgreSQL_ARRAY
import uuid
import json


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.

    Uses PostgreSQL's UUID type when available, otherwise uses
    CHAR(36) for other databases like SQLite.

    This allows the same model code to work with both PostgreSQL
    (production) and SQLite (testing).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgreSQL_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value) if not isinstance(value, uuid.UUID) else value
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value)) if value else None
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value


class JSON(TypeDecorator):
    """
    Platform-independent JSON type.

    Uses PostgreSQL's JSONB type when available, otherwise uses
    TEXT with JSON serialization for other databases like SQLite.

    This allows the same model code to work with both PostgreSQL
    (production) and SQLite (testing).
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgreSQL_JSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            return json.loads(value)


class StringArray(TypeDecorator):
    """
    Platform-independent ARRAY type for string arrays.

    Uses PostgreSQL's ARRAY type when available, otherwise uses
    TEXT with JSON serialization for other databases like SQLite.

    This allows the same model code to work with both PostgreSQL
    (production) and SQLite (testing).
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgreSQL_ARRAY(String))
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            # Convert list to JSON string for SQLite
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            # Convert JSON string back to list for SQLite
            return json.loads(value)
