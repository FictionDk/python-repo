#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script to transfer document chunks from CSV to PostgreSQL database.
Reads document_chunk.csv using utils and writes to database using operator_kg.
"""

from typing import Dict, Any, List
import logging
from utils import read_graph_from_csv
from operator_kg import OperatorKG
from database import DatabaseConnection


def main():
    """
    Main function to read document chunks from CSV and write to PostgreSQL database.
    
    Steps:
    1. Read document_chunk.csv using read_graph_from_csv from utils
    2. Extract chunks data (stored in 'relations' key by the utility function)
    3. Initialize database connection and OperatorKG
    4. Write chunks to database using write_document_chunks method
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    try:
        # Read document chunks from CSV file
        # Note: read_graph_from_csv returns data with 'entities' and 'relations' keys
        # For document chunks, we use the 'relations' key based on the function's structure
        logger.info("Reading document_chunk.csv file...")
        data = read_graph_from_csv(nodes_file='document_chunk.csv', edges_file='document_chunk.csv')
        
        # Extract chunks from the data
        # The read_graph_from_csv function puts all rows in both 'entities' and 'relations'
        # We'll use 'relations' for document chunks
        chunks: List[Dict[str, Any]] = data.get('relations', [])
        
        if not chunks:
            logger.warning("No chunks found in document_chunk.csv")
            return
        
        logger.info(f"Successfully read {len(chunks)} chunks from CSV")
        
        # Initialize database connection and operator
        logger.info("Initializing database connection...")
        db_conn = DatabaseConnection()
        kg_operator = OperatorKG(db_conn)
        
        # Write chunks to database
        logger.info("Writing chunks to database...")
        inserted_count = kg_operator.write_document_chunks(chunks)
        
        logger.info(f"Successfully wrote {inserted_count} chunks to database")
        
    except FileNotFoundError as e:
        logger.error(f"CSV file not found: {e}")
        #raise
    except Exception as e:
        logger.error(f"Error processing document chunks: {e}")
        #raise


if __name__ == "__main__":
    main()
    while True:
        user_input = input("按回车键退出，或输入任意内容后回车以重试: ")
        if user_input == "":
            print("收到回车，程序退出。")
            break