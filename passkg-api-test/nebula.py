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
