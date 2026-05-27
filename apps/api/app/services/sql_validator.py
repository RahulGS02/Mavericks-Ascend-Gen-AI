"""
SQL Validator - Security Layer for Natural Language to SQL
Validates generated SQL queries to prevent SQL injection and dangerous operations
"""
import re
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)

# Dangerous SQL keywords that should NEVER appear in queries
DANGEROUS_KEYWORDS = [
    'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER',
    'CREATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', 'CALL',
    'UNION', 'INTO OUTFILE', 'LOAD_FILE', 'DUMPFILE',
    'PROCEDURE', 'FUNCTION', 'TRIGGER', 'VIEW', 'INDEX',
    'LOCK', 'UNLOCK', 'REPLACE', 'MERGE', 'UPSERT',
    'COPY', 'BULK', 'IMPORT', 'EXPORT'
]

# Suspicious patterns that might indicate injection attempts.
# Note: comment patterns (-- and /* */) are NOT listed here because comments
# are stripped before this check runs. Listing them would cause false positives
# when -- or /* appear inside quoted string literals.
SUSPICIOUS_PATTERNS = [
    r';\s*SELECT',  # Multiple statements
    r';\s*INSERT',
    r';\s*UPDATE',
    r';\s*DELETE',
    r';\s*DROP',
    r'xp_',  # Extended stored procedures (SQL Server)
    r'sp_',  # System stored procedures
    r'@@',  # System variables
    r'\bCHAR\s*\(',  # CHAR() function (often used in injection)
    r'\bCONCAT_WS\s*\(',  # Suspicious concatenation
    r'WAITFOR\s+DELAY',  # Time-based injection
    r'BENCHMARK\s*\(',  # MySQL benchmark (timing attack)
    r'SLEEP\s*\(',  # Sleep function (timing attack)
    r'pg_sleep\s*\(',  # PostgreSQL sleep
    r'DBMS_',  # Oracle DBMS packages
    r'UTL_',  # Oracle utility packages
]


def validate_sql_query(sql: str) -> Tuple[bool, str, List[str]]:
    """
    Validates that SQL query is safe to execute.

    Strips SQL comments before checking so that AI-generated queries with
    inline comments don't cause false rejections.

    Args:
        sql: The SQL query string to validate

    Returns:
        Tuple of (is_valid: bool, error_message: str, warnings: List[str])
    """
    warnings = []

    if not sql or not sql.strip():
        return False, "SQL query is empty", []

    # Pre-strip comments so they don't trigger false rejections.
    # The sanitize step will do this again; this just avoids rejecting
    # AI-generated SQL that happens to include comments.
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    sql = re.sub(r"--[^\n]*", " ", sql)
    sql = re.sub(r"[ \t]+", " ", sql).strip()

    sql_stripped = sql.strip()
    sql_upper = sql_stripped.upper()

    # Check 1: Must start with SELECT
    if not sql_upper.startswith('SELECT'):
        return False, "Only SELECT queries are allowed. Query must start with SELECT.", []
    
    # Check 2: Verify it's actually a SELECT and not disguised as something else
    # Remove the SELECT keyword and check if dangerous keywords appear before FROM
    first_from = sql_upper.find('FROM')
    if first_from > 0:
        select_part = sql_upper[:first_from]
        for keyword in DANGEROUS_KEYWORDS:
            if keyword in select_part and keyword != 'SELECT':
                return False, f"Dangerous keyword '{keyword}' detected in SELECT clause", []
    
    # Check 3: Look for dangerous keywords anywhere in the query
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in sql_upper:
            return False, f"Dangerous keyword detected: {keyword}", []
    
    # Check 4: Check for semicolons (prevents multiple statements)
    semicolon_count = sql.count(';')
    if semicolon_count > 1:
        return False, "Multiple statements detected (multiple semicolons). Only single SELECT queries allowed.", []
    
    # Allow one trailing semicolon but warn about it
    if semicolon_count == 1:
        if not sql_stripped.endswith(';'):
            return False, "Semicolon detected in middle of query. Only single SELECT queries allowed.", []
        warnings.append("Query has trailing semicolon (will be removed)")
    
    # Check 5: Confirm no remaining comment markers (they were stripped at entry;
    # if any survived, that means they were inside string literals — still safe
    # to allow, but warn).
    if '--' in sql or '/*' in sql:
        warnings.append("SQL appears to contain comment-like strings inside quoted literals (ignored)")

    # Check 6: Check for suspicious patterns
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, sql, re.IGNORECASE):
            return False, f"Suspicious SQL pattern detected: {pattern}", []
    
    # Check 7: No LIMIT is fine — sanitize_sql_query() adds LIMIT 1000 automatically
    if 'LIMIT' not in sql_upper:
        warnings.append("No LIMIT clause — system will add LIMIT 1000 safety cap")
    
    # Check 8: Check for nested queries (subqueries are OK, but be cautious)
    select_count = sql_upper.count('SELECT')
    if select_count > 3:
        warnings.append(f"Query contains {select_count} SELECT statements (nested queries detected)")
    
    # Check 9: Verify proper FROM clause
    if 'FROM' not in sql_upper:
        return False, "Query must contain FROM clause to specify table(s)", []
    
    # Check 10: Check for excessive wildcards in LIKE
    like_count = sql.count('%')
    if like_count > 10:
        warnings.append(f"Query contains {like_count} wildcard characters - may be slow")
    
    # Check 11: Basic syntax validation - check for balanced parentheses
    if sql.count('(') != sql.count(')'):
        return False, "Unbalanced parentheses in query", []
    
    # Check 12: Validate quote balance
    single_quotes = sql.count("'") - sql.count("\\'")  # Exclude escaped quotes
    if single_quotes % 2 != 0:
        return False, "Unbalanced single quotes in query", []
    
    # Check 13: Check query length (prevent extremely long queries)
    if len(sql) > 10000:
        return False, "Query is too long (max 10000 characters)", []
    
    # Check 14: Ensure query doesn't try to access system tables
    system_tables = ['pg_catalog', 'information_schema', 'pg_', 'sys.']
    for sys_table in system_tables:
        if sys_table.lower() in sql.lower():
            return False, f"Access to system table/schema '{sys_table}' is not allowed", []
    
    logger.info(f"✅ SQL validation passed{' with warnings' if warnings else ''}")
    if warnings:
        for warning in warnings:
            logger.warning(f"   ⚠️  {warning}")
    
    return True, "Valid SQL query", warnings


def sanitize_sql_query(sql: str) -> str:
    """
    Sanitizes SQL query by removing dangerous/problematic elements.

    Strips SQL comments (-- and /* */), removes trailing semicolon,
    and enforces a LIMIT cap of 1000.

    Args:
        sql: The SQL query to sanitize

    Returns:
        Sanitized SQL query string
    """
    sql = sql.strip()

    # Remove block comments (/* ... */) — may span multiple lines
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)

    # Remove line comments (-- to end of line)
    sql = re.sub(r"--[^\n]*", " ", sql)

    # Collapse extra whitespace introduced by comment removal
    sql = re.sub(r"[ \t]+", " ", sql)
    sql = re.sub(r"\n{3,}", "\n\n", sql)
    sql = sql.strip()

    # Remove trailing semicolon
    if sql.endswith(';'):
        sql = sql[:-1].strip()

    # Add LIMIT if not present
    if 'LIMIT' not in sql.upper():
        sql = f"{sql} LIMIT 1000"

    # Ensure LIMIT is not too high
    limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
    if limit_match:
        limit_value = int(limit_match.group(1))
        if limit_value > 1000:
            sql = re.sub(r'LIMIT\s+\d+', 'LIMIT 1000', sql, flags=re.IGNORECASE)
            logger.warning(f"LIMIT reduced from {limit_value} to 1000 for safety")

    return sql


def get_query_tables(sql: str) -> List[str]:
    """
    Extract table names from SQL query
    
    Args:
        sql: SQL query string
    
    Returns:
        List of table names referenced in the query
    """
    tables = []
    sql_upper = sql.upper()
    
    # Find all FROM and JOIN clauses
    from_pattern = r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
    matches = re.findall(from_pattern, sql, re.IGNORECASE)
    
    for match in matches:
        table_name = match.lower()
        if table_name not in tables:
            tables.append(table_name)
    
    return tables
