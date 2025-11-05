from neo_operator import import_neo4j_data
from utils import read_graph_from_csv


def import_csv_to_neo4j(workspace: str = "neo4j", node_file: str = 'neo_node.csv', edge_file: str = 'neo_edge.csv'):
    """
    Import data from CSV files into Neo4j.
    
    Args:
        workspace (str): The workspace to import into
        node_file (str): Path to the node CSV file
        edge_file (str): Path to the edge CSV file
    """
    # Read data from CSV files
    data = read_graph_from_csv(node_file, edge_file)
    # print(data["entities"][1])
    # print(data["relations"][1])

    # Import data into Neo4j
    import_neo4j_data(workspace, data)

# If this script is run directly, import the data
if __name__ == "__main__":
    import_csv_to_neo4j()
