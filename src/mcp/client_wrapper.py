"""
MCP Client Wrapper for Gradio Integration

This module provides a synchronous wrapper around the MCP client that makes it
easy to use TeachBack AI MCP tools from Gradio applications.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("teachback-mcp-client")


class MCPClientWrapper:
    """
    Synchronous wrapper for MCP client to interact with TeachBack AI server.

    This wrapper handles subprocess management, connection lifecycle, and provides
    simple synchronous methods that can be easily called from Gradio applications.
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize the MCP client wrapper.

        Args:
            timeout: Maximum seconds to wait for each MCP call (default: 30)

        Raises:
            RuntimeError: If mcp_server.py cannot be found or started
        """
        self.timeout = timeout
        self.session: Optional[ClientSession] = None
        self._server_process: Optional[subprocess.Popen] = None
        self._read_stream = None
        self._write_stream = None

        # Locate mcp_server.py
        self.server_script = self._find_server_script()
        if not self.server_script:
            raise RuntimeError("Could not locate mcp_server.py")

        logger.info(f"MCP Client Wrapper initialized with timeout={timeout}s")
        logger.info(f"Server script: {self.server_script}")

    def _find_server_script(self) -> Optional[Path]:
        """
        Locate the mcp_server.py script.

        Returns:
            Path to mcp_server.py or None if not found
        """
        # Try relative to current file
        current_dir = Path(__file__).parent
        repo_root = current_dir.parent.parent

        server_path = repo_root / "mcp_server.py"
        if server_path.exists():
            return server_path

        # Try current working directory
        cwd_path = Path.cwd() / "mcp_server.py"
        if cwd_path.exists():
            return cwd_path

        logger.error("Could not find mcp_server.py")
        return None

    async def _initialize_connection(self):
        """
        Initialize connection to MCP server via stdio.

        Raises:
            RuntimeError: If server process fails to start
            TimeoutError: If connection times out
        """
        if self.session is not None:
            logger.warning("Connection already initialized")
            return

        try:
            # Create server parameters for stdio connection
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[str(self.server_script)],
                env=os.environ.copy()
            )

            logger.info(f"Starting MCP server: {sys.executable} {self.server_script}")

            # Create stdio client connection
            self._stdio_context = stdio_client(server_params)
            self._read_stream, self._write_stream = await self._stdio_context.__aenter__()

            # Create session
            self._session_context = ClientSession(self._read_stream, self._write_stream)
            self.session = await self._session_context.__aenter__()

            # Initialize the session
            await self.session.initialize()

            logger.info("MCP client connected successfully")

        except Exception as e:
            logger.error(f"Failed to initialize MCP connection: {e}")
            await self._cleanup_connection()
            raise RuntimeError(f"Failed to connect to MCP server: {e}")

    async def _cleanup_connection(self):
        """Clean up MCP connection and server process."""
        try:
            # Clean up session
            if self.session and self._session_context:
                try:
                    await self._session_context.__aexit__(None, None, None)
                except Exception as e:
                    logger.warning(f"Error closing session: {e}")
                finally:
                    self.session = None

            # Clean up stdio streams
            if self._stdio_context:
                try:
                    await self._stdio_context.__aexit__(None, None, None)
                except Exception as e:
                    logger.warning(f"Error closing stdio: {e}")
                finally:
                    self._read_stream = None
                    self._write_stream = None

            logger.info("MCP connection cleaned up")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    async def _call_tool_async(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool asynchronously.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Tool response as dictionary

        Raises:
            RuntimeError: If not connected or tool call fails
            TimeoutError: If call exceeds timeout
        """
        if self.session is None:
            await self._initialize_connection()

        try:
            logger.debug(f"Calling tool: {tool_name} with args: {arguments}")

            # Call the tool with timeout
            result = await asyncio.wait_for(
                self.session.call_tool(tool_name, arguments),
                timeout=self.timeout
            )

            # Parse response
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                response_data = json.loads(response_text)

                # Check for errors
                if "error" in response_data:
                    raise RuntimeError(response_data["error"])

                logger.debug(f"Tool {tool_name} returned: {response_data}")
                return response_data
            else:
                raise RuntimeError(f"Empty response from tool {tool_name}")

        except asyncio.TimeoutError:
            logger.error(f"Tool call {tool_name} timed out after {self.timeout}s")
            raise TimeoutError(f"Tool call timed out after {self.timeout} seconds")
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise RuntimeError(f"Tool call failed: {e}")

    def _call_tool_sync(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous wrapper for tool calls.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Tool response as dictionary
        """
        try:
            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Run the async call
            return loop.run_until_complete(
                self._call_tool_async(tool_name, arguments)
            )
        except Exception as e:
            logger.error(f"Sync tool call failed: {e}")
            raise

    def create_teaching_session(self, user_id: str, topic: str, mode: str) -> Dict[str, Any]:
        """
        Create a new teaching practice session.

        Args:
            user_id: Unique identifier for the user
            topic: The topic to be taught
            mode: AI student personality (socratic, contrarian, five-year-old, anxious)

        Returns:
            Dictionary with session_id and welcome_message

        Raises:
            ValueError: If mode is invalid
            RuntimeError: If tool call fails
            TimeoutError: If call exceeds timeout

        Example:
            >>> client = MCPClientWrapper()
            >>> result = client.create_teaching_session("user123", "Python", "socratic")
            >>> print(result["session_id"])
            >>> print(result["welcome_message"])
        """
        arguments = {
            "user_id": user_id,
            "topic": topic,
            "mode": mode
        }
        return self._call_tool_sync("create_teaching_session", arguments)

    def analyze_explanation(self, session_id: str, explanation: str) -> Dict[str, Any]:
        """
        Analyze the quality of a teaching explanation.

        Args:
            session_id: The session identifier
            explanation: The user's explanation text

        Returns:
            Dictionary with:
                - confidence_score (float 0-1)
                - clarity_score (float 0-1)
                - knowledge_gaps (list of strings)
                - unexplained_jargon (list of strings)
                - strengths (list of strings)

        Raises:
            KeyError: If session doesn't exist
            RuntimeError: If tool call fails
            TimeoutError: If call exceeds timeout

        Example:
            >>> client = MCPClientWrapper()
            >>> analysis = client.analyze_explanation(
            ...     session_id="abc-123",
            ...     explanation="Python is a programming language..."
            ... )
            >>> print(f"Clarity: {analysis['clarity_score']}")
        """
        arguments = {
            "session_id": session_id,
            "explanation": explanation
        }
        return self._call_tool_sync("analyze_explanation", arguments)

    def generate_question(
        self,
        session_id: str,
        explanation: str,
        analysis: Dict[str, Any],
        mode: str
    ) -> str:
        """
        Generate next question from AI student.

        Args:
            session_id: The session identifier
            explanation: The user's latest explanation
            analysis: Analysis results from analyze_explanation
            mode: AI student personality mode

        Returns:
            The AI student's next question as a string

        Raises:
            KeyError: If session doesn't exist
            ValueError: If analysis structure is invalid
            RuntimeError: If tool call fails
            TimeoutError: If call exceeds timeout

        Example:
            >>> client = MCPClientWrapper()
            >>> question = client.generate_question(
            ...     session_id="abc-123",
            ...     explanation="Python uses dynamic typing...",
            ...     analysis=analysis_result,
            ...     mode="socratic"
            ... )
            >>> print(question)
        """
        arguments = {
            "session_id": session_id,
            "explanation": explanation,
            "analysis": analysis,
            "mode": mode
        }
        result = self._call_tool_sync("generate_question", arguments)
        return result.get("question", "")

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get comprehensive summary of a teaching session.

        Args:
            session_id: The session identifier

        Returns:
            Dictionary with:
                - topic (str)
                - mode (str)
                - total_turns (int)
                - average_confidence (float)
                - average_clarity (float)
                - persistent_gaps (list)
                - conversation_history (list)

        Raises:
            KeyError: If session doesn't exist
            RuntimeError: If tool call fails
            TimeoutError: If call exceeds timeout

        Example:
            >>> client = MCPClientWrapper()
            >>> summary = client.get_session_summary("abc-123")
            >>> print(f"Turns: {summary['total_turns']}")
            >>> print(f"Avg Clarity: {summary['average_clarity']}")
        """
        arguments = {
            "session_id": session_id
        }
        return self._call_tool_sync("get_session_summary", arguments)

    def cleanup(self):
        """
        Clean up resources and stop the MCP server.

        Should be called when done using the client, especially in
        finally blocks or context managers.

        Example:
            >>> client = MCPClientWrapper()
            >>> try:
            ...     result = client.create_teaching_session(...)
            ... finally:
            ...     client.cleanup()
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(self._cleanup_connection())
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except:
            pass
