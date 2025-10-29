from typing import List, Dict, Any
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from nebula3.data.ResultSet import ResultSet
from nebula3.common.ttypes import Value
import logging
import os

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class NebulaExporter:
    """
    Handles exporting data from Nebula graph database to CSV files.
    Manages connection and data export operations.
    """
    
    def __init__(self):
        """
        Initialize Nebula connection using environment variables.
        """
        host = os.getenv('NEBULA_ADDRESS')
        port = int(os.getenv('NEBULA_PORT'))
        self.username = os.getenv('NEBULA_USERNAME')
        self.password = os.getenv('NEBULA_PASSWORD')
        self.config = Config()
        self.config.max_connection_pool_size = 10
        self.config.timeout = 3000000  # 30秒超时
        self.conn_pool = ConnectionPool()
        try:
            ok = self.conn_pool.init([(host, port)], self.config)
            if not ok:
                raise Exception("Failed to connect to Nebula Graph")
            print("✅ Successfully connected to Nebula Graph")
            self.session = self.conn_pool.get_session(self.username, self.password)
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            exit(1)

    def do_exec(self, sql, params: dict[str, Any] = None) -> ResultSet:
        """Execute and return result"""
        try:
            if params is None:
                return self.session.execute(sql)
            else:
                return self.session.execute_parameter(sql, params)
        except Exception as e:
            print(f"❌ Exec {sql}, {params} error: {e}")
            exit(0)

    def close(self):
        """Close connection"""
        if self.conn_pool:
            self.conn_pool.close()

    def export_entities(self, space: str) -> List[Dict[str, Any]]:
        """
        Export entities (vertices) from Nebula database.
        Args:
            space (str): The Nebula space to export from
            output_file (str, optional): Path to output CSV file. If None, returns data without writing to file.
        Returns:
            List[Dict[str, Any]]: List of entity data exported
        """
        # Use space
        r = self.do_exec(f"USE `{space}`")
        if not r.is_succeeded():
            logger.error(f"Failed to use space '{space}', err= {r.error_msg() if r else 'Unknown error'}")
            return []

        # Query all entities
        query = "MATCH (e:entity) RETURN id(e) as id, properties(e).name as name, properties(e).type as type, properties(e).description as description, properties(e).ref as ref, properties(e).created_at as created_at"
        r : ResultSet = self.do_exec(query)
        
        if not r.is_succeeded():
            logger.error(f"Failed to query entities, err = {r.error_msg() if r else 'Unknown error'}")
            return []
        
        # Parse result
        entities = []
        row_count = r.row_size()
        
        for i in range(row_count):
            val = r.row_values(i)
            entity = {
                'id': val[0],
                'name': val[1],
                'type': val[2],
                'description': val[3],
                'ref': val[4],
                'created_at': val[5]
            }
            entities.append(entity)
        
        logger.info(f"Successfully exported {len(entities)} entities")
        return entities

    def export_relations(self, space: str) -> List[Dict[str, Any]]:
        """
        Export relations (edges) from Nebula database.
        Args:
            space (str): The Nebula space to export from
            output_file (str, optional): Path to output CSV file. If None, returns data without writing to file.
        Returns:
            List[Dict[str, Any]]: List of relation data exported
        """
        # Use space
        r = self.do_exec(f"USE `{space}`")
        if not r.is_succeeded():
            logger.error(f"Failed to use space '{space}', err= {r.error_msg() if r else 'Unknown error'}")
            return []

        # Query all relations
        query = "MATCH (e1:entity)-[r:relation]->(e2:entity) RETURN id(e1) as source_id, id(e2) as target_id, properties(r).keywords as keywords, properties(r).description as description, properties(r).weight as weight, properties(r).ref as ref"
        r = self.do_exec(query)
        
        if not r.is_succeeded():
            logger.error(f"Failed to query relations, err = {r.error_msg() if r else 'Unknown error'}")
            return []
        
        # Parse result
        relations = []
        row_count = r.row_size()
        
        for i in range(row_count):
            val = r.row_values(i)
            relation = {
                'source_id': val[0],
                'target_id': val[1],
                'keywords': val[2],
                'description': val[3],
                'weight': val[4],
                'ref': val[5]
            }
            relations.append(relation)
        
        logger.info(f"Successfully exported {len(relations)} relations")

        return relations

def export_nebula_data(space: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Convenience function to export data from Nebula Graph to CSV files.
    
    Args:
        space (str): The Nebula space to export from
        entities_file (str, optional): Path to output CSV file for entities. If None, returns data without writing to file.
        relations_file (str, optional): Path to output CSV file for relations. If None, returns data without writing to file.
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary with 'entities' and 'relations' keys
    """
    exporter = NebulaExporter()
    try:
        entities = exporter.export_entities(space)
        relations = exporter.export_relations(space)
        return {
            'entities': entities,
            'relations': relations
        }
    finally:
        exporter.close()
