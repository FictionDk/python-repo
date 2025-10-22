from typing import List, Dict, Any
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from nebula3.data.ResultSet import ResultSet
from nebula3.gclient.net import Session

import logging
import os

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class NebulaClient:
    def __init__(self):
        host = os.getenv('NEBULA_ADDRESS')
        port = int(os.getenv('NEBULA_PORT'))
        self.username = os.getenv('NEBULA_USERNAME')
        self.password = os.getenv('NEBULA_PASSWORD')
        self.config = Config()
        self.config.max_connection_pool_size = 10
        self.config.timeout = 3000000  # 30秒超时，避免查询结果过大时出现TimeoutError
        self.conn_pool = ConnectionPool()
        try:
            ok = self.conn_pool.init([(host, port)], self.config)
            if not ok:
                raise Exception("Failed to connect to Nebula Graph")
            print("✅ Successfully connected to Nebula Graph")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            exit(1)

        session = self.conn_pool.get_session(self.username, self.password)
        if not session:
            print("❌ Failed to create session")
            self.conn_pool.close()
            exit(1)

    def do_exec(self, sql, params: dict[str, Any] = None, space: str = None) -> ResultSet:
        """执行并返回结果"""
        try:
            session = self.conn_pool.get_session(self.username, self.password)
            if space:
                session.execute(f"USE `{space}`")
            if params is None:
                print(f"sql={sql}")
                return session.execute(sql)
            else:
                print(f"sql={sql}, p={params}")
                return session.execute_parameter(sql, params)
        except Exception as e:
            print(f"❌ Query execution error: {e}")
            return None

    def close(self):
        """关闭连接"""
        if self.conn_pool:
            self.conn_pool.close()

create_tag_entity = """
CREATE TAG IF NOT EXISTS entity(
    name string,
    type string,
    description string,
    ref string,
    created_at timestamp
);
"""
create_edge_relation = """
CREATE EDGE IF NOT EXISTS relation(
    keywords string,
    description string,
    weight double,
    ref string
);
"""



class NebulaImporter:
    """
    Handles importing data into Nebula graph database.
    Manages connection, schema creation, and data import operations.
    """
    
    def __init__(self):
        """
        Initialize Nebula connection using environment variables.
        """
        self.client = NebulaClient()

    def _exec(self, command: str, params: dict[str, Any] = None, space: str = None) -> ResultSet:
        return self.client.do_exec(command, params, space)

    def _init_space(self, space:str = 'defalut'):
        r = self._exec(f"DROP SPACE IF EXISTS `{space}`")
        if not r.is_succeeded():
            logger.error(f"Failed to drop space '{space}', err= {r.error_msg()}")

        create_space = f"CREATE SPACE IF NOT EXISTS {space} (partition_num=10, replica_factor=1, vid_type=fixed_string(32));"
        r = self._exec(create_space)
        if not r.is_succeeded():
            logger.error(f"Failed to create space {space}, err = {r.error_msg()}")
        
        #self._exec(f"USE `{space}`")

        r = self._exec(create_tag_entity, space=space)
        if not r.is_succeeded():
            logger.error(f"Failed to create node for {space}, err = {r.error_msg()}")

        r = self._exec(create_edge_relation, space=space)
        if not r.is_succeeded():
            logger.error(f"Failed to create relation for {space}, err = {r.error_msg()}")

    
    def _import_entities(self, space: str, entities: List[Dict[str, Any]]) -> int:
        """
        Import entities (nodes) into Nebula database.
        Args:
            space (str): The Nebula space to import into
            entities (List[Dict[str, Any]]): List of entity data to import
        Returns:
            int: Number of entities imported
        """
        if not entities:
            logger.info("No entities to import")
            return 0
        
        imported_count = 0

        #self._exec(f"USE `{space}`;")
        for entity in entities:
            insert_node_stmt = f'INSERT VERTEX entity(name, type, description, ref, created_at) VALUES "{entity['id']}": ($name, $type, $description, $ref, $created_at)'
            entity = {k: v for k, v in entity.items() if k != 'id'}
            r = self._exec(insert_node_stmt, entity, space=space)
            if r is not None and r.is_succeeded():
                imported_count += 1
            else:
                #logger.error(f"Failed to import entity {entity['id']}: {r.error_msg()}")
                exit(0)
        return imported_count

    
    def _import_relations(self, space: str, relations: List[Dict[str, Any]]) -> int:
        """
        Import relations (edges) into Nebula database.
        Args:
            space (str): The Nebula space to import into
            relations (List[Dict[str, Any]]): List of relation data to import
        Returns:
            int: Number of relations imported
        """
        if not relations:
            logger.info("No relations to import")
            return 0
        imported_count = 0
        self._exec(f"USE {space};")

        for rel in relations:
            insert_stmt = '''
            INSERT EDGE relation(keywords, description, weight, ref)
            VALUES $src -> $dst: ($keywords, $description, $weight, $ref)
            '''
            # Execute the statement
            result = self._exec(insert_stmt, rel)
            if result and result.is_succeeded():
                imported_count += 1
            else:
                logger.error(f"Failed to import relation {rel['source_id']}->{rel['target_id']}: {result.error_msg() if result else 'Unknown error'}")
        logger.info(f"Successfully imported {imported_count} relations")
        return imported_count


def grahp_import(space: str, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> tuple[int, int]:
    nebula_imp = NebulaImporter()
    nebula_imp._init_space(space)
    e_count = nebula_imp._import_entities(space, entities)
    r_clount = nebula_imp._import_relations(space, relations)
    #nebula_imp.client.close()
    return e_count, r_clount
