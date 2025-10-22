from neo4j import GraphDatabase
from typing import Dict, List, Any
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class Neo4jExporter:
    """
    Handles exporting data from Neo4j graph database.
    """
    
    def __init__(self):
        """
        Initialize Neo4j connection using environment variables.
        """
        self.uri = os.getenv('NEO4J_URI')
        self.username = os.getenv('NEO4J_USERNAME')
        self.password = os.getenv('NEO4J_PASSWORD')
        
        if not all([self.uri, self.username, self.password]):
            raise ValueError("Neo4j connection parameters not found in environment variables")
            
        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
    
    def close(self):
        """
        Close the Neo4j driver connection.
        """
        if self.driver:
            self.driver.close()
    
    def show_space(self):
        """
        Display information about the 'neo4j' database/space only.
        """
        with self.driver.session() as session:
            # Query for all databases
            result = session.run("SHOW DATABASES;")
            records = list(result)

            if not records:
                print("No databases found.")
                return
                
            # Find and display only the 'neo4j' database
            neo4j_record = None
            for record in records:
                if record.get('name') == 'neo4j':
                    neo4j_record = record
                    break
            
            if neo4j_record is None:
                print("Database 'neo4j' not found.")
                return
                
            # Get field names and print header
            field_names = records[0].keys()
            header = "  ".join(f"{field.upper():<15}" for field in field_names)
            print(header)
            print("-" * len(header))
            
            # Print only the neo4j record
            row_parts = []
            for field in field_names:
                value = neo4j_record.get(field, 'N/A')
                # Convert list/dict/None to string
                if value is None:
                    value_str = "N/A"
                elif isinstance(value, (list, dict)):
                    value_str = str(value)
                else:
                    value_str = str(value)
                # Format with fixed width
                row_parts.append(f"{value_str:<15}")
            row = "  ".join(row_parts)
            print(row)

    def get_schema(self) -> Dict[str, Any]:
        """
        Query and return the graph schema including node labels, relationship types, 
        and their properties.
        
        Returns:
            Dict[str, Any]: Schema information with labels and relationship types
        """
        schema = {
            'labels': [],
            'relationship_types': []
        }
        
        try:
            with self.driver.session() as session:
                # Get all node labels and their properties
                labels_result = session.run("""
                    CALL db.schema.nodeTypeProperties()
                    YIELD nodeLabels, propertyName, propertyTypes
                    RETURN nodeLabels, propertyName, propertyTypes
                """)
                
                labels_dict = {}
                for record in labels_result:
                    labels = record["nodeLabels"]
                    prop_name = record["propertyName"]
                    prop_types = record["propertyTypes"]
                    
                    # Convert list of labels to a single label string (assuming single label)
                    label = labels[0] if labels else "Unknown"
                    
                    if label not in labels_dict:
                        labels_dict[label] = {
                            'label': label,
                            'properties': []
                        }
                    
                    labels_dict[label]['properties'].append({
                        'name': prop_name,
                        'types': prop_types
                    })
                
                schema['labels'] = list(labels_dict.values())
                
                # Get all relationship types and their properties
                rels_result = session.run("""
                    CALL db.schema.relTypeProperties()
                    YIELD relType, propertyName, propertyTypes
                    RETURN relType, propertyName, propertyTypes
                """)
                
                rels_dict = {}
                for record in rels_result:
                    rel_type = record["relType"]
                    prop_name = record["propertyName"]
                    prop_types = record["propertyTypes"]
                    
                    if rel_type not in rels_dict:
                        rels_dict[rel_type] = {
                            'type': rel_type,
                            'properties': []
                        }
                    
                    rels_dict[rel_type]['properties'].append({
                        'name': prop_name,
                        'types': prop_types
                    })
                
                schema['relationship_types'] = list(rels_dict.values())
                
                return schema
                
        except Exception as e:
            logger.error(f"Error retrieving schema: {str(e)}")
            raise
    
    def print_schema(self):
        """
        Print the graph schema in a readable format for the 'neo4j' space only.
        """
        try:
            schema = self.get_schema()
            print("=== Neo4j Graph Schema ===")
            
            print("\nNode Labels:")
            for label_info in schema['labels']:
                print(f"  Label: {label_info['label']}")
                print("    Properties:")
                for prop in label_info['properties']:
                    print(f"      {prop['name']}: {prop['types']}")
            
            print("\nRelationship Types:")
            for rel_info in schema['relationship_types']:
                print(f"  Type: {rel_info['type']}")
                print("    Properties:")
                for prop in rel_info['properties']:
                    print(f"      {prop['name']}: {prop['types']}")
                    
        except Exception as e:
            logger.error(f"Error printing schema: {str(e)}")
            raise
    
    def export_graph(self, workspace: str = "neo4j") -> Dict[str, List[Dict[str, Any]]]:
        """
        Export all nodes and relationships from the specified workspace.
        
        Args:
            workspace (str, optional): The workspace to filter by. Defaults to "neo4j".
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary with 'nodes' and 'relationships' keys
        """
        try:
            with self.driver.session() as session:
                # Base MATCH clause
                match_clause = "MATCH (n)"
                where_clause = ""
                params = {}
                
                # Add workspace filter if specified
                if workspace:
                    where_clause = "WHERE n.workspace = $workspace"
                    params['workspace'] = workspace
                
                # Query for nodes
                nodes_query = f"""
                    {match_clause}
                    {where_clause}
                    OPTIONAL MATCH (n)-[r]->(m)
                    WITH n, count(r) as out_degree
                    OPTIONAL MATCH (n)<-[r2]-(m2)
                    WITH n, out_degree, count(r2) as in_degree
                    RETURN 
                        id(n) as id,
                        labels(n) as labels,
                        properties(n) as properties,
                        out_degree,
                        in_degree
                """
                
                nodes_result = session.run(nodes_query, **params)
                nodes = []
                
                for record in nodes_result:
                    node = {
                        'id': record['id'],
                        'labels': record['labels'],
                        'properties': dict(record['properties']),
                        'out_degree': record['out_degree'],
                        'in_degree': record['in_degree']
                    }
                    nodes.append(node)
                
                # Query for relationships
                rels_query = f"""
                    MATCH (n)-[r]->(m)
                    {where_clause.replace('n.', '') if where_clause else ''}
                    RETURN
                        id(r) as id,
                        type(r) as type,
                        id(startNode(r)) as start_id,
                        id(endNode(r)) as end_id,
                        properties(r) as properties,
                        labels(startNode(r)) as start_labels,
                        labels(endNode(r)) as end_labels
                """
                
                rels_result = session.run(rels_query, **params)
                relationships = []
                
                for record in rels_result:
                    rel = {
                        'id': record['id'],
                        'type': record['type'],
                        'start_id': record['start_id'],
                        'end_id': record['end_id'],
                        'properties': dict(record['properties']),
                        'start_labels': record['start_labels'],
                        'end_labels': record['end_labels']
                    }
                    relationships.append(rel)
                
                return {
                    'nodes': nodes,
                    'relationships': relationships
                }
                
        except Exception as e:
            logger.error(f"Error exporting graph: {str(e)}")
            raise

def export_neo4j_data(workspace: str = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Convenience function to export data from Neo4j.
    
    Args:
        workspace (str, optional): The workspace to filter by. If None, export all data.
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary with 'nodes' and 'relationships' keys
    """
    exporter = Neo4jExporter()
    try:
        return exporter.export_graph(workspace)
    finally:
        exporter.close()

def print_neo4j_schema():
    """
    Convenience function to print the Neo4j graph schema.
    """
    exporter = Neo4jExporter()
    try:
        exporter.show_space()
        exporter.print_schema()
    finally:
        exporter.close()
