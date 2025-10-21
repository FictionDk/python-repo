from typing import List, Dict, Any
from database import DatabaseConnection, DatabaseOperator
from utils import extract_filename_from_path


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
                'id': row[0],
                'workspace': row[1],
                'doc_name': row[2],
                'content': row[3],
                'meta': row[4],
                'create_time': row[5],
                'update_time': row[6]
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
                'id': row[0],
                'workspace': row[1],
                'full_doc_id': row[2],
                'chunk_order_index': row[3],
                'tokens': row[4],
                'content': row[5],
                'content_vector': row[6],
                'file_path': row[7],
                'create_time': row[8],
                'update_time': row[9],
                'llm_cache_list': row[10]
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
        
    def transfer_doc_name(self) -> int:
        """
        Transfer document names from file_path to doc_name field in lightrag_doc_full table.
        For documents where doc_name is null, extract the name from the file_path of associated chunks
        by splitting on '.' and taking the first part.
        
        Returns:
            int: Number of documents updated
        """
        # Read all data
        data = self.read_all_data()
        full_docs = data['full_docs']
        doc_chunks = data['doc_chunks']
        print(full_docs[0]['doc_name'])
        
        # Create a mapping of full_doc_id to file_path from chunks
        # Since all chunks for the same document have the same file_path, we can use any chunk
        file_path_map = {}
        for chunk in doc_chunks:
            full_doc_id = chunk['full_doc_id']
            if full_doc_id not in file_path_map:
                file_path_map[full_doc_id] = chunk['file_path']
        
        # Filter documents where doc_name is null or empty
        docs_to_update = [doc for doc in full_docs if not doc['doc_name']]
        
        # Update count
        updated_count = 0
        
        # Generate and execute UPDATE statements
        update_sql = """
        UPDATE lightrag_doc_full 
        SET doc_name = %s, update_time = CURRENT_TIMESTAMP 
        WHERE id = %s
        """
        
        for doc in docs_to_update:
            full_doc_id = doc['id']
            # Get file_path from associated chunks
            file_path = file_path_map.get(full_doc_id)
            if file_path:
                # Extract doc_name using the utility function
                doc_name = extract_filename_from_path(file_path)
                if doc_name:
                    # Execute UPDATE
                    try:
                        rows_affected = self.db_conn.update(update_sql, (doc_name, full_doc_id), DatabaseOperator.LG)
                        if rows_affected > 0:
                            updated_count += 1
                    except Exception as e:
                        print(f"Error updating document {full_doc_id}: {str(e)}")
                        continue
        
        return updated_count
