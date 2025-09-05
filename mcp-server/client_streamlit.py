import asyncio
import json
import logging
import os
from contextlib import AsyncExitStack
from typing import Any

import streamlit as st
from dotenv import load_dotenv

# Import core components from terminal client
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp import ClientSession, StdioServerParameters

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# LLM configuration constants
LLM_TEMPERATURE = 0.7
LLM_TOP_P = 1
LLM_STREAM = False

# Page configuration
st.set_page_config(
    page_title="MCP Chat",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto"
)

class Configuration:
    """Manages configuration and environment variables for the MCP client."""
    
    def __init__(self) -> None:
        """Initialize configuration with environment variables."""
        self.api_key = os.getenv("LLM_API_KEY")
        if not self.api_key:
            raise ValueError("LLM_API_KEY not found in environment variables")

    @staticmethod
    def load_config(file_path: str) -> dict[str, Any]:
        """Load server configuration from JSON file.
        
        Args:
            file_path: Path to the JSON configuration file.
            
        Returns:
            Dict containing server configuration.
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            JSONDecodeError: If configuration file is invalid JSON.
        """
        with open(file_path, "r", encoding="utf8") as f:
            return json.load(f)

    @property
    def llm_api_key(self) -> str:
        """Get the LLM API key.
        
        Returns:
            The API key as a string.
            
        Raises:
            ValueError: If the API key is not found in environment variables.
        """
        if not self.api_key:
            raise ValueError("LLM_API_KEY not found in environment variables")
        return self.api_key


class Server:
    """Manages MCP server connections and tool execution."""
    
    def __init__(self, name: str, config: dict[str, Any]) -> None:
        self.name: str = name
        self.config: dict[str, Any] = config
        self.stdio_context: Any | None = None
        self.session: ClientSession | None = None
        self._cleanup_lock: asyncio.Lock = asyncio.Lock()
        self.exit_stack: AsyncExitStack = AsyncExitStack()

    async def initialize(self) -> None:
        """Initialize the server connection using the appropriate transport."""
        try:
            transport = self.config.get("transport", "stdio")
            
            if transport == "sse":
                url = self.config.get("url")
                if not url:
                    raise ValueError(f"URL required for SSE transport in server {self.name}")
                
                # Use sse_client context manager for SSE connections
                read, write = await self.exit_stack.enter_async_context(
                    sse_client(url)
                )
                session = await self.exit_stack.enter_async_context(
                    ClientSession(read, write)
                )
                await session.initialize()
                self.session = session
                logging.info(f"Connected to server {self.name} via SSE at {url}")
                
            else:
                # Handle stdio transport for local processes
                import shutil
                command = (
                    shutil.which("npx")
                    if self.config["command"] == "npx"
                    else self.config["command"]
                )
                if command is None:
                    raise ValueError("The command must be a valid string and cannot be None.")

                server_params = StdioServerParameters(
                    command=command,
                    args=self.config["args"],
                    env={**os.environ, **self.config["env"]}
                    if self.config.get("env")
                    else None,
                )
                stdio_transport = await self.exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                read, write = stdio_transport
                session = await self.exit_stack.enter_async_context(
                    ClientSession(read, write)
                )
                await session.initialize()
                self.session = session
                logging.info(f"Connected to server {self.name} via stdio")
                
        except Exception as e:
            logging.error(f"Error initializing server {self.name}: {e}")
            await self.cleanup()
            raise

    async def list_tools(self) -> list[Any]:
        """List available tools from the server.
        
        Returns:
            A list of available tools.
            
        Raises:
            RuntimeError: If the server is not initialized.
        """
        transport = self.config.get("transport", "stdio")
        if transport == 'stdio' and not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")
        if transport == 'sse':
            async with sse_client(self.config.get("url")) as streams:
                async with ClientSession(*streams) as session:
                    self.session = session
                    await self.session.initialize()
                    tools_response = await self.session.list_tools()
        else:
            tools_response = await self.session.list_tools()
        tools = []
        if tools_response:
            for item in tools_response:
                if isinstance(item, tuple) and item[0] == "tools":
                    for tool in item[1]:
                        tools.append(Tool(tool.name, tool.description, tool.inputSchema))

        return tools

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        retries: int = 2,
        delay: float = 1.0,
    ) -> Any:
        """Execute a tool with retry mechanism.
        
        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.
            retries: Number of retry attempts.
            delay: Delay between retries in seconds.
            
        Returns:
            Tool execution result.
            
        Raises:
            RuntimeError: If server is not initialized.
            Exception: If tool execution fails after all retries.
        """
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")

        attempt = 0
        transport = self.config.get("transport", "stdio")
        while attempt < retries:
            try:
                logging.info(f"Executing {tool_name}...")
                if transport == 'sse':
                    async with sse_client(self.config.get("url")) as streams:
                        async with ClientSession(*streams) as session:
                            self.session = session
                            await self.session.initialize()
                            result = await self.session.call_tool(tool_name, arguments)
                else:
                    result = await self.session.call_tool(tool_name, arguments)
                return result

            except Exception as e:
                attempt += 1
                logging.warning(
                    f"Error executing tool: {e}. Attempt {attempt} of {retries}."
                )
                if attempt < retries:
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logging.error("Max retries reached. Failing.")
                    raise

    async def cleanup(self) -> None:
        """Clean up server resources."""
        async with self._cleanup_lock:
            try:
                await self.exit_stack.aclose()
                self.session = None
                self.stdio_context = None
            except Exception as e:
                logging.error(f"Error during cleanup of server {self.name}: {e}")


class Tool:
    """Represents a tool with its properties and formatting."""
    
    def __init__(
        self, name: str, description: str, input_schema: dict[str, Any]
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.input_schema: dict[str, Any] = input_schema

    def format_for_llm(self) -> str:
        """Format tool information for LLM.
        
        Returns:
            A formatted string describing the tool.
        """
        args_desc = []
        if "properties" in self.input_schema:
            for param_name, param_info in self.input_schema["properties"].items():
                arg_desc = (
                    f"- {param_name}: {param_info.get('description', 'No description')}"
                )
                if param_name in self.input_schema.get("required", []):
                    arg_desc += " (required)"
                args_desc.append(arg_desc)

        return f"""
Tool: {self.name}
Description: {self.description}
Arguments:
{chr(10).join(args_desc)}
"""


class LLMClient:
    """Manages communication with the LLM provider."""
    
    def __init__(self) -> None:
        pass

    def get_response(self, messages: list[dict[str, str]]) -> str:
        """Get a response from the LLM.
        
        Args:
            messages: A list of message dictionaries.
            
        Returns:
            The LLM's response as a string.
            
        Raises:
            httpx.RequestError: If the request to the LLM fails.
        """
        import httpx
        from httpx import Timeout
        
        url = os.getenv("LLM_API_URL")
        if not url:
            raise ValueError("LLM_API_URL not found in environment variables")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('LLM_API_KEY')}",
        }
        payload = {
            "messages": messages,
            "model": os.getenv("LLM_MODEL"),
            "temperature": LLM_TEMPERATURE,
            "top_p": LLM_TOP_P,
            "stream": LLM_STREAM,
            "stop": None,
        }

        try:
            with httpx.Client(timeout=Timeout(40)) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except httpx.RequestError as e:
            error_message = f"Error getting LLM response: {str(e)}"
            logging.error(error_message)

            if isinstance(e, httpx.HTTPStatusError):
                status_code = e.response.status_code
                logging.error(f"Status code: {status_code}")
                logging.error(f"Response details: {e.response.text}")

            return (
                f"I encountered an error: {error_message}. "
                "Please try again or rephrase your request."
            )


class ChatSession:
    """Orchestrates the interaction between user, LLM, and tools."""
    
    def __init__(self, servers: list[Server], llm_client: LLMClient) -> None:
        self.servers: list[Server] = servers
        self.llm_client: LLMClient = llm_client

    async def cleanup_servers(self) -> None:
        """Clean up all servers properly."""
        if not self.servers:
            return
            
        # Use asyncio.shield to protect cleanup tasks from cancellation
        cleanup_tasks = []
        for server in self.servers:
            # Wrap each cleanup task with shield to prevent cancellation
            cleanup_task = asyncio.shield(server.cleanup())
            cleanup_tasks.append(cleanup_task)

        if cleanup_tasks:
            try:
                # Wait for all cleanup tasks to complete
                results = await asyncio.gather(*cleanup_tasks, return_exceptions=True)
                # Log any exceptions that occurred during cleanup
                for result in results:
                    if isinstance(result, Exception):
                        logging.warning(f"Cleanup task completed with exception: {result}")
            except asyncio.CancelledError:
                logging.warning("Cleanup operation was cancelled")
                # If we're cancelled, make sure to wait for cleanup tasks to complete
                results = await asyncio.gather(*cleanup_tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, Exception):
                        logging.warning(f"Cleanup task completed with exception: {result}")
            except Exception as e:
                logging.warning(f"Unexpected error during cleanup: {e}")
                # Ensure cleanup tasks are awaited even if unexpected error occurs
                if cleanup_tasks:
                    await asyncio.gather(*cleanup_tasks, return_exceptions=True)

    async def process_llm_response(self, llm_response: str) -> str:
        """Process the LLM response and execute tools if needed.
        
        Args:
            llm_response: The response from the LLM.
            
        Returns:
            The result of tool execution or the original response.
        """
        import json

        try:
            tool_call_arr = json.loads(llm_response)
            if len(tool_call_arr) > 0:
                for tool_call in tool_call_arr:
                    if "tool" in tool_call and "arguments" in tool_call:
                        logging.info(f"Executing tool: {tool_call['tool']}")
                        logging.info(f"With arguments: {tool_call['arguments']}")

                        for server in self.servers:
                            tools = await server.list_tools()
                            if any(tool.name == tool_call["tool"] for tool in tools):
                                try:
                                    result = await server.execute_tool(
                                        tool_call["tool"], tool_call["arguments"]
                                    )

                                    if isinstance(result, dict) and "progress" in result:
                                        progress = result["progress"]
                                        total = result["total"]
                                        percentage = (progress / total) * 100
                                        logging.info(
                                            f"Progress: {progress}/{total} "
                                            f"({percentage:.1f}%)"
                                        )

                                    return f"Tool execution result: {result}"
                                except Exception as e:
                                    error_msg = f"Error executing tool: {str(e)}"
                                    logging.error(error_msg)
                                    return error_msg

                return f"No server found with tool: {tool_call['tool']}"
            return llm_response
        except json.JSONDecodeError:
            return llm_response

    async def start(self) -> None:
        """Main chat session handler."""
        try:
            for server in self.servers:
                try:
                    await server.initialize()
                except Exception as e:
                    st.error(f"Failed to initialize server: {e}")
                    await self.cleanup_servers()
                    return

            all_tools = []
            for server in self.servers:
                tools = await server.list_tools()
                all_tools.extend(tools)

            tools_description = "\\n".join([tool.format_for_llm() for tool in all_tools])

            system_message = (
                "You are a helpful assistant with access to these tools:\\n\\n"
                f"{tools_description}\\n"
                "Choose the appropriate tools based on the user's question. "
                "If no tool is needed, reply directly.\\n\\n"
                "IMPORTANT: When you need to use one tool or more tools, respond "
                "exclusively with a valid JSON array of tool call objects in the exact format below "
                "the exact JSON object format below, nothing else:\\n"
                "[{\\n"
                '    "tool": "tool-name-1",\\n'
                '    "arguments": {\\n'
                '        "argument-name": "value-1"\\n'
                "    }\\n"
                "}\\n\\n"
                "{\\n"
                '    "tool": "tool-name-2",\\n'
                '    "arguments": {\\n'
                '        "argument-name": "value-2"\\n'
                "    }\\n"
                "}]\\n\\n"
                "After receiving tool response:\\n"
                "1. Transform the raw data into a natural, conversational response\\n"
                "2. Keep responses concise but informative\\n"
                "3. Focus on the most relevant information\\n"
                "4. Use appropriate context from the user's question\\n"
                "5. Avoid simply repeating the raw data\\n\\n"
                "Please use only the tools that are explicitly defined above."
            )

            # Initialize session state for messages if not exists
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {"role": "system", "content": system_message}
                ]

            # Display chat messages
            for message in st.session_state.messages:
                if message["role"] != "system":
                    with st.chat_message(message["role"]):
                        st.write(message["content"])

            # Get user input
            if prompt := st.chat_input("What would you like to know?"):
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Display user message
                with st.chat_message("user"):
                    st.write(prompt)

                # Get LLM response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        llm_response = self.llm_client.get_response(st.session_state.messages)
                        st.write("Assistant: " + llm_response)

                    # Process LLM response for tool calls
                    result = await self.process_llm_response(llm_response)

                    if result != llm_response:
                        # Add tool call to messages
                        st.session_state.messages.append({"role": "assistant", "content": llm_response})
                        st.session_state.messages.append({"role": "system", "content": result})

                        # Get final response from LLM
                        with st.spinner("Processing tool result..."):
                            final_response = self.llm_client.get_response(st.session_state.messages)
                            st.write("Final response: " + final_response)
                            st.session_state.messages.append(
                                {"role": "assistant", "content": final_response}
                            )
                    else:
                        # Add direct response to messages
                        st.session_state.messages.append({"role": "assistant", "content": llm_response})

        finally:
            await self.cleanup_servers()


async def main() -> None:
    """Initialize and run the chat session."""
    try:
        config = Configuration()
        server_config = config.load_config("mcp-server/passkg_config.json")
        servers = [
            Server(name, srv_config)
            for name, srv_config in server_config["mcpServers"].items()
        ]
        llm_client = LLMClient()
        chat_session = ChatSession(servers, llm_client)
        await chat_session.start()
    except Exception as e:
        st.error(f"Error starting chat application: {e}")
        logging.error(f"Error starting chat application: {e}")


if __name__ == "__main__":
    asyncio.run(main())
