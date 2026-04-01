#!/usr/bin/env python3
"""MCP server — exposes AIO ontology search as a tool for Claude Desktop / claude.ai.

NOTE: This MCP server is kept for Claude Desktop integration. When using Claude
Code, prefer the aio-search agent or skill instead — no API key required.
"""

from mcp.server.fastmcp import FastMCP
from search_aio import label_search, run_sparql, _load_ontology

mcp = FastMCP("aio-ontology")


@mcp.tool()
def search_aio_sparql(sparql: str) -> str:
    """Execute a SPARQL SELECT query against the AIO ontology.

    Args:
        sparql: A SPARQL SELECT query. Standard aio/rdfs/owl/rdf prefixes are
                injected automatically if omitted.

    Returns:
        Raw ontology result rows, one per line.
    """
    _load_ontology()
    results = run_sparql(sparql)
    return "\n".join(str(row) for row in results)


@mcp.tool()
def search_aio_label(term: str) -> str:
    """Search the AIO ontology by label/comment substring (no SPARQL needed).

    Args:
        term: Case-insensitive substring to search in rdfs:label and rdfs:comment.

    Returns:
        Matching entities as [iri, label, comment] rows, one per line.
    """
    _load_ontology()
    results = label_search(term)
    return "\n".join(str(row) for row in results)


if __name__ == "__main__":
    mcp.run()
