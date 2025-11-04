from nebula_export import export_nebula_data
from utils import save_graph_to_csv, save_to_csv
from database import DatabaseConnection
from operator_kg import OperatorKG

from neo_exporter import export_neo4j_data

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kg_export.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def export_to_csv(tables: list[str]):
    db_conn = None
    try:
        db_conn = DatabaseConnection()
        kg_opt = OperatorKG(db_conn)
        for table_name in tables:
            data = kg_opt.export_table(table_name)
            if len(data) > 0:
                headers = list(data[0].keys())
                save_to_csv(data, headers, f"{table_name}.csv")
                logger.info(f"Exported {len(data)} records to {table_name}")
            else:
                logger.info(f"Exported {table_name} failed, empty or name err")
    except Exception as e:
        logger.error(f"Error during export to CSV: {str(e)}")
        raise
    finally:
        if db_conn:
            db_conn.close_all_connections()
            logger.info("Closed all database connections")

def export_kg():
    data = export_nebula_data('cowherd')
    save_graph_to_csv(data)
    export_to_csv(['documents','document_chunks','graph_vdb_entity'])

def export_neo():
    data = export_neo4j_data()
    save_graph_to_csv(data,nodes_file="neo_node.csv", edges_file="neo_edge.csv")

if __name__ == "__main__":
    export_neo()
