"""
测试 NebulaClient 的 find_duplicate_names 方法
"""

from nebula import NebulaClient

n_gql_0 = '''
MATCH (v:entity) WHERE properties(v).name IN ['血供科', '输血科'] 
RETURN id(v) AS id,properties(v).name AS name,
    properties(v).type AS type,
    properties(v).ref AS ref
'''

n_gql_1 = '''
MATCH (v:entity)-[e:relation*0..2]-(u:entity) 
WHERE v.name IN ['血供科'] 
WITH v, u, e, [ee IN e | 'ref:' + coalesce(properties(ee).ref, 'unknown')] AS edge_refs,
[ee IN e | properties(ee).description] AS descriptions 
UNWIND edge_refs AS ref_item UNWIND descriptions AS desc_item 
RETURN collect(DISTINCT ref_item) AS refs,collect(DISTINCT desc_item) AS descriptions
'''

n_gql_2 = '''
MATCH (v:entity)-[e:relation*0..2]-(u:entity)
WHERE properties(v).name IN ['血供科']
RETURN DISTINCT
  id(u) AS vertex_id,
  properties(u).name AS name,
  properties(u).type AS type
'''

n_gql_3 = '''
MATCH (v:entity)-[e:relation *0..1]-(u:entity) 
WHERE properties(v).name IN ['血供科'] 
WITH REDUCE(refs = ['ref:' + properties(u).ref, 'ref:'+properties(v).ref], ee IN e | refs + ('ref:' + ee.ref) + ee.description) AS all_refs 
unwind all_refs as refs RETURN collect(DISTINCT refs) as refs
'''

n_gql_4 = '''
MATCH (start:entity {name: '血供科'})-[e:relation*1..2]-(u:entity)
WITH u, size(e) AS hop, 
     coalesce(CASE WHEN size(e) > 0 THEN properties(e[-1]).weight END, 0.0) AS weight
RETURN DISTINCT
  id(u) AS vertex_id,
  properties(u).name AS name,
  properties(u).type AS type,
  properties(u).ref AS ref,
  hop AS hop_count,
  weight
ORDER BY hop_count, name

'''

n_gql_5 = '''
UNWIND ['血供科'] AS start_name
MATCH (start:entity {name: start_name})-[e:relation*0..2]-(u:entity)
WITH 
  u,
  start.name AS source_name,
  size(e) AS hop_count,
  CASE 
    WHEN size(e) > 0 THEN properties(e[-1]).weight 
    ELSE 0.0 
  END AS last_edge_weight
ORDER BY u.name, hop_count
WITH 
  u,
  source_name,
  hop_count,
  coalesce(last_edge_weight, 0.0) AS weight
WHERE hop_count == min(hop_count) OVER (PARTITION BY id(u))
RETURN DISTINCT
  id(u) AS vertex_id,
  properties(u).name AS name,
  properties(u).type AS type,
  collect({source: source_name, hop: hop_count, weight: weight}) AS sources
ORDER BY hop_count, name
'''

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
            # for node_id in ids:
            #     # 根据节点ID查询节点详情
            #     detail_query = f'''
            #     FETCH PROP ON entity {node_id}
            #     YIELD 
            #     properties(vertex).name AS name,
            #     properties(vertex).type AS type,
            #     properties(vertex).description AS description,
            #     properties(vertex).ref AS ref;
            #     '''
            #     result = client.execute_query(detail_query)
            #     if result is not None and result.is_succeeded():
            #         # 直接打印ResultSet，它会包含所有属性
            #         print(f"    节点详情 (ID: {node_id}):\n{result}")
            #     else:
            #         print(f"    ❌ 无法获取节点 {node_id} 的详情: {result.error_msg() if result else 'Unknown error'}")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
    finally:
        # 关闭连接
        client.close()

def test_query(space, nGQL_arr: list):
    client = NebulaClient()
    try:
        client.execute_query(f"USE `{space}`")
        for nGQL in nGQL_arr:
            r = client.execute_query(nGQL)
            print("*"*40)
            print(f"查询结果行数: {r.row_size()}")
            for i in range(r.row_size()):
                print(f"第 {i+1} 行: {r.row_values(i)}")
        print("*"*40)
        print("END")
    except Exception as e:
        print(f"测试异常: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    test_find_duplicate_names()
    #test_query('2kbebs', [n_gql_0, n_gql_4])
