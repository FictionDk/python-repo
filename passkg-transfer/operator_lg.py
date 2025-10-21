from typing import List, Dict, Any
from database import DatabaseConnection, DatabaseOperator


doc_read_sql = '''
SELECT id, workspace, doc_name, content, meta, create_time, update_time
FROM lightrag_doc_full
'''

chunk_read_sql = '''
SELECT id, workspace, full_doc_id, chunk_order_index, tokens, content, 
        content_vector, file_path, create_time, update_time, llm_cache_list
FROM lightrag_doc_chunks
'''

class OperatorLG:
    """
    Handles reading data from the source PostgreSQL database (lightrag schema).
    """
    def __init__(self, db_connection: DatabaseConnection):
        self.db_conn = db_connection
    
    def read_full_docs(self) -> List[Dict[str, Any]]:
        """
        Read all records from lightrag_doc_full table.
        Returns:
            List[Dict[str, Any]]: List of document records
        """
        results = self.db_conn.read(doc_read_sql, DatabaseOperator.LG)
        records = []
        for row in results:
            record = {
                'id': row['id'],
                'workspace': row['workspace'],
                'doc_name': row['doc_name'],
                'content': row['content'],
                'meta': row['meta'],
                'create_time': row['create_time'],
                'update_time': row['update_time']
            }
            records.append(record)
        return records

    
    def read_doc_chunks(self) -> List[Dict[str, Any]]:
        """
        Read all records from lightrag_doc_chunks table.
        
        Returns:
            List[Dict[str, Any]]: List of chunk records
        """
        results = self.db_conn.read(chunk_read_sql, DatabaseOperator.LG)
        records = []
        for row in results:
            record = {
                'id': row['id'],
                'workspace': row['workspace'],
                'full_doc_id': row['full_doc_id'],
                'chunk_order_index': row['chunk_order_index'],
                'tokens': row['tokens'],
                'content': row['content'],
                'content_vector': row['content_vector'],
                'file_path': row['file_path'],
                'create_time': row['create_time'],
                'update_time': row['update_time'],
                'llm_cache_list': row['llm_cache_list']
            }
            records.append(record)
        return records
    
    def read_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Read all data from both lightrag tables.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary containing data from both tables
        """
        full_docs = self.read_full_docs()
        doc_chunks = self.read_doc_chunks()
        
        return {
            'full_docs': full_docs,
            'doc_chunks': doc_chunks
        }
