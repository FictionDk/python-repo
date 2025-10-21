import os
import psycopg2
from typing import List, Dict, Any
from psycopg2.pool import SimpleConnectionPool
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

    def close_all_connections(self):
        self.pool_map[DatabaseOperator.KG].closeall()
        self.pool_map[DatabaseOperator.LG].closeall() 

    def insert_batch(self, sql: str, documents: List[Dict[str, Any]], db_opt: DatabaseOperator) -> int:
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
                cursor.executemany(sql, documents)
                conn.commit()
                return len(documents)
                
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Error exec(insert): {sql}: {str(e)}")
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
                cursor.execute(sql)
                return cursor.fetchall()

        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Error exec(read): {sql}: {str(e)}")
        finally:
            if conn:
                self.pool_map[db_opt].putconn(conn)
                
    def update(self, update_sql: str, params: tuple, db_opt: DatabaseOperator) -> int:
        """
        Execute an UPDATE statement on the specified database.
        
        Args:
            update_sql (str): The UPDATE SQL statement
            params (tuple): Parameters for the SQL statement
            db_opt (DatabaseOperator): Which database to update (LG or KG)
            
        Returns:
            int: Number of rows affected
        """
        conn = None
        try:
            conn : psycopg2.extensions.connection = self.pool_map[db_opt].getconn()
            if not conn:
                raise Exception("Failed to get database connection")

            with conn.cursor() as cursor:
                cursor.execute(update_sql, params)
                conn.commit()
                return cursor.rowcount
                
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Error executing UPDATE statement: {str(e)}")
        finally:
            if conn:
                self.pool_map[db_opt].putconn(conn)
