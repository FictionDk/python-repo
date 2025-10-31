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
    Handles writing data to and reading/exporting data from the target PostgreSQL database (passkg schema).
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
        return self.db_conn.insert_batch(chunk_insert_sql, chunks, DatabaseOperator.KG)

    def export_table(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Export all data from the tabel.
        
        Args:
            tabel_name (str): Name of the table to export
            
        Returns:
            List[Dict[str, Any]]: List of document records
            
        Raises:
            ValueError: If the table name is not in the allowed list
        """
        allowed_tables = {
            "chat_logs",
            "documents",
            "document_answers",
            "document_chunks",
            "document_domain_trees",
            "document_histories",
            "document_questions",
            "graph_vdb_entity",
            "model_configs",
            "projects",
            "prompts",
            "workspaces",
            "workspace_members",
            "workspace_task_models"
        }
        if table_name not in allowed_tables:
            print(f"Table '{table_name}' is not in the allowed list for export. ")
            print(f"Allowed tables: {sorted(allowed_tables)}")
            return []
        return self.db_conn.read_all(table_name, DatabaseOperator.KG)

    def export_documents(self) -> List[Dict[str, Any]]:
        """
        Export all documents from the documents table.
        
        Returns:
            List[Dict[str, Any]]: List of document records
        """
        return self.db_conn.read_all("documents", DatabaseOperator.KG)
    
    
    def export_document_chunks(self) -> List[Dict[str, Any]]:
        """
        Export all document chunks from the document_chunks table.
        
        Returns:
            List[Dict[str, Any]]: List of document chunk records
        """
        return self.db_conn.read_all("document_chunks", DatabaseOperator.KG)
    
    
    def export_graph_vdb_entity(self) -> List[Dict[str, Any]]:
        """
        Export all graph VDB entities from the graph_vdb_entity table.
        
        Returns:
            List[Dict[str, Any]]: List of graph VDB entity records
        """
        return self.db_conn.read_all("graph_vdb_entity", DatabaseOperator.KG)
