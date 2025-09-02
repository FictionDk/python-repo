import asyncio
import threading
import queue
import sys
import logging
from typing import Optional
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from mcp.types import CallToolRequest

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SseSessionManager:
    """
    管理SSE会话的类，使用独立线程和线程安全操作。
    
    该类提供了一个线程安全的接口来管理SSE连接，允许主线程继续执行，
    同时SSE会话在后台线程中运行。它处理连接生命周期、事件处理和
    跨线程边界的工具执行。
    
    属性:
        url (str): 要连接的SSE端点URL
        loop (Optional[asyncio.AbstractEventLoop]): 在工作线程中运行的asyncio事件循环
        session (Optional[ClientSession]): 活动的MCP客户端会话
        thread (Optional[threading.Thread]): 运行事件循环的工作线程
        result_queue (queue.Queue): 线程安全队列，用于从工作线程向主线程传递事件
        stop_event (threading.Event): 用于通知工作线程停止的事件
    """
    
    def __init__(self, url: str):
        """
        使用SSE端点URL初始化SseSessionManager。
        
        参数:
            url (str): SSE端点的URL（例如："http://localhost:8080/mcp/sse"）
        """
        self.url = url
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.session: Optional[ClientSession] = None
        self.thread: Optional[threading.Thread] = None
        self.result_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.logger = logging.getLogger(f"{__name__}.SseSessionManager")
        
    def start(self) -> None:
        """
        启动会话管理线程。
        
        此方法创建并启动一个守护线程，该线程将运行asyncio事件循环并管理SSE会话。
        线程被设置为守护线程，因此当主程序退出时它会自动终止。
        """
        self.logger.info(f"Starting session management thread for {self.url}")
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
        self.logger.info("Session management thread started")
        
    def _run_event_loop(self) -> None:
        """
        在独立线程中运行asyncio事件循环。
        
        此私有方法在工作线程中设置并运行asyncio事件循环。
        它确保SSE会话的所有异步操作都在单个线程中发生，这是asyncio所要求的。
        在finally块中始终关闭循环，以防止资源泄漏。
        """
        self.logger.info("Creating new event loop in worker thread")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.logger.info("Running session management coroutine")
            self.loop.run_until_complete(self._manage_session())
            self.logger.info("Session management coroutine completed")
        except Exception as e:
            self.logger.error(f"Error in session management: {str(e)}", exc_info=True)
            self.result_queue.put(('error', str(e)))
        finally:
            self.logger.info("Closing event loop")
            self.loop.close()

    async def _manage_session(self) -> None:
        """
        管理完整的SSE会话生命周期。
        
        此协程处理整个会话过程：
        1. 连接到SSE端点
        2. 初始化MCP客户端会话
        3. 发现可用工具
        4. 维持连接直到停止
        
        该方法使用异步上下文管理器来确保正确清理资源，即使发生错误。
        所有重要事件都放入结果队列，供主线程处理。
        """
        self.logger.info(f"Starting session management for {self.url}")
        
        try:
            # 使用mcp客户端的sse_client连接到SSE端点
            self.logger.info(f"Connecting to SSE endpoint: {self.url}")
            async with sse_client(self.url) as streams:
                self.logger.info("Successfully connected to SSE endpoint")
                
                # 使用接收到的流创建ClientSession
                async with ClientSession(*streams) as session:
                    self.session = session
                    self.logger.info("ClientSession created")
                    
                    # 初始化与服务器的会话
                    self.logger.info("Initializing session with server")
                    result = await session.initialize()
                    self.logger.info(f"Session initialized successfully. Server: {result.serverInfo.name}")
                    
                    # 发送连接事件到主线程
                    self.result_queue.put(('connected', result.serverInfo.name))
                    
                    # 发现服务器上可用的工具
                    self.logger.info("Discovering available tools")
                    tools = await session.list_tools()
                    tool_names = [tool.name for tool in tools.tools]
                    self.logger.info(f"Discovered {len(tool_names)} tools: {tool_names}")
                    
                    # 发送工具列表事件到主线程
                    self.result_queue.put(('tools', tool_names))
                    
                    # 保持会话活动直到被告知停止
                    # 此循环每秒运行一次以检查停止条件
                    self.logger.info("Session established and running")
                    while not self.stop_event.is_set():
                        await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"Error in session management: {str(e)}", exc_info=True)
            # 如果发生任何错误，将其发送到主线程进行处理
            self.result_queue.put(('error', str(e)))
        finally:
            self.logger.info("Cleaning up session resources")
            self.session = None
            
    def get_result(self, timeout: float = 1.0) -> Optional[tuple]:
        """
        从会话线程获取下一个结果。
        
        此方法以线程安全的方式从工作线程检索事件。
        它被主线程用来接收连接状态、工具列表和错误。
        
        参数:
            timeout (float): 等待结果的最大时间（秒）
            
        返回:
            Optional[tuple]: 如果可用则返回(event_type, data)元组，超时则返回None
            
        事件类型:
            - 'connected': 服务器连接已建立（数据：服务器名称）
            - 'tools': 发现的可用工具列表（数据：工具名称列表）
            - 'error': 工作线程中发生错误（数据：错误消息）
        """
        try:
            result = self.result_queue.get(timeout=timeout)
            if result:
                self.logger.debug(f"Got result from queue: {result[0]}")
            return result
        except queue.Empty:
            self.logger.debug("No result in queue within timeout")
            return None

    def call_tool(self, tool_name: str, arguments: dict) -> CallToolRequest:
        """
        从主线程通过托管会话调用工具。
        
        此方法允许主线程通过托管会话在服务器上执行工具。
        它使用asyncio.run_coroutine_threadsafe在不同线程中安全地调用异步方法。
        
        参数:
            tool_name (str): 要调用的工具名称
            arguments (dict): 传递给工具的参数
            
        返回:
            Any: 工具执行的结果
            
        异常:
            RuntimeError: 如果会话未初始化
        """
        if not self.session or not self.loop:
            error_msg = "Cannot call tool: session not initialized"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        self.logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
        
        # 在工作线程的事件循环中安排协程运行
        future = asyncio.run_coroutine_threadsafe(
            self.session.call_tool(tool_name, arguments), 
            self.loop
        )
        
        try:
            # 等待并返回结果
            result = future.result()
            self.logger.info(f"Tool call successful: {tool_name}")
            return result
        except Exception as e:
            self.logger.error(f"Tool call failed: {tool_name}, error: {str(e)}", exc_info=True)
            raise

    def stop(self) -> None:
        """
        优雅地停止会话管理线程。
        
        此方法向工作线程发出停止信号并等待其终止。
        应在finally块中调用以确保正确清理。
        """
        if self.stop_event:
            self.logger.info("Setting stop event")
            self.stop_event.set()
            
        if self.thread:
            self.logger.info("Waiting for worker thread to join")
            self.thread.join()
            self.logger.info("Worker thread joined successfully")

class SessionController:
    """
    管理会话状态和用户输入的控制器。
    
    该类负责：
    1. 管理SSE会话状态
    2. 处理用户输入
    3. 控制会话的开启和关闭
    """
    
    def __init__(self, manager: SseSessionManager):
        """
        初始化会话控制器。
        
        参数:
            manager (SseSessionManager): SSE会话管理器
        """
        self.manager = manager
        self.running = False
        self.event_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(f"{__name__}.SessionController")
        
    async def start_session(self) -> None:
        """启动会话。"""
        if not self.running:
            self.logger.info("Starting session")
            self.manager.start()
            self.running = True
            self.logger.info("Session started successfully")

    async def stop_session(self) -> None:
        """停止会话。"""
        if self.running:
            self.logger.info("Stopping session")
            self.manager.stop()
            self.running = False
            if self.event_task and not self.event_task.done():
                self.logger.info("Cancelling event handling task")
                self.event_task.cancel()
            self.logger.info("Session stopped")

    async def handle_events(self) -> None:
        """
        异步处理SSE会话事件。
        
        这个协程负责处理从SseSessionManager接收到的所有事件，
        包括连接状态、可用工具列表和错误信息。
        """
        self.logger.info("Starting event handling")
        
        try:
            # 事件处理循环
            while self.running:
                # 以1秒超时获取下一个结果
                result = self.manager.get_result(timeout=1.0)
                if result:
                    event_type, data = result
                    if event_type == 'connected':
                        self.logger.info(f"Connected to server: {data}")
                    elif event_type == 'tools':
                        self.logger.info(f"Available tools: {data}")
                    elif event_type == 'error':
                        self.logger.error(f"Session error: {data}")
                        break

                # 检查工作线程是否已终止
                if not self.manager.thread.is_alive():
                    self.logger.warning("Worker thread is not alive")
                    break
                    
        except asyncio.CancelledError:
            self.logger.info("Event handling task cancelled")
        except Exception as e:
            self.logger.error(f"Event handling error: {str(e)}", exc_info=True)
            
    async def input_listener(self) -> None:
        """
        监听用户输入以控制会话。
        
        支持的命令：
        - start: 启动会话
        - stop: 停止会话
        - quit: 退出程序
        """
        self.logger.info("Starting input listener")
        
        try:
            while True:
                try:
                    # 从标准输入读取命令
                    if sys.stdin.isatty():
                        self.logger.debug("Reading command from interactive input")
                        user_input = await asyncio.get_event_loop().run_in_executor(
                            None, input, "Enter command (start/stop/quit): "
                        )
                    else:
                        # 非交互式环境下的处理
                        self.logger.debug("Reading command from non-interactive input")
                        user_input = await asyncio.get_event_loop().run_in_executor(
                            None, sys.stdin.readline
                        )
                        if not user_input:
                            self.logger.info("End of input stream reached")
                            break
                        user_input = user_input.strip()
                    
                    user_input = user_input.strip().lower()
                    self.logger.info(f"Received command: {user_input}")
                    
                    if user_input == 'start':
                        await self.start_session()
                    elif user_input == 'stop':
                        await self.stop_session()
                    elif user_input == 'quit':
                        self.logger.info("Quit command received")
                        await self.stop_session()
                        break
                    elif user_input.startswith('call_tool'):
                        # 解析 call_tool 命令
                        try:
                            if not self.running:
                                print("Error: Session is not running. Please start the session first.")
                                continue
                                
                            # 分割命令获取参数
                            parts = user_input.split(' ', 2)
                            if len(parts) != 3:
                                print("Error: Invalid format. Use 'call_tool name=xxxx params={}'")
                                continue
                                
                            # 解析 name 参数
                            if not parts[1].startswith('name='):
                                print("Error: Second parameter must be name=xxxx")
                                continue
                            tool_name = parts[1][5:]  # 去掉 'name=' 前缀
                            
                            # 解析 params 参数
                            if not parts[2].startswith('params='):
                                print("Error: Third parameter must be params={}")
                                continue
                            params_str = parts[2][7:]  # 去掉 'params=' 前缀
                            
                            # 解析 JSON 参数
                            try:
                                import json
                                params = json.loads(params_str)
                            except json.JSONDecodeError as e:
                                print(f"Error: Invalid JSON in params - {str(e)}")
                                continue

                            self.logger.info(f"Calling tool '{tool_name}' with params: {params}")
                            result = self.manager.call_tool(tool_name, params)
                            if isinstance(result, dict) and "progress" in result:
                                progress = result["progress"]
                                total = result["total"]
                                percentage = (progress / total) * 100
                                logging.info(
                                    f"Progress: {progress}/{total} "
                                    f"({percentage:.1f}%)"
                                )
                            self.logger.info(f"Tool result: {result} with type {type(result)}")
                            
                        except Exception as e:
                            self.logger.error(f"Error calling tool: {str(e)}")
                    else:
                        self.logger.warning(f"Unknown command: {user_input}")
                        
                except EOFError:
                    self.logger.info("EOF encountered in input stream")
                    # 处理输入流结束
                    break
                except Exception as e:
                    self.logger.error(f"Input error: {str(e)}", exc_info=True)
                    print(f"Input error: {str(e)}")
                    break
                    
        except asyncio.CancelledError:
            self.logger.info("Input listener task cancelled")
            print("Input listener task cancelled")
            
    async def run(self) -> None:
        """
        运行会话控制器。
        
        启动事件处理任务和输入监听任务，并等待它们完成。
        """
        self.logger.info("Starting session controller")
        
        # 创建任务
        self.event_task = asyncio.create_task(self.handle_events())
        input_task = asyncio.create_task(self.input_listener())
        
        self.logger.info("Session controller tasks created")
        
        try:
            # 等待输入监听任务完成（通常是用户输入quit）
            self.logger.info("Waiting for input listener task to complete")
            await input_task
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        finally:
            # 确保会话被停止
            self.logger.info("Cleaning up session controller")
            await self.stop_session()
            # 取消事件处理任务
            if self.event_task and not self.event_task.done():
                self.logger.info("Cancelling event handling task")
                self.event_task.cancel()

async def main():
    """
    主函数，演示多线程SSE会话管理。
    
    此函数展示了如何使用SseSessionManager类：
    1. 创建管理器实例
    2. 创建会话控制器
    3. 运行控制器
    """
    # 创建会话管理器
    manager = SseSessionManager("http://localhost:8080/mcp/sse")

    # 创建会话控制器
    controller = SessionController(manager)

    # 运行控制器
    await controller.run()

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
