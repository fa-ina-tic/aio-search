# AIO Agent — AI Ontology Subagent

A CLI subagent that answers natural-language questions about AI concepts by querying the **Artificial Intelligence Ontology (AIO)** via SPARQL, then reasoning over the results with Claude.

It is designed to run as:
- A **standalone CLI** for human use
- A **subagent tool** called by a parent Claude agent

---

## 1. Download the AIO Ontology

> **Required before first run.**

Download `aio-full.owl` and place it in the project root:

```bash
curl -L "https://raw.githubusercontent.com/berkeleybop/artificial-intelligence-ontology/main/aio-full.owl" \
     -o aio-full.owl
```

Or download manually from:
https://github.com/berkeleybop/artificial-intelligence-ontology/blob/main/aio-full.owl

---

## 2. Install

```bash
uv sync
```

This registers the `aio-search` CLI command.

---

## 3. Usage

### Interactive mode

```bash
ANTHROPIC_API_KEY=sk-... aio-search
```

```
Question: What is reinforcement learning?
Question: What subclasses does neural network have?
```

### Single-shot (scripted / agent use)

```bash
aio-search "What is a transformer model?"
```

### JSON output — for parent agents

```bash
aio-search --json "What is supervised learning?"
# → {"results": [...], "query": "SELECT ...", "attempts": 1}
```

---

## 4. Integrations

### A — Claude Code marketplace (plugin install)

Install directly from GitHub into Claude Code:

```bash
/plugin marketplace add fa-ina-tic/aio-search
```

Or validate locally before distributing:

```bash
claude plugin validate .
```

Once installed, Claude Code will automatically discover and use the `aio-search` subagent.

---

### B — MCP server for Claude Desktop / claude.ai

Start the server:

```bash
ANTHROPIC_API_KEY=sk-... uv run mcp_server.py
```

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "aio-ontology": {
      "command": "uv",
      "args": ["run", "mcp_server.py"],
      "cwd": "/absolute/path/to/aio-search",
      "env": {
        "ANTHROPIC_API_KEY": "sk-..."
      }
    }
  }
}
```

Claude will then have a `search_aio` tool available in every conversation.

---

### C — Python import (programmatic use)

```python
from search_aio import search, TOOL_SCHEMA

result = search("What is a generative adversarial network?")
print(result["results"])   # raw SPARQL rows
print(result["query"])     # SPARQL query used
print(result["attempts"])  # number of retries

# TOOL_SCHEMA — pass to client.messages.create(tools=[TOOL_SCHEMA], ...)
```

---

## How It Works

```
User question (scope already validated by parent pipeline)
     │
     ▼
[Claude → SPARQL] ──▶ [owlready2 query on aio-full.owl]
     │                          │
     └──────── results ─────────┘
     │  (retries up to 3× if results are thin)
     ▼
  Raw ontology results
```

---

## Project Structure

```
aio-full.owl               ← ontology file (you download this)
search_aio.py              ← core: CLI + importable module + TOOL_SCHEMA
mcp_server.py              ← MCP server for Claude Desktop / claude.ai
.claude-plugin/
  plugin.json              ← plugin manifest (for marketplace distribution)
  marketplace.json         ← marketplace catalog (GitHub install target)
pyproject.toml             ← deps + aio-search CLI entry point
```
