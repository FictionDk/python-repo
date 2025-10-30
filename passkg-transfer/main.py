from database import DatabaseConnection
from operator_lg import OperatorLG
from operator_kg import OperatorKG
from utils import map_lightrag_to_documents, map_lightrag_chunks_to_document_chunks, schema_mapper, save_graph_to_csv, save_id_mapping_to_csv, read_graph_from_csv, save_to_csv
from neo_exporter import export_neo4j_data
from nebula_export import export_nebula_data
from nebula_import import grahp_import
from kg_import import post
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

        # Write data to target database
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

def _export_graph_data():
    logger.info("Exporting data from Neo4j...")
    raw_data = export_neo4j_data()
    logger.info(f"Exported {len(raw_data['nodes'])} nodes and {len(raw_data['relationships'])} relationships")
    # print(f"=>{raw_data['nodes'][0]}")
    # print(f"=>{raw_data['relationships'][0]}")

    # Step 3: Transform data to Nebula format
    logger.info("Mapping data to Nebula schema format...")
    mapped_data = schema_mapper(raw_data)
    logger.info(f"Mapped {len(mapped_data['entities'])} entities and {len(mapped_data['relations'])} relations")

    # Step 4: Save to CSV files
    logger.info("Saving data to CSV files...")
    save_graph_to_csv(mapped_data)

def _import_graph_data(workspace_id):
    data = read_graph_from_csv()
    # Use the new post method to send data to the remote API
    success = post(workspace_id, data=data)
    if success:
        logger.info("Graph data successfully pushed to remote API.")
    else:
        logger.error("Failed to push graph data to remote API.")
        raise Exception("Graph data import via API failed.")

# 图数据迁移
def migrate_graph_data():
    #_export_graph_data()
    #data = export_nebula_data('5vm9t8')
    #save_graph_to_csv(data)
    _import_graph_data('5vm9t8')
    logger.info("Graph data migration completed successfully!")

# 读取映射关系，写入csv
def export_mapping():
    db_conn = DatabaseConnection()
    lgOpt = OperatorLG(db_conn)
    mapping = lgOpt.read_chunk_to_full_doc_mapping()
    save_id_mapping_to_csv(mapping, 'chunk_to_full_doc_mapping.csv')
    logger.info(f"Exported {len(mapping)} chunk to full document mappings to CSV")

def export_to_csv():
    """
    Export data from documents, document_chunks, and graph_vdb_entity tables to CSV files.
    """
    db_conn = None
    try:
        db_conn = DatabaseConnection()
        kg_opt = OperatorKG(db_conn)
        
        # Export documents table
        logger.info("Exporting documents table...")
        documents = kg_opt.export_documents()
        if documents:
            # Get headers from the first document's keys
            headers = list(documents[0].keys())
            save_to_csv(documents, headers, 'documents.csv')
            logger.info(f"Exported {len(documents)} documents to documents.csv")
        else:
            logger.info("No documents found to export")
        
        # Export document_chunks table
        logger.info("Exporting document_chunks table...")
        chunks = kg_opt.export_document_chunks()
        if chunks:
            # Get headers from the first chunk's keys
            headers = list(chunks[0].keys())
            save_to_csv(chunks, headers, 'document_chunks.csv')
            logger.info(f"Exported {len(chunks)} document chunks to document_chunks.csv")
        else:
            logger.info("No document chunks found to export")
        
        # Export graph_vdb_entity table
        logger.info("Exporting graph_vdb_entity table...")
        entities = kg_opt.export_graph_vdb_entity()
        if entities:
            # Get headers from the first entity's keys
            headers = list(entities[0].keys())
            save_to_csv(entities, headers, 'graph_vdb_entity.csv')
            logger.info(f"Exported {len(entities)} graph VDB entities to graph_vdb_entity.csv")
        else:
            logger.info("No graph VDB entities found to export")
            
    except Exception as e:
        logger.error(f"Error during export to CSV: {str(e)}")
        raise
    finally:
        if db_conn:
            db_conn.close_all_connections()
            logger.info("Closed all database connections")


def main():
    # Execute the regular data transfer
    # transfer()
    # fill_doc_name()
    # export_mapping()
    migrate_graph_data()
    #export_to_csv()

if __name__ == "__main__":
    main()
