"""
Test script for LLM management functionality
"""

from db.database import init_database
from api.llm_client import LLMClient


def test_llm_database():
    """Test LLM database table creation and operations"""
    print("Testing LLM database operations...")
    
    # Initialize database
    db = init_database()
    
    # Test inserting a record
    from datetime import datetime
    create_at = datetime.now().isoformat()
    
    record_id = db.insert_llm_history(
        type="测试",
        create_at=create_at,
        req_content="这是一个测试请求"
    )
    
    print(f"✓ Inserted record with ID: {record_id}")
    
    # Test updating response
    success = db.update_response(
        record_id=record_id,
        resp_content="这是一个测试响应",
        success=True
    )
    
    print(f"✓ Updated response: {success}")
    
    # Test querying records
    records = db.get_llm_history(limit=5)
    print(f"✓ Retrieved {len(records)} records")
    
    # Display the test record
    if records:
        import sqlite3
        for row in records:
            print(f"  - ID: {row['id']}, Type: {row['type']}, Success: {row['sucess']}")
    
    db.close()
    print("✓ Database test completed\n")


def test_llm_client():
    """Test LLM client initialization"""
    print("Testing LLM client...")
    
    try:
        # Initialize client
        client = LLMClient()
        print(f"✓ LLM Client initialized")
        print(f"  - Base URL: {client.base_url}")
        print(f"  - Model: {client.model}")
        
        # Health check
        is_healthy = client.health_check()
        print(f"✓ Health check: {'Healthy' if is_healthy else 'Unhealthy (service may not be running)'}")
        
        print("✓ Client test completed\n")
        
    except Exception as e:
        print(f"✗ Client test failed: {e}\n")


def test_full_workflow():
    """Test full workflow with database and client"""
    print("Testing full LLM workflow...")
    
    from datetime import datetime
    
    # Initialize database
    db = init_database()
    
    # Initialize client
    client = LLMClient()
    
    # Test generate_response (will fail if LLM service is not running, but that's ok)
    create_at = datetime.now().isoformat()
    
    print("Attempting to get LLM response (may fail if service not running)...")
    response, success = client.generate_response(
        type="测试汇总",
        req_content="请生成一个测试摘要",
        create_at=create_at,
        db_instance=db
    )
    
    print(f"✓ Response generated: Success={success}")
    print(f"  Response: {response[:100]}..." if len(response) > 100 else f"  Response: {response}")
    
    # Verify record was saved
    records = db.get_llm_history(type_filter="测试汇总", limit=1)
    if records:
        print(f"✓ Record saved in database with ID: {records[0]['id']}")
    
    db.close()
    print("✓ Full workflow test completed\n")


if __name__ == "__main__":
    print("=" * 60)
    print("LLM Management Test Suite")
    print("=" * 60 + "\n")
    
    # Run tests
    test_llm_database()
    test_llm_client()
    test_full_workflow()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
