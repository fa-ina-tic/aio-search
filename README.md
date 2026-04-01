# AIO Agent — AI Ontology Search for Claude Code

A CLI tool that searches the **Artificial Intelligence Ontology (AIO)** via SPARQL.
No LLM required — SPARQL queries are written by the Claude Code agent or skill, not by the CLI itself.

It is designed to run as:
- A **Claude Code plugin** (agent + skill, installed via marketplace)
- A **standalone CLI** for direct use
- An **MCP server** for Claude Desktop / claude.ai

---

## 1. Claude Code Plugin (recommended)

Install directly from GitHub:

```bash
/plugin marketplace add fa-ina-tic/aio-search
```

On first session start, the plugin automatically:
1. Creates a venv at `$CLAUDE_PLUGIN_DATA/.venv` and installs dependencies
2. Symlinks `aio-search` to `~/.local/bin/` so it works from any directory
3. Downloads `aio-full.owl` (~5 MB) to `$CLAUDE_PLUGIN_DATA/`

Once installed, use the skill or agent in any project:

```
/aio-search what is a transformer?
```

Or Claude Code will invoke the `aio-search` subagent automatically when answering AI concept questions.

---

## 2. Standalone CLI

### Install

```bash
uv sync
```

This registers the `aio-search` CLI command inside the project venv.

### SPARQL query

```bash
aio-search --sparql "
PREFIX aio: <https://w3id.org/aio/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?class ?label ?comment WHERE {
  ?class rdfs:label ?label .
  FILTER(CONTAINS(LCASE(STR(?label)), \"transformer\"))
  OPTIONAL { ?class rdfs:comment ?comment }
}
" --json
```

### Label search (no SPARQL needed)

```bash
aio-search --label "transformer" --json
```

Standard `aio:` / `rdfs:` / `owl:` / `rdf:` prefixes are injected automatically if omitted.

---

## 3. MCP Server (Claude Desktop / claude.ai)

Start the server:

```bash
uv run mcp_server.py
```

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aio-ontology": {
      "command": "uv",
      "args": ["run", "mcp_server.py"],
      "cwd": "/absolute/path/to/aio-search"
    }
  }
}
```

Two tools are exposed:
- `search_aio_sparql(sparql)` — execute a SPARQL SELECT query
- `search_aio_label(term)` — substring search on label/comment

---

## 4. Python API

```python
from search_aio import run_sparql, label_search, _load_ontology

_load_ontology()

rows = run_sparql("SELECT ?class ?label WHERE { ?class rdfs:label ?label }")
rows = label_search("transformer")
```

---

## How It Works

```
User question
     │
     ▼
Claude Code agent/skill writes SPARQL query
     │
     ▼
aio-search CLI  ──▶  owlready2 query on aio-full.owl
     │
     ▼
Raw ontology results (JSON)
     │
     ▼
Claude Code formats and presents results
```

No LLM API calls are made by the CLI — all reasoning happens in the Claude Code session.

---

## Project Structure

```
search_aio.py              ← CLI: --sparql / --label / --json flags
mcp_server.py              ← MCP server (search_aio_sparql, search_aio_label tools)
agents/aio-search.md       ← Claude Code subagent definition
skills/SKILL.md            ← Claude Code /aio-search skill definition
scripts/install.sh         ← SessionStart hook: install deps + symlink binary
hooks/hooks.json           ← Hook manifest
.claude-plugin/
  plugin.json              ← Plugin manifest (marketplace distribution)
  marketplace.json         ← Marketplace catalog
pyproject.toml             ← deps + aio-search CLI entry point
```
