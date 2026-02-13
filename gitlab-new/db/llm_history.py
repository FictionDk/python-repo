"""
LLM History Table Mixin
Handles operations for llm_history table (LLM request/response history)
"""

import sqlite3
from typing import Dict, Any, List, Optional


class LLMHistoryMixin:
    """Mixin class for llm_history table operations"""
    
    def _create_llm_history_table(self):
        """Create llm_history table according to PLAN.md specification"""
        self.connect().execute('''
            CREATE TABLE IF NOT EXISTS llm_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                create_at TEXT NOT NULL,
                req_content TEXT NOT NULL,
                resp_content TEXT NOT NULL,
                sucess BOOLEAN
            )
        ''')
        self.connect().commit()
    
    def insert_llm_history(
        self,
        type: str,
        create_at: str,
        req_content: str
    ) -> int:
        """
        Insert a new LLM history record
        
        Args:
            type: The type of request (e.g., "日汇总", "周汇总", "提交评价")
            create_at: The timestamp for this record (ISO 8601 format)
            req_content: The request content sent to LLM
            
        Returns:
            The ID of the inserted record
        """
        cursor = self.connect().execute('''
            INSERT INTO llm_history (type, create_at, req_content, resp_content, sucess)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            type,
            create_at,
            req_content,
            '',  # Initial empty response
            False  # Initial success status will be updated later
        ))
        self.connect().commit()
        
        return cursor.lastrowid
    
    def update_response(
        self,
        record_id: int,
        resp_content: str,
        success: bool
    ) -> bool:
        """
        Update the response content and success status for an LLM history record
        
        Args:
            record_id: The ID of the record to update
            resp_content: The response content from LLM (with thinking content removed)
            success: Whether the request was successful
            
        Returns:
            True if update was successful, False otherwise
        """
        cursor = self.connect().execute('''
            UPDATE llm_history
            SET resp_content = ?, sucess = ?
            WHERE id = ?
        ''', (resp_content, success, record_id))
        
        self.connect().commit()
        return cursor.rowcount > 0
    
    def get_llm_history(
        self,
        limit: Optional[int] = None,
        type_filter: Optional[str] = None
    ) -> List[sqlite3.Row]:
        """
        Query LLM history records
        
        Args:
            limit: Maximum number of records to return (optional)
            type_filter: Filter by type (optional)
            
        Returns:
            List of database rows with LLM history information
        """
        query = '''
            SELECT id, type, create_at, req_content, resp_content, sucess
            FROM llm_history
        '''
        
        params = []
        
        if type_filter:
            query += ' WHERE type = ?'
            params.append(type_filter)
        
        query += ' ORDER BY create_at DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor = self.connect().execute(query, params)
        return cursor.fetchall()
    
    def _row_to_llm_history(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to LLM history dictionary"""
        return {
            'id': row['id'],
            'type': row['type'],
            'create_at': row['create_at'],
            'req_content': row['req_content'],
            'resp_content': row['resp_content'],
            'success': bool(row['sucess'])
        }
