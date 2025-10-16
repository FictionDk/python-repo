"""
测试 NebulaClient 的 find_duplicate_names 方法
"""

from nebula import NebulaClient

def test_find_duplicate_names():
    # 创建客户端实例
    client = NebulaClient()
    
    try:
        # 指定要查询的space名称
        space_name = "2kbebs"

        # 调用方法查找重复的name
        duplicates = client.find_duplicate_names(space_name)        
        # 打印详细信息
        for name, ids in duplicates.items():
            print(f"  节点名: '{name}', 出现次数: {len(ids)}")
            for node_id in ids:
                # 根据节点ID查询节点详情
                detail_query = f'''
                FETCH PROP ON entity {node_id}
                YIELD 
                properties(vertex).name AS name,
                properties(vertex).type AS type,
                properties(vertex).description AS description,
                properties(vertex).ref AS ref;
                '''
                result = client.execute_query(detail_query)
                if result is not None and result.is_succeeded():
                    # 直接打印ResultSet，它会包含所有属性
                    print(f"    节点详情 (ID: {node_id}):\n{result}")
                else:
                    print(f"    ❌ 无法获取节点 {node_id} 的详情: {result.error_msg() if result else 'Unknown error'}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
    finally:
        # 关闭连接
        client.close()

if __name__ == "__main__":
    test_find_duplicate_names()
