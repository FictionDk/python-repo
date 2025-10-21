import os
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
