from import_data import import_chunk_pg_data, import_graph_data

if __name__ == "__main__":
    try:    
        import_chunk_pg_data()
        import_graph_data()
        print("\nPress Enter or Ctrl+C to exit...")
        input()
    except Exception as e:
        print(f"ex: {e}")
        input()
