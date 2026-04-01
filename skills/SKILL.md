---
name: aio-search
description: Search the Artificial Intelligence Ontology (AIO) for AI concepts, algorithms, techniques, and model types. Runs entirely within the current Claude Code session — no API key required.
---

# AIO Ontology Search

Search the AIO ontology for the concept or question provided in the arguments.

## Ontology facts

- Namespace: `https://w3id.org/aio/`
- Classes have `rdfs:label` (name) and `rdfs:comment` (definition)
- Subclass relations: `?child rdfs:subClassOf ?parent`
- Standard prefixes:

```sparql
PREFIX aio: <https://w3id.org/aio/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
```

## Instructions

1. Write a SPARQL SELECT query for the question: `$ARGUMENTS`
2. Execute it:

```bash
aio-search --sparql "YOUR QUERY" --json
```

3. If results are empty or errored, revise the query and retry (up to 3 times).
4. Fall back to label search if SPARQL keeps failing:

```bash
aio-search --label "keyword" --json
```

5. Present the results clearly — include the concept name, IRI, and definition where available.
