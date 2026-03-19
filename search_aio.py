#!/usr/bin/env python3
"""AIO subagent — query the Artificial Intelligence Ontology via natural language."""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import anthropic
from owlready2 import get_ontology, default_world

DEFAULT_OWL = Path(__file__).parent / "aio-full.owl"
NS = "https://w3id.org/aio/"

_onto = None
_client = None


def _load_ontology(owl_path: Path):
    global _onto
    if _onto is None:
        print("Loading AIO ontology...", file=sys.stderr)
        _onto = get_ontology(f"file://{owl_path}").load()
        print("Ontology loaded.", file=sys.stderr)
    return _onto


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not set.", file=sys.stderr)
            sys.exit(1)
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


SPARQL_CTX = f"""You query the AIO (Artificial Intelligence Ontology) via SPARQL.
Namespace: {NS}
Prefixes:
  PREFIX aio: <{NS}>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  PREFIX owl: <http://www.w3.org/2002/07/owl#>
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

Classes have rdfs:label (name) and rdfs:comment (definition).
Subclass relations: ?child rdfs:subClassOf ?parent
Return ONLY the SPARQL SELECT query, no explanation or markdown."""


def _llm(prompt: str, max_tokens: int = 512) -> str:
    return _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    ).content[0].text.strip()


def _run_sparql(query: str) -> list:
    query = re.sub(r"^```(?:sparql)?\n?", "", query.strip())
    query = re.sub(r"\n?```$", "", query).strip()
    try:
        return list(default_world.sparql(query))[:15]
    except Exception as e:
        return [f"SPARQL error: {e}"]


def search(question: str, owl_path: Path = DEFAULT_OWL, max_iters: int = 3) -> dict:
    """Search the AIO ontology for a question.

    Scope filtering is handled by the parent pipeline — this subagent always searches.

    Returns:
        {
          "answer": str,
          "attempts": int
        }

    Can be imported and called directly by a parent agent:
        from search_aio import search
        result = search("What is reinforcement learning?")
    """
    _load_ontology(owl_path)

    history = []
    for i in range(max_iters):
        prev = (
            "\n".join(
                f"Attempt {j+1}:\n  Query: {h['q'][:200]}\n  Results: {str(h['r'])[:300]}"
                for j, h in enumerate(history)
            )
            if history
            else "None yet."
        )

        sparql = _llm(
            f"{SPARQL_CTX}\n\n"
            f"Question: {question}\n\n"
            f"Previous attempts:\n{prev}\n\n"
            "Write a SPARQL query:",
            max_tokens=400,
        )
        results = _run_sparql(sparql)
        history.append({"q": sparql, "r": results})

        print(
            f"  [iter {i+1}] {results[:2]}{'...' if len(results) > 2 else ''}",
            file=sys.stderr,
        )

        answer = _llm(
            f"Question: {question}\n\n"
            "AIO ontology SPARQL results:\n"
            + "\n".join(f"Attempt {j+1}: {h['r']}" for j, h in enumerate(history))
            + "\n\nAnswer the question from these results. "
            "If insufficient, start with NEED_MORE.",
            max_tokens=600,
        )

        if not answer.upper().startswith("NEED_MORE"):
            return {"answer": answer, "attempts": i + 1}

    final = _llm(
        f"Question: {question}\n\nAll ontology data:\n"
        + "\n".join(str(h["r"]) for h in history)
        + "\n\nGive the best possible answer.",
        max_tokens=600,
    )
    return {"answer": final, "attempts": max_iters}


# ---------------------------------------------------------------------------
# Claude tool schema — use this when registering aio-search as a tool in a
# parent Claude agent (tool_use / computer-use pattern).
# ---------------------------------------------------------------------------
TOOL_SCHEMA = {
    "name": "search_aio",
    "description": (
        "Query the Artificial Intelligence Ontology (AIO) with a natural-language question. "
        "Returns a structured answer grounded in the ontology. "
        "Scope filtering is handled by the caller — always passes the question through."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "A natural-language question about an AI concept.",
            }
        },
        "required": ["question"],
    },
}


def main():
    parser = argparse.ArgumentParser(
        prog="aio-search",
        description="Query the AI Ontology (AIO) with natural language. "
        "Designed to run as a standalone CLI or as a subagent tool.",
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Question to ask. Omit for interactive mode.",
    )
    parser.add_argument(
        "--ontology",
        type=Path,
        default=DEFAULT_OWL,
        metavar="PATH",
        help="Path to aio-full.owl (default: ./aio-full.owl)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_out",
        help="Output result as JSON — use this when called from a parent agent.",
    )
    args = parser.parse_args()

    if args.question:
        # Single-shot mode (agent / scripted use)
        result = search(args.question, owl_path=args.ontology)
        if args.json_out:
            print(json.dumps(result))
        else:
            print(result["answer"])
    else:
        # Interactive REPL
        _load_ontology(args.ontology)
        print("=== AIO Ontology Search ===  (type 'quit' to exit)\n")
        while True:
            try:
                question = input("Question: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not question or question.lower() in ("quit", "exit", "q"):
                break
            result = search(question, owl_path=args.ontology)
            print(f"\n{result['answer']}\n" + "─" * 60 + "\n")


if __name__ == "__main__":
    main()
