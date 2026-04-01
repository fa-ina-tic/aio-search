#!/usr/bin/env python3
"""AIO CLI — execute SPARQL queries against the Artificial Intelligence Ontology.

No LLM calls. SPARQL generation is the caller's responsibility (e.g. a Claude
Code agent or skill running on a subscription session).
"""

import argparse
import json
import re
import sys
from pathlib import Path

from owlready2 import get_ontology, default_world

DEFAULT_OWL = Path(__file__).parent / "aio-full.owl"
NS = "https://w3id.org/aio/"

SPARQL_PREFIXES = f"""\
PREFIX aio: <{NS}>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""

_onto = None


def _load_ontology(owl_path: Path):
    global _onto
    if _onto is None:
        print("Loading AIO ontology...", file=sys.stderr)
        _onto = get_ontology(f"file://{owl_path}").load()
        print("Ontology loaded.", file=sys.stderr)
    return _onto


def _serialize(val):
    if isinstance(val, (str, int, float, bool)) or val is None:
        return val
    return str(val)


def run_sparql(query: str) -> list:
    """Execute a raw SPARQL SELECT query. Returns list of result rows."""
    query = re.sub(r"^```(?:sparql)?\n?", "", query.strip())
    query = re.sub(r"\n?```$", "", query).strip()
    # Prepend standard prefixes if caller omitted them
    if "PREFIX" not in query.upper():
        query = SPARQL_PREFIXES + "\n" + query
    try:
        rows = list(default_world.sparql(query))[:20]
        return [[_serialize(cell) for cell in row] for row in rows]
    except Exception as e:
        return [f"SPARQL error: {e}"]


def label_search(term: str) -> list:
    """Simple case-insensitive label/comment search — no SPARQL needed."""
    term_lower = term.lower()
    results = []
    for entity in list(_onto.classes()) + list(_onto.properties()):
        label = getattr(entity, "label", [])
        comment = getattr(entity, "comment", [])
        label_str = label[0] if label else ""
        comment_str = comment[0] if comment else ""
        if term_lower in label_str.lower() or term_lower in comment_str.lower():
            results.append([entity.iri, label_str, comment_str[:200]])
        if len(results) >= 20:
            break
    return results


def main():
    parser = argparse.ArgumentParser(
        prog="aio-search",
        description=(
            "Execute SPARQL queries or label searches against the AIO ontology. "
            "No LLM calls — SPARQL is provided by the caller."
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--sparql",
        metavar="QUERY",
        help="Raw SPARQL SELECT query to execute.",
    )
    mode.add_argument(
        "--label",
        metavar="TERM",
        help="Case-insensitive substring search over rdfs:label and rdfs:comment.",
    )
    mode.add_argument(
        "--prefixes",
        action="store_true",
        help="Print the standard AIO SPARQL prefixes and exit.",
    )
    parser.add_argument(
        "--ontology",
        type=Path,
        default=DEFAULT_OWL,
        metavar="PATH",
        help="Path to aio-full.owl (default: next to this script)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_out",
        help="Output results as JSON.",
    )
    args = parser.parse_args()

    if args.prefixes:
        print(SPARQL_PREFIXES)
        return

    _load_ontology(args.ontology)

    if args.sparql:
        results = run_sparql(args.sparql)
    else:
        results = label_search(args.label)

    if args.json_out:
        print(json.dumps({"results": results}))
    else:
        for row in results:
            print(row)


if __name__ == "__main__":
    main()
