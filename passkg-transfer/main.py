from database import DatabaseConnection
from operator_lg import OperatorLG
from operator_kg import OperatorKG
from utils import map_lightrag_to_documents, map_lightrag_chunks_to_document_chunks
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('passkg_transfer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def transfer():
    """
    Main function to orchestrate the data transfer process.
    """
    db_conn = None
    try:
        db_conn = DatabaseConnection()
        # Initialize reader and writer
        lgOpt, kgOpt = OperatorLG(db_conn), OperatorKG(db_conn)
        
        # Read all data from source database
        logger.info("Reading data from source database...")
        data = lgOpt.read_all_data()
        
        full_docs = data['full_docs']
        doc_chunks = data['doc_chunks']
        
        logger.info(f"Read {len(full_docs)} full documents and {len(doc_chunks)} chunks")
        
        # Group chunks by full_doc_id for mapping
        chunks_by_doc = {}
        for chunk in doc_chunks:
            doc_id = chunk['full_doc_id']
            if doc_id not in chunks_by_doc:
                chunks_by_doc[doc_id] = []
            chunks_by_doc[doc_id].append(chunk)
        
        # Transform data for target database
        logger.info("Transforming data for target database...")
        documents = []
        document_chunks = []
        
        for doc in full_docs:
            # Map full doc to documents table
            doc_chunks_list = chunks_by_doc.get(doc['id'], [])
            mapped_doc = map_lightrag_to_documents(doc, doc_chunks_list)
            documents.append(mapped_doc)

            # Map chunks to document_chunks table
            for chunk in doc_chunks_list:
                mapped_chunk = map_lightrag_chunks_to_document_chunks(chunk)
                document_chunks.append(mapped_chunk)
        
        logger.info(f"Transformed {len(documents)} documents and {len(document_chunks)} chunks")
        # print(f"{documents[0]} \n {document_chunks[0]}")

        #Write data to target database
        logger.info("Writing data to target database...")
        docs_written = kgOpt.write_document(documents)
        chunks_written = kgOpt.write_document_chunks(document_chunks)
        
        logger.info(f"Successfully wrote {docs_written} documents and {chunks_written} chunks to target database")
        
    except Exception as e:
        logger.error(f"Error during data transfer: {str(e)}")
        sys.exit(1)
        
    finally:
        # Close all database connections
        if db_conn:
            db_conn.close_all_connections()
            logger.info("Closed all database connections")


def fill_doc_name():
    db_conn = DatabaseConnection()
    lgOpt = OperatorLG(db_conn)
    print(f"exec doc filling: {lgOpt.transfer_doc_name()}")

def main():
    transfer()
    # fill_doc_name()

if __name__ == "__main__":
    main()
