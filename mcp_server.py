"""
MCP Server for TeachBack AI

This module provides an MCP (Model Context Protocol) server that exposes
the TeachingAgent functionality as tools for AI assistants and other MCP clients.
"""

import logging
import json
from typing import Any, Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.agents.teaching_agent import TeachingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("teachback-ai-mcp")

# Initialize the MCP server
app = Server("teachback-ai")

# Initialize the TeachingAgent
try:
    agent = TeachingAgent()
    logger.info("TeachingAgent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize TeachingAgent: {e}")
    raise


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available MCP tools.

    Returns:
        List of Tool objects describing available functionality
    """
    return [
        Tool(
            name="create_teaching_session",
            description="Create a new teaching practice session with specified topic and AI student personality",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Unique identifier for the user"
                    },
                    "topic": {
                        "type": "string",
                        "description": "The topic to be taught"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["socratic", "contrarian", "five-year-old", "anxious"],
                        "description": "AI student personality mode"
                    }
                },
                "required": ["user_id", "topic", "mode"]
            }
        ),
        Tool(
            name="analyze_explanation",
            description="Analyze the quality of a teaching explanation and detect knowledge gaps",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session identifier"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "The user's explanation text to analyze"
                    }
                },
                "required": ["session_id", "explanation"]
            }
        ),
        Tool(
            name="generate_question",
            description="Generate next question from AI student based on their personality mode",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session identifier"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "The user's latest explanation"
                    },
                    "analysis": {
                        "type": "object",
                        "description": "Analysis results from analyze_explanation",
                        "properties": {
                            "confidence_score": {"type": "number"},
                            "clarity_score": {"type": "number"},
                            "knowledge_gaps": {"type": "array", "items": {"type": "string"}},
                            "unexplained_jargon": {"type": "array", "items": {"type": "string"}},
                            "strengths": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["confidence_score", "clarity_score", "knowledge_gaps", "unexplained_jargon", "strengths"]
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["socratic", "contrarian", "five-year-old", "anxious"],
                        "description": "AI student personality mode"
                    }
                },
                "required": ["session_id", "explanation", "analysis", "mode"]
            }
        ),
        Tool(
            name="get_session_summary",
            description="Get comprehensive summary and analytics for a teaching session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session identifier"
                    }
                },
                "required": ["session_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """
    Handle tool execution requests.

    Args:
        name: The name of the tool to execute
        arguments: Dictionary of arguments for the tool

    Returns:
        List of TextContent responses

    Raises:
        ValueError: If tool name is not recognized
    """
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    try:
        if name == "create_teaching_session":
            result = await handle_create_teaching_session(arguments)
        elif name == "analyze_explanation":
            result = await handle_analyze_explanation(arguments)
        elif name == "generate_question":
            result = await handle_generate_question(arguments)
        elif name == "get_session_summary":
            result = await handle_get_session_summary(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        logger.info(f"Tool {name} executed successfully")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"error": error_msg}, indent=2)
        )]


async def handle_create_teaching_session(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle create_teaching_session tool calls.

    Args:
        arguments: Dictionary with user_id, topic, and mode

    Returns:
        Dictionary with session_id and welcome_message

    Raises:
        ValueError: If required arguments are missing or invalid
    """
    user_id = arguments.get("user_id")
    topic = arguments.get("topic")
    mode = arguments.get("mode")

    if not user_id or not topic or not mode:
        raise ValueError("Missing required arguments: user_id, topic, mode")

    result = agent.create_session(user_id=user_id, topic=topic, mode=mode)
    logger.debug(f"Created session: {result['session_id']}")
    return result


async def handle_analyze_explanation(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle analyze_explanation tool calls.

    Args:
        arguments: Dictionary with session_id and explanation

    Returns:
        Dictionary with analysis results (confidence_score, clarity_score, etc.)

    Raises:
        ValueError: If required arguments are missing
        KeyError: If session_id doesn't exist
    """
    session_id = arguments.get("session_id")
    explanation = arguments.get("explanation")

    if not session_id or not explanation:
        raise ValueError("Missing required arguments: session_id, explanation")

    result = agent.analyze_explanation(session_id=session_id, explanation=explanation)
    logger.debug(f"Analyzed explanation for session: {session_id}")
    return result


async def handle_generate_question(arguments: Dict[str, Any]) -> Dict[str, str]:
    """
    Handle generate_question tool calls.

    Args:
        arguments: Dictionary with session_id, explanation, analysis, and mode

    Returns:
        Dictionary with the generated question

    Raises:
        ValueError: If required arguments are missing or invalid
        KeyError: If session_id doesn't exist
    """
    session_id = arguments.get("session_id")
    explanation = arguments.get("explanation")
    analysis = arguments.get("analysis")
    mode = arguments.get("mode")

    if not session_id or not explanation or not analysis or not mode:
        raise ValueError("Missing required arguments: session_id, explanation, analysis, mode")

    # Validate analysis structure
    required_keys = ["confidence_score", "clarity_score", "knowledge_gaps",
                     "unexplained_jargon", "strengths"]
    if not all(key in analysis for key in required_keys):
        raise ValueError(f"Invalid analysis object. Required keys: {required_keys}")

    question = agent.generate_question(
        session_id=session_id,
        explanation=explanation,
        analysis=analysis,
        mode=mode
    )
    logger.debug(f"Generated question for session: {session_id}")
    return {"question": question}


async def handle_get_session_summary(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle get_session_summary tool calls.

    Args:
        arguments: Dictionary with session_id

    Returns:
        Dictionary with comprehensive session summary

    Raises:
        ValueError: If session_id is missing
        KeyError: If session_id doesn't exist
    """
    session_id = arguments.get("session_id")

    if not session_id:
        raise ValueError("Missing required argument: session_id")

    result = agent.get_session_summary(session_id=session_id)
    logger.debug(f"Retrieved summary for session: {session_id}")
    return result


async def main():
    """
    Main entry point for the MCP server.

    Initializes and runs the server using stdio transport for MCP protocol.
    """
    logger.info("Starting TeachBack AI MCP Server...")

    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running on stdio")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
