import os
import psycopg2
from typing import List, Dict, Any
from psycopg2.pool import SimpleConnectionPool
from database import DatabaseConnection
from enum import Enum

from dotenv import load_dotenv

load_dotenv()


class DatabaseOperator(Enum):
    LG = "lightRAG"
    KG = "passKG"

class DatabaseConnection:
    """
    Handles database connections for both source (LG) and target (KG) databases.
    """

    def __init__(self):
        # Source database (LG) configuration
        self.lg_config = {
            'host': os.getenv('LG_HOST'),
            'port': int(os.getenv('LG_PORT')),
            'user': os.getenv('LG_USER'),
            'password': os.getenv('LG_PASSWORD'),
            'database': os.getenv('LG_DATABASE')
        }

        # Target database (KG) configuration
        self.kg_config = {
            'host': os.getenv('KG_HOST'),
            'port': int(os.getenv('KG_PORT')),
            'user': os.getenv('KG_USER'),
            'password': os.getenv('KG_PASSWORD'),
            'database': os.getenv('KG_DBNAME')
        }
        self._create_pools()

    def _create_pools(self):
        """Create connection pools for both databases."""
        try:
            self.pool_map: Dict[DatabaseOperator, SimpleConnectionPool] = {
                DatabaseOperator.LG: SimpleConnectionPool(1, 20, **self.lg_config),
                DatabaseOperator.KG: SimpleConnectionPool(1, 20, **self.kg_config)
            }
        except Exception as e:
            raise Exception(f"Error creating connection pools: {str(e)}")

    def insert_batch(self, insert_sql: str, documents: List[Dict[str, Any]], db_opt: DatabaseOperator) -> int:
        """
        Write documents to the documents table.
        
        Args:
            documents (List[Dict[str, Any]]): List of document data to write
            
        Returns:
            int: Number of records inserted
        """
        if not documents:
            return 0
        try:
            conn : psycopg2.extensions.connection = self.pool_map[db_opt].getconn()
            if not conn:
                raise Exception("Failed to get database connection")

            with conn.cursor() as cursor:
                # Execute batch insert
                cursor.executemany(insert_sql, documents)
                conn.commit()
                return len(documents)
                
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Error writing to documents table: {str(e)}")
        finally:
            if conn:
                self.pool_map[db_opt].putconn(conn)


    def read(self, sql: str, db_opt: DatabaseOperator) -> list[tuple[Any, ...]]:
        """
        Read all records from lightrag_doc_full table.
        Returns:
            List[Dict[str, Any]]: List of document records
        """
        conn = None
        try:
            conn : psycopg2.extensions.connection = self.pool_map[db_opt].getconn()
            if not conn:
                raise Exception("Failed to get database connection")

            with conn.cursor() as cursor:
                query = """
                SELECT id, workspace, doc_name, content, meta, create_time, update_time
                FROM lightrag_doc_full
                """
                cursor.execute(sql)
                results = cursor.fetchall()
                
                # Convert to list of dictionaries
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
                
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Error writing to documents table: {str(e)}")
        finally:
            if conn:
                self.pool_map[db_opt].putconn(conn)