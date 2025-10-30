import os
import csv
from typing import List, Dict, Any

def extract_filename_from_path(file_path: str) -> str:
    """
    Extract filename from file path, splitting on '.' and taking the first part.
    
    Args:
        file_path (str): The full file path
        
    Returns:
        str: First part of filename after splitting on '.'
    """
    if not file_path:
        return ""
    
    # Get the base filename
    filename = os.path.basename(file_path)
    
    # Remove extension (everything after the last dot)
    name_without_ext = os.path.splitext(filename)[0]
    
    # Split on '.' and return the first part
    return name_without_ext.split('.')[0]

def _process_source_id(source_id: str, chunk_to_full_doc_mapping: Dict[str, str]) -> str:
    """
    Process source_id by splitting on <SEP>, mapping chunk IDs to full document IDs,
    and joining with commas. Removes leading comma and prints warning if result is empty.
    
    Args:
        source_id (str): The source_id string containing chunk IDs separated by <SEP>
        chunk_to_full_doc_mapping (Dict[str, str]): Mapping from chunk IDs to full document IDs
        
    Returns:
        str: Processed ref string with full document IDs joined by commas
    """
    if not source_id:
        print("Warning: source_id is empty or None")
        return ""
        
    full_doc_ids = []
    # Split source_id by <SEP> to get chunk IDs
    chunk_ids = source_id.split('<SEP>')
    # Map each chunk ID to its full document ID
    for chunk_id in chunk_ids:
        chunk_id = chunk_id.strip()  # Remove any whitespace
        if chunk_id in chunk_to_full_doc_mapping:
            full_doc_ids.append(chunk_to_full_doc_mapping[chunk_id])
    
    # Join full document IDs with commas
    ref = ','.join(full_doc_ids) if full_doc_ids else ''
    
    # Remove leading comma if present
    if ref.startswith(','):
        ref = ref[1:]
    
    # Print warning if ref is empty
    if not ref:
        print(f"Warning: Processed ref is empty for source_id: {source_id}")
    
    return ref

def schema_mapper(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Map Neo4j graph data to Nebula graph schema format.
    
    Args:
        data (Dict): Graph data with 'nodes' and 'relationships' keys
        
    Returns:
        Dict: Mapped data with 'entities' (TAGs) and 'relations' (EDGEs) in Nebula format
    """
    entities = []
    relations = []
    
    # Read chunk to full document mapping
    chunk_to_full_doc_mapping = read_id_mapping_from_csv('chunk_to_full_doc_mapping.csv')
    
    # Map nodes to Nebula TAG entities
    for node in data.get('nodes', []):
        # Extract properties from the node
        props : dict = node['properties']
        
        # Process source_id to get full document references
        source_id = props.get('source_id', '')
        ref = _process_source_id(source_id, chunk_to_full_doc_mapping)
        
        # Create entity with Nebula schema properties
        entity = {
            'id': node['id'],
            'name': props.get('entity_id', ''),
            'type': props.get('entity_type', ''),
            'description': props.get('description', ''),
            'ref': ref,
            'created_at': props.get('created_at', 0)
        }
        entities.append(entity)
        props.clear()

    # Map relationships to Nebula EDGE relations
    for rel in data.get('relationships', []):
        # Extract properties from the relationship
        props = rel['properties']
        
        # Process source_id to get full document references
        source_id = props.get('source_id', '')
        ref = _process_source_id(source_id, chunk_to_full_doc_mapping)
        
        # Create relation with Nebula schema properties
        relation = {
            'source_id': rel['start_id'],
            'target_id': rel['end_id'],
            'keywords': props.get('keywords', ''),
            'description': props.get('description', ''),
            'weight': props.get('weight', 0.0),
            'ref': ref
        }
        relations.append(relation)
    
    return {
        'entities': entities,
        'relations': relations
    }

def save_graph_to_csv(data: Dict[str, List[Dict[str, Any]]], nodes_file: str = 'nodes.csv', edges_file: str = 'edges.csv'):
    """
    Save graph data to CSV files.
    
    Args:
        data (Dict): Graph data with 'entities' and 'relations' keys
        nodes_file (str): Output file for nodes/entities
        edges_file (str): Output file for edges/relations
    """
    # Save entities (nodes) to CSV
    if 'entities' in data and data['entities']:
        with open(nodes_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'type', 'description', 'ref', 'created_at'])
            writer.writeheader()
            writer.writerows(data['entities'])
    
    # Save relations (edges) to CSV
    if 'relations' in data and data['relations']:
        with open(edges_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['source_id', 'target_id', 'keywords', 'description', 'weight', 'ref'])
            writer.writeheader()
            writer.writerows(data['relations'])

def read_graph_from_csv(nodes_file: str = 'nodes.csv', edges_file: str = 'edges.csv') -> Dict[str, List[Dict[str, Any]]]:
    """
    Read graph data from CSV files and convert to JSON objects.
    
    Args:
        nodes_file (str): Input file for nodes/entities
        edges_file (str): Input file for edges/relations
        
    Returns:
        Dict: Graph data with 'entities' and 'relations' keys
    """
    data = {'entities': [], 'relations': []}
    
    # Read entities (nodes) from CSV
    try:
        with open(nodes_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data['entities'] = [row for row in reader]
    except FileNotFoundError:
        print(f"Nodes file {nodes_file} not found. Continuing with empty nodes list.")
    except Exception as e:
        print(f"Error reading nodes file {nodes_file}: {str(e)}")
    
    # Read relations (edges) from CSV
    try:
        with open(edges_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data['relations'] = [row for row in reader]
    except FileNotFoundError:
        print(f"Edges file {edges_file} not found. Continuing with empty edges list.")
    except Exception as e:
        print(f"Error reading edges file {edges_file}: {str(e)}")
    
    return data

def map_lightrag_to_documents(doc_full_data: Dict[str, Any], 
                            doc_chunks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Map lightrag_doc_full data to documents table schema.
    
    Args:
        doc_full_data (Dict): Data from lightrag_doc_full table
        doc_chunks_data (List): List of chunks data for this document
        
    Returns:
        Dict: Mapped data for documents table
    """
    # Extract name from file_path if doc_name is null
    doc_name = doc_full_data.get('doc_name')
    if not doc_name and doc_chunks_data:
        # Use the file_path from the first chunk
        file_path = doc_chunks_data[0].get('file_path', '')
        doc_name = extract_filename_from_path(file_path)
    # (id, content, extraction_prompt, workspace_id, created_at, chunks, 
    # parent, is_project_doc, last_mod, process_status, name, type, summary, tags)
    mapped_data = {
        'id': doc_full_data['id'],
        'content': doc_full_data['content'],
        'workspace_id': doc_full_data['workspace'],
        'name': doc_name,
        'created_at': doc_full_data.get('create_time'),
        'last_mod': doc_full_data.get('update_time'),
        'process_status': 'completed',
        'is_project_doc': False,
        'chunks': len(doc_chunks_data) if doc_chunks_data else 0,
        'type': 'D',
        'summary': None,
        'tags': None,
        'extraction_prompt': '',
        'parent': ''
    }
    
    return mapped_data

def map_lightrag_chunks_to_document_chunks(chunk_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map lightrag_doc_chunks data to document_chunks table schema.
    
    Args:
        chunk_data (Dict): Data from lightrag_doc_chunks table
        
    Returns:
        Dict: Mapped data for document_chunks table
    """
    mapped_data = {
        'document_id': chunk_data['full_doc_id'],
        'chunk_index': str(chunk_data['chunk_order_index']) if chunk_data['chunk_order_index'] is not None else '0',
        'text': chunk_data['content'],
        'embedding': chunk_data.get('content_vector')
    }
    
    return mapped_data

def save_id_mapping_to_csv(mapping: Dict[str, str], filepath: str) -> None:
    """
    Save chunk id to full document id mapping to a CSV file.
    
    Args:
        mapping (Dict[str, str]): Dictionary mapping chunk id to full document id
        filepath (str): Path to the output CSV file
    """
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['chunk_id', 'full_doc_id'])
        writer.writeheader()
        for chunk_id, full_doc_id in mapping.items():
            writer.writerow({'chunk_id': chunk_id, 'full_doc_id': full_doc_id})

def read_id_mapping_from_csv(filepath: str) -> Dict[str, str]:
    """
    Read chunk id to full document id mapping from a CSV file.
    
    Args:
        filepath (str): Path to the input CSV file
        
    Returns:
        Dict[str, str]: Dictionary mapping chunk id to full document id
    """
    mapping = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mapping[row['chunk_id']] = row['full_doc_id']
    except FileNotFoundError:
        print(f"Mapping file {filepath} not found. Returning empty mapping.")
    except Exception as e:
        print(f"Error reading mapping file {filepath}: {str(e)}")
    
    return mapping


def save_to_csv(data: List[Dict[str, Any]], headers: List[str], filepath: str) -> None:
    """
    Save data to a CSV file with specified headers.
    
    Args:
        data (List[Dict[str, Any]]): List of dictionaries containing the data to save
        headers (List[str]): List of column headers for the CSV file
        filepath (str): Path to the output CSV file
    """
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        print(f"Successfully saved {len(data)} records to {filepath}")
    except Exception as e:
        print(f"Error saving data to {filepath}: {str(e)}")
