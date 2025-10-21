# pip install nebula3-python

from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from nebula3.data.ResultSet import ResultSet

host="192.168.120.246"
port=32586

class NebulaClient:
    def __init__(self, address=(host, port), username='root', password='nebula'):
        self.config = Config()
        self.config.max_connection_pool_size = 10
        self.config.timeout = 3000000  # 30秒超时，避免查询结果过大时出现TimeoutError
        self.conn_pool = ConnectionPool()

        # 初始化连接池
        try:
            ok = self.conn_pool.init([address], self.config)
            if not ok:
                raise Exception("Failed to connect to Nebula Graph")
            print("✅ Successfully connected to Nebula Graph")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            exit(1)

        # 获取会话
        self.session = self.conn_pool.get_session(username, password)
        if not self.session:
            print("❌ Failed to create session")
            self.conn_pool.close()
            exit(1)

    def execute_query(self, query) -> ResultSet:
        """执行查询并返回结果"""
        try:
            return self.session.execute(query)
        except Exception as e:
            print(f"❌ Query execution error: {e}")
            return None

    def close(self):
        """关闭连接"""
        if self.conn_pool:
            self.conn_pool.close()

    def find_duplicate_names(self, space_name):
        """
        在指定空间中查询所有节点的name属性，找出重复的name值。
        
        Args:
            space_name (str): 图空间名称
            
        Returns:
            dict: 包含重复name值及其对应节点ID列表的字典，格式如 {'name1': [id1, id2], 'name2': [id3, id4]}
        """
        # 切换到指定space
        space_query = f"USE `{space_name}`"
        result = self.execute_query(space_query)
        if not result or not result.is_succeeded():
            print(f"❌ 无法切换到space {space_name}: {result.error_msg() if result else 'Unknown error'}")
            return {}
        
        # 查询所有entity节点的id和name属性
        query = "MATCH (v:entity) RETURN id(v) as id, properties(v).name as name"
        result = self.execute_query(query)
        if not result or not result.is_succeeded():
            print(f"❌ 查询执行失败: {result.error_msg() if result else 'Unknown error'}")
            return {}
        
        # 处理查询结果，收集name到id的映射
        name_to_ids = {}
        
        # 获取id和name列的值
        id_values = result.column_values("id")
        name_values = result.column_values("name")
        
        # 遍历所有行
        for i in range(len(id_values)):
            node_id = id_values[i].cast()
            name_value = name_values[i]
            # 处理name值可能为null的情况
            name = name_value.cast() if not name_value.is_null() else None
            
            if name not in name_to_ids:
                name_to_ids[name] = []
            name_to_ids[name].append(node_id)
        
        # 筛选出重复的name（出现次数大于1）
        duplicates = {name: ids for name, ids in name_to_ids.items() if len(ids) > 1 and name is not None}
        
        if duplicates:
            print(f"✅ 总数：{len(id_values)}; 找到 {len(duplicates)} 个重复的name值:")
            # for name, ids in duplicates.items():
            #     print(f"  '{name}': {ids}")
        else:
            print("✅ 未找到重复的name值")
            
        return duplicates

def main():
    # 创建客户端实例
    client = NebulaClient()

    print("🎮 Welcome to Nebula Graph Query Console!")
    print("Type 'exit' to quit.")

    while True:
        try:
            # 获取用户输入
            query = input("\n🔍 Enter your query: ").strip()

            # 退出条件
            if query.lower() == 'exit':
                print("👋 Goodbye!")
                break

            # 跳过空查询
            if not query:
                continue

            # 执行查询
            result = client.execute_query(query)
            if result is None:
                continue
            if result.is_succeeded:
                print(f"\n📊 Query Result:\n{result}")
            else:
                print(f"{result.error_msg()}")

        except KeyboardInterrupt:
            print("\n👋 Exiting due to keyboard interrupt.")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")

    # 关闭连接
    client.close()

if __name__ == "__main__":
    main()
