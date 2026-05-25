"""
Natural Language Query API Endpoints
Allows SuperAdmins to query database using natural language
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging
import uuid as uuid_lib

from ....database import get_db
from ....models.user import User
from ....utils.dependencies import get_super_admin
from ....services.schema_provider import get_database_schema_context
from ....services.ai_service import ai_service
from ....services.sql_validator import validate_sql_query, sanitize_sql_query, get_query_tables
from ....services.query_executor import execute_safe_query
from ....services.excel_generator import excel_generator
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class NaturalLanguageQueryRequest(BaseModel):
    """Request model for natural language query"""
    query: str = Field(..., min_length=5, max_length=500, description="Natural language query")
    include_stats: bool = Field(True, description="Include statistical aggregations")
    max_rows: Optional[int] = Field(None, ge=1, le=1000, description="Maximum rows to return")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show me mavericks available for deployment with Python skills",
                "include_stats": True,
                "max_rows": 100
            }
        }


class QueryResult(BaseModel):
    """Response model for query results"""
    query_id: str = Field(..., description="Unique query identifier")
    natural_query: str = Field(..., description="Original natural language query")
    generated_sql: str = Field(..., description="Generated SQL query")
    explanation: str = Field(..., description="Explanation of what the query does")
    tables_used: list[str] = Field(..., description="Database tables used in query")
    data: list[dict] = Field(..., description="Query results")
    statistics: dict = Field(..., description="Query statistics and aggregations")
    executed_at: str = Field(..., description="Execution timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "550e8400-e29b-41d4-a716-446655440000",
                "natural_query": "Show me available mavericks",
                "generated_sql": "SELECT * FROM mavericks WHERE deployment_status = 'AVAILABLE' LIMIT 100",
                "explanation": "Returns all mavericks with AVAILABLE deployment status",
                "tables_used": ["mavericks"],
                "data": [{"id": "uuid-1", "name": "John Doe"}],
                "statistics": {"total_rows": 45, "execution_time_ms": 123.45},
                "executed_at": "2026-05-23T10:30:00"
            }
        }


@router.post("/search", response_model=QueryResult)
async def search_with_natural_language(
    request: NaturalLanguageQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Execute natural language query and return results
    
    **Only SuperAdmins can use this endpoint**
    
    Process:
    1. Get database schema context
    2. Generate SQL from natural language using AI
    3. Validate SQL for security
    4. Execute query safely
    5. Return results with statistics
    
    Example queries:
    - "Show me mavericks available for deployment"
    - "List active batches with their enrollment counts"
    - "Find mavericks with Python skills above 80%"
    - "Count mavericks by deployment status"
    """
    try:
        logger.info(f"Natural language query from SuperAdmin {current_user.email}: {request.query}")
        
        # Step 1: Get schema context
        schema_context = get_database_schema_context()
        
        # Step 2: Generate SQL using AI
        ai_result = await ai_service.generate_sql_from_natural_language(
            natural_query=request.query,
            schema_context=schema_context
        )
        
        if not ai_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate SQL query. AI service may be unavailable."
            )
        
        generated_sql = ai_result['sql']
        explanation = ai_result.get('explanation', 'SQL query generated from natural language')
        tables_used = ai_result.get('tables_used', [])
        
        logger.info(f"Generated SQL: {generated_sql[:100]}...")
        
        # Step 3: Validate SQL for security
        is_valid, error_message, warnings = validate_sql_query(generated_sql)
        
        if not is_valid:
            logger.error(f"SQL validation failed: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Generated SQL failed security validation: {error_message}"
            )
        
        if warnings:
            for warning in warnings:
                logger.warning(f"SQL validation warning: {warning}")
        
        # Step 4: Sanitize SQL (add LIMIT, remove trailing semicolon, etc.)
        sanitized_sql = sanitize_sql_query(generated_sql)
        
        # Apply max_rows if specified
        if request.max_rows:
            import re
            sanitized_sql = re.sub(r'LIMIT\s+\d+', f'LIMIT {request.max_rows}', sanitized_sql, flags=re.IGNORECASE)
        
        logger.info(f"Executing sanitized SQL: {sanitized_sql[:100]}...")
        
        # Step 5: Execute query
        try:
            data, stats = await execute_safe_query(db, sanitized_sql)
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Query execution failed: {str(e)}"
            )
        
        # Step 6: Prepare response
        query_id = str(uuid_lib.uuid4())
        
        # Extract table names if not provided by AI
        if not tables_used:
            tables_used = get_query_tables(sanitized_sql)
        
        logger.info(f"✅ Query executed successfully: {stats.get('total_rows', 0)} rows returned in {stats.get('execution_time_ms', 0)}ms")
        
        return QueryResult(
            query_id=query_id,
            natural_query=request.query,
            generated_sql=sanitized_sql,
            explanation=explanation,
            tables_used=tables_used,
            data=data if request.include_stats else data[:100],  # Limit data in response
            statistics=stats,
            executed_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in natural language query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/search/download")
async def download_query_results_excel(
    request: NaturalLanguageQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Execute natural language query and download results as Excel
    
    **Only SuperAdmins can use this endpoint**
    
    Returns an Excel file with:
    - Sheet 1: Query Results (all data)
    - Sheet 2: Statistics (aggregations, counts, averages)
    - Sheet 3: Query Info (natural query, SQL, explanation)
    
    Example: Download list of available mavericks with their skills
    """
    try:
        logger.info(f"Excel download request from SuperAdmin {current_user.email}: {request.query}")
        
        # Execute the same query pipeline
        schema_context = get_database_schema_context()
        
        ai_result = await ai_service.generate_sql_from_natural_language(
            natural_query=request.query,
            schema_context=schema_context
        )
        
        if not ai_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate SQL query"
            )
        
        generated_sql = ai_result['sql']
        
        # Validate and sanitize
        is_valid, error_message, warnings = validate_sql_query(generated_sql)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SQL validation failed: {error_message}"
            )
        
        sanitized_sql = sanitize_sql_query(generated_sql)
        
        # Apply max_rows if specified
        if request.max_rows:
            import re
            sanitized_sql = re.sub(r'LIMIT\s+\d+', f'LIMIT {request.max_rows}', sanitized_sql, flags=re.IGNORECASE)
        
        # Execute query
        try:
            data, stats = await execute_safe_query(db, sanitized_sql)
            logger.info(f"Query executed: {len(data)} rows, {len(stats.get('columns', []))} columns")
        except Exception as e:
            logger.error(f"Query execution failed in download: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Query execution failed: {str(e)}"
            )

        # Generate Excel
        query_info = {
            'natural_query': request.query,
            'sql': sanitized_sql,
            'explanation': ai_result.get('explanation', ''),
            'tables_used': ai_result.get('tables_used', [])
        }

        try:
            logger.info(f"Generating Excel with {len(data)} rows")
            excel_buffer = excel_generator.generate_excel(data, stats, query_info)
            logger.info(f"Excel buffer size: {excel_buffer.tell()} bytes")

            # IMPORTANT: Seek to beginning of buffer before streaming
            excel_buffer.seek(0)
            logger.info("Excel buffer ready for streaming")
        except Exception as e:
            logger.error(f"Excel generation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Excel generation failed: {str(e)}"
            )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"query_results_{timestamp}.xlsx"

        logger.info(f"✅ Excel file generated: {filename} ({stats.get('total_rows', 0)} rows)")

        # Return as downloadable file
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating Excel download: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Excel file: {str(e)}"
        )
