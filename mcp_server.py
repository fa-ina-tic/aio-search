#!/usr/bin/env python3
"""MCP server — exposes AIO ontology search as a tool for Claude Desktop / claude.ai."""

from mcp.server.fastmcp import FastMCP
from search_aio import search

mcp = FastMCP("aio-ontology")


@mcp.tool()
def search_aio(question: str) -> str:
    """Query the Artificial Intelligence Ontology (AIO) with a natural-language question.

    Use this to look up AI concepts, algorithms, techniques, model types, and
    their relationships. Scope filtering is handled by the caller.

    Args:
        question: A natural-language question about an AI concept.

    Returns:
        A grounded answer derived from the AIO ontology.
    """
    result = search(question)
    return result["answer"]


if __name__ == "__main__":
    mcp.run()
