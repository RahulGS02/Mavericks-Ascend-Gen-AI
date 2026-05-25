"""
Query Executor - Safe SQL Query Execution with Statistics
Executes validated SQL queries and returns results with metadata
"""
import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)


def serialize_value(value: Any) -> Any:
    """
    Serialize database values to JSON-compatible types
    
    Args:
        value: Value from database query
    
    Returns:
        JSON-serializable value
    """
    if value is None:
        return None
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, uuid.UUID):
        return str(value)
    elif isinstance(value, (list, dict)):
        return value  # JSONB data is already serializable
    elif isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    else:
        return value


async def execute_safe_query(
    db: Session,
    sql: str,
    timeout_seconds: int = 30
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Executes validated SQL query and returns results with statistics
    
    Args:
        db: SQLAlchemy database session
        sql: Validated SQL query (must be SELECT only)
        timeout_seconds: Query timeout in seconds (default: 30)
    
    Returns:
        Tuple of (results, statistics)
        
        results: List of dictionaries, one per row
        [
            {"id": "uuid-123", "name": "John", "email": "john@ex.com"},
            {"id": "uuid-456", "name": "Jane", "email": "jane@ex.com"}
        ]
        
        statistics: Dictionary with query metadata
        {
            "total_rows": 45,
            "columns": ["id", "name", "email"],
            "column_types": {"id": "uuid", "name": "str", "email": "str"},
            "execution_time_ms": 123.45,
            "aggregations": {
                "numeric_columns": {...},
                "string_columns": {...}
            }
        }
    
    Raises:
        SQLAlchemyError: If query execution fails
        TimeoutError: If query exceeds timeout
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Executing query: {sql[:100]}...")
        
        # Set statement timeout for safety
        db.execute(text(f"SET statement_timeout = {timeout_seconds * 1000}"))  # milliseconds
        
        # Execute query
        result = db.execute(text(sql))
        
        # Get column names and types
        if result.returns_rows:
            columns = list(result.keys())
        else:
            raise ValueError("Query did not return any rows structure")
        
        # Fetch all rows
        rows = result.fetchall()
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        logger.info(f"✅ Query executed successfully in {execution_time_ms:.2f}ms")
        logger.info(f"   Returned {len(rows)} rows, {len(columns)} columns")
        
        # Convert rows to list of dictionaries with serialized values
        data = []
        for row in rows:
            row_dict = {}
            for col in columns:
                value = getattr(row, col)
                row_dict[col] = serialize_value(value)
            data.append(row_dict)
        
        # Detect column types from data
        column_types = detect_column_types(data, columns)
        
        # Generate statistics
        stats = {
            "total_rows": len(data),
            "columns": columns,
            "column_types": column_types,
            "execution_time_ms": round(execution_time_ms, 2),
            "query_executed": sql,
            "executed_at": datetime.now().isoformat()
        }
        
        # Add aggregations if data exists
        if data:
            stats["aggregations"] = calculate_aggregations(data, columns, column_types)
        else:
            stats["aggregations"] = {}
        
        return data, stats
        
    except SQLAlchemyError as e:
        logger.error(f"❌ SQL execution error: {e}")
        raise
    
    except Exception as e:
        logger.error(f"❌ Unexpected error during query execution: {e}")
        raise
    
    finally:
        # Reset statement timeout
        try:
            db.execute(text("RESET statement_timeout"))
        except:
            pass


def detect_column_types(data: List[Dict[str, Any]], columns: List[str]) -> Dict[str, str]:
    """
    Detect data types of columns from sample data
    
    Args:
        data: List of row dictionaries
        columns: List of column names
    
    Returns:
        Dictionary mapping column names to types
    """
    column_types = {}
    
    for col in columns:
        # Get first non-None value to determine type
        sample_value = None
        for row in data:
            if row.get(col) is not None:
                sample_value = row[col]
                break
        
        if sample_value is None:
            column_types[col] = "null"
        elif isinstance(sample_value, bool):
            column_types[col] = "boolean"
        elif isinstance(sample_value, int):
            column_types[col] = "integer"
        elif isinstance(sample_value, float):
            column_types[col] = "float"
        elif isinstance(sample_value, str):
            # Check if it's a UUID
            try:
                uuid.UUID(sample_value)
                column_types[col] = "uuid"
            except (ValueError, AttributeError):
                # Check if it's a date/datetime string
                if 'T' in sample_value or '-' in sample_value:
                    column_types[col] = "datetime"
                else:
                    column_types[col] = "string"
        elif isinstance(sample_value, list):
            column_types[col] = "array"
        elif isinstance(sample_value, dict):
            column_types[col] = "object"
        else:
            column_types[col] = "unknown"
    
    return column_types


def calculate_aggregations(
    data: List[Dict[str, Any]], 
    columns: List[str],
    column_types: Dict[str, str]
) -> Dict[str, Any]:
    """
    Calculate statistical aggregations for numeric and string columns
    
    Args:
        data: List of row dictionaries
        columns: List of column names
        column_types: Dictionary of column types
    
    Returns:
        Dictionary with aggregations
    """
    aggregations = {
        "numeric": {},
        "string": {},
        "boolean": {},
        "summary": {}
    }
    
    total_rows = len(data)
    aggregations["summary"]["total_rows"] = total_rows
    
    for col in columns:
        col_type = column_types.get(col, "unknown")
        
        # Numeric aggregations
        if col_type in ["integer", "float"]:
            values = [row[col] for row in data if row.get(col) is not None and isinstance(row[col], (int, float))]
            
            if values:
                aggregations["numeric"][col] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": round(sum(values) / len(values), 2),
                    "sum": sum(values)
                }
        
        # String aggregations
        elif col_type == "string":
            values = [row[col] for row in data if row.get(col) is not None]
            
            if values:
                unique_values = list(set(values))
                aggregations["string"][col] = {
                    "count": len(values),
                    "unique_count": len(unique_values),
                    "null_count": total_rows - len(values)
                }
                
                # Include sample unique values (max 10)
                if len(unique_values) <= 10:
                    aggregations["string"][col]["unique_values"] = sorted(unique_values)
        
        # Boolean aggregations
        elif col_type == "boolean":
            values = [row[col] for row in data if row.get(col) is not None]
            
            if values:
                true_count = sum(1 for v in values if v)
                false_count = len(values) - true_count
                aggregations["boolean"][col] = {
                    "true_count": true_count,
                    "false_count": false_count,
                    "true_percentage": round(true_count / len(values) * 100, 2)
                }
    
    return aggregations
