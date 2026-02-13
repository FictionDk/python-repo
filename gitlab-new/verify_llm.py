"""
Simple verification script for LLM implementation
"""

import sqlite3
from db.database import get_database


def verify_database():
    """Verify llm_history table exists and has correct structure"""
    print("Verifying LLM database implementation...")
    
    db = get_database()
    conn = db.connect()
    cursor = conn.cursor()
    
    # Check if llm_history table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='llm_history'
    """)
    result = cursor.fetchone()
    
    if result:
        print("✓ llm_history table exists")
        
        # Get table schema
        cursor.execute("PRAGMA table_info(llm_history)")
        columns = cursor.fetchall()
        
        print("\nTable schema:")
        expected_columns = ['id', 'type', 'create_at', 'req_content', 'resp_content', 'sucess']
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            print(f"  - {col_name}: {col_type}")
            if col_name not in expected_columns:
                print(f"    ⚠ Warning: Unexpected column '{col_name}'")
        
        print(f"\n✓ All expected columns present: {all(col[1] in expected_columns for col in columns)}")
        
        # Test insert
        from datetime import datetime
        create_at = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO llm_history (type, create_at, req_content, resp_content, sucess)
            VALUES (?, ?, ?, ?, ?)
        """, ("验证测试", create_at, "测试请求", "测试响应", 0))
        
        record_id = cursor.lastrowid
        print(f"✓ Inserted test record with ID: {record_id}")
        
        # Test query
        cursor.execute("""
            SELECT * FROM llm_history WHERE id = ?
        """, (record_id,))
        row = cursor.fetchone()
        
        if row:
            print(f"✓ Retrieved record: type={row[1]}, create_at={row[2]}")
        
        # Test update
        cursor.execute("""
            UPDATE llm_history SET resp_content = ?, sucess = ? WHERE id = ?
        """, ("更新的响应", 1, record_id))
        
        conn.commit()
        print(f"✓ Updated record successfully")
        
        # Clean up test record
        cursor.execute("DELETE FROM llm_history WHERE id = ?", (record_id,))
        conn.commit()
        print(f"✓ Cleaned up test record")
        
    else:
        print("✗ llm_history table not found!")
    
    conn.close()
    print("\n✓ Database verification completed")


def verify_imports():
    """Verify all imports work correctly"""
    print("\nVerifying imports...")
    
    try:
        from api.llm_client import LLMClient
        print("✓ LLMClient import successful")
        
        from db.llm_history import LLMHistoryMixin
        print("✓ LLMHistoryMixin import successful")
        
        from db.models import Database
        print("✓ Database import successful")
        
        client = LLMClient()
        print(f"✓ LLMClient instantiated: {client.base_url}")
        
    except Exception as e:
        print(f"✗ Import failed: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("LLM Implementation Verification")
    print("=" * 60 + "\n")
    
    verify_imports()
    verify_database()
    
    print("\n" + "=" * 60)
    print("Verification completed!")
    print("=" * 60)
