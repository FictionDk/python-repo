from typing import List, Dict, Any
from database import DatabaseConnection, DatabaseOperator

doc_insert_sql = '''
INSERT INTO documents 
(id, content, extraction_prompt, workspace_id, created_at, chunks, 
    parent, is_project_doc, last_mod, process_status, name, type, summary, tags)
VALUES 
(%(id)s, %(content)s, %(extraction_prompt)s, %(workspace_id)s, %(created_at)s, 
    %(chunks)s, %(parent)s, %(is_project_doc)s, %(last_mod)s, %(process_status)s, 
    %(name)s, %(type)s, %(summary)s, %(tags)s)
ON CONFLICT (id) DO UPDATE SET
content = EXCLUDED.content,
name = EXCLUDED.name
'''

chunk_insert_sql = '''
INSERT INTO document_chunks 
(document_id, chunk_index, text, embedding)
VALUES 
(%(document_id)s, %(chunk_index)s, %(text)s, %(embedding)s)
ON CONFLICT (document_id, chunk_index) DO UPDATE SET
text = EXCLUDED.text,
embedding = EXCLUDED.embedding
'''


class OperatorKG:
    """
    Handles writing data to the target PostgreSQL database (passkg schema).
    """
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db_conn = db_connection
    
    def write_document(self, documents: List[Dict[str, Any]]) -> int:
        """
        Write documents to the documents table.
        Args:
            documents (List[Dict[str, Any]]): List of document data to write
        Returns:
            int: Number of records inserted
        """   
        return self.db_conn.insert_batch(doc_insert_sql, documents, DatabaseOperator.KG)

    
    def write_document_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Write document chunks to the document_chunks table.
        
        Args:
            chunks (List[Dict[str, Any]]): List of chunk data to write
            
        Returns:
            int: Number of records inserted
        """
        return self.db_conn.insert_batch(chunk_insert_sql, chunks, DatabaseOperator.LG)