from pathlib import Path
from test import test_post

def process_files_in_directory(directory_path):
    """
    Read all files from the specified directory and call test_post method for each file.
    
    Args:
        directory_path (str): Path to the directory containing files to process
    """
    # Convert to Path object for easier handling
    dir_path = Path(directory_path)
    
    # Check if directory exists
    if not dir_path.exists():
        print(f"Error: Directory {directory_path} does not exist.")
        return
    
    # Check if path is a directory
    if not dir_path.is_dir():
        print(f"Error: {directory_path} is not a directory.")
        return
    
    # Get all files in the directory (non-recursive)
    files = [f for f in dir_path.iterdir() if f.is_file()]
    
    if not files:
        print(f"No files found in directory: {directory_path}")
        return
    
    print(f"Found {len(files)} files in {directory_path}. Starting processing...")
    
    # Process each file
    for file_path in files:
        print(f"\nProcessing file: {file_path}")
        try:
            # Call test_post method with the file path
            test_post(pdf_file_path=str(file_path), direct_ocr='false')
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue
    
    print("\nProcessing completed.")

if __name__ == "__main__":
    # Specify the target directory
    target_directory = r"D:\Doc\2025年四季度\file"
    
    # Process all files in the directory
    process_files_in_directory(target_directory)
