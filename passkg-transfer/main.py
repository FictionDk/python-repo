from utils import read_graph_from_csv
from kg_import import post
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('passkg_transfer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def _import_graph_data(workspace_id):
    data = read_graph_from_csv()
    print(data['entities'][0])
    print(data['relations'][0])
    success = post(workspace_id, data=data, base_url="http://192.168.98.11:8080")
    if success:
        logger.info("Graph data successfully pushed to remote API.")
    else:
        logger.error("Failed to push graph data to remote API.")
        raise Exception("Graph data import via API failed.")

def migrate_graph_data():
    _import_graph_data('cowherd')

def main():
    migrate_graph_data()

if __name__ == "__main__":
    try:    
        main()
        print("\nPress Enter or Ctrl+C to exit...")
        input()
    except KeyboardInterrupt:
        pass
    except Exception:
        print("")
