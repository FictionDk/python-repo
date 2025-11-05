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

q_1 = 'MATCH (v:entity) WHERE id(v) == "-2230898713318503079" RETURN id(v) as id, properties(v).name as name, properties(v).type as type, properties(v).description as description, properties(v).ref as ref'

q_2 = '''
MATCH (v:entity) WHERE properties(v).name IN ["血小板配型方法","血小板","配型方法"] RETURN id(v) AS id, properties(v).name AS name, properties(v).type AS type, properties(v).ref AS ref
'''
q_e_count = 'MATCH (v) RETURN COUNT(v) AS vertex_count;'

q_r_count = 'MATCH ()-[e]->() RETURN COUNT(e) AS edge_count;'

q_3 = 'FETCH PROP ON entity -6150443974223083657 YIELD properties(vertex);'

drop_ngql = 'DROP SPACE `cowherd`'

show_entity = '''
MATCH (v:entity) RETURN id(v) as id, properties(v).name as name, properties(v).type as type, properties(v).description as description, properties(v).ref as ref
LIMIT 10
'''
show_relation = '''
MATCH (v:entity)-[e:relation]->(u:entity) RETURN id(v) as source_id, id(u) as target_id, properties(v).name as source_name, properties(u).name as target_name, properties(e).keywords as keywords, properties(e).description as description, properties(e).weight as weight, properties(e).ref as ref 
LIMIT 10
'''

add_host = 'ADD HOST "storaged0":9779;'

def test_find_duplicate_names(space_name):
    # 创建客户端实例
    client = NebulaClient()
    try:
        result = client.execute_query(f"USE `{space_name}`")
        if not result or not result.is_succeeded():
            print(f"❌ 无法切换到space {space_name}: {result.error_msg() if result else 'Unknown error'}")
            return {}

        result = client.execute_query("MATCH (v:entity) RETURN id(v) as id, properties(v).name as name")
        if not result or not result.is_succeeded():
            print(f"❌ 查询执行失败: {result.error_msg() if result else 'Unknown error'}")
            return {}

        # 处理查询结果，收集name到id的映射
        name_to_ids = {}
        # 超长节点名称收集
        extra_long_names = []
        
        # 获取id和name列的值
        id_values = result.column_values("id")
        name_values = result.column_values("name")
        
        # 遍历所有行
        for i in range(len(id_values)):
            node_id = id_values[i].cast()
            name_value = name_values[i]
            # 处理name值可能为null的情况
            name = name_value.cast() if not name_value.is_null() else 'None'
            if name not in name_to_ids:
                name_to_ids[name] = []
            list(name_to_ids[name]).append(node_id)
        
        # 筛选出重复的name（出现次数大于1）
        duplicates = {name: ids for name, ids in name_to_ids.items() if len(ids) > 1 and name is not None}
        # 筛选name长度超过12的name
        extra_long_names = [name for name, _ in name_to_ids.items() if len(name) > 18]
        if duplicates:
            print(f"✅ 总数：{len(id_values)}; 找到 {len(duplicates)} 个重复的name值:")
        else:
            print("✅ 未找到重复的name值")

        if len(extra_long_names) > 1:
            for name in extra_long_names:
                print(name)
        print("*"*40)
        print(f"总数：{len(id_values)};找到{len(extra_long_names)} 条超长name")
        # 打印详细信息
        # for name, ids in duplicates.items():
        #     print(f"  节点名: '{name}', 出现次数: {len(ids)}")
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
            #         print(f"    节点详情 (ID: {node_id}):\n{result}")
            #     else:
            #         print(f"    ❌ 无法获取节点 {node_id} 的详情: {result.error_msg() if result else 'Unknown error'}")

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
    finally:
        # 关闭连接
        client.close()

def test_query(space = None, nGQL_arr: list = None):
    client = NebulaClient()
    try:
        client.execute_query(f"USE `{space}`")
        for nGQL in nGQL_arr:
            r = client.execute_query(nGQL)
            print("*"*40)
            print(f"{r.is_succeeded()}/{r.error_msg()} 查询结果行数: {r.row_size()}")
            for i in range(r.row_size()):
                print(f"第 {i+1} 行: {r.row_values(i)}")
        print("*"*40)
        print("END")
    except Exception as e:
        print(f"测试异常: {e}")
    finally:
        client.close()

def exec(n_gql):
    """执行nGQL命令，捕获所有异常，失败不退出"""
    client = None
    try:
        client = NebulaClient()
        result = client.execute_query(n_gql)
        if result is not None and result.is_succeeded():
            print(f"✅ 执行成功: {n_gql}")
        else:
            error_msg = result.error_msg() if result else "Unknown error"
            print(f"❌ 执行失败: {error_msg}")
    except Exception as e:
        print(f"❌ 执行异常: {e}")
    finally:
        if client:
            client.close()

create_tag_entity = """
CREATE TAG IF NOT EXISTS entity(
    name string,
    type string,
    description string,
    ref string,
    created_at timestamp
);
"""
create_edge_relation = """
CREATE EDGE IF NOT EXISTS relation(
    keywords string,
    description string,
    weight double,
    ref string
);
"""
create_workspace = 'CREATE SPACE IF NOT EXISTS `cowherd` (vid_type=INT64, partition_num=10, replica_factor=1, charset = utf8, collate = utf8_bin)'

# 2kbebs
if __name__ == "__main__":
    #test_find_duplicate_names('cowherd')
    test_query('cowherd', [q_3])
    #exec(drop_ngql)
