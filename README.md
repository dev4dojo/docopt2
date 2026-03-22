# docopt2

<div align="center">
  <h1>Docopt 2.0</h1>
  <p><strong>Usage is Truth.</strong></p>
  <p>A modular, type-safe CLI parsing pipeline built on Python frozen dataclasses and an immutable backtracking engine.</p>
</div>

> The usage string is the specification.

`docopt2` is a modern, high-performance, and type-safe re-imagining of the classic `docopt` library. Instead of relying on a monolithic block of procedural regex, `docopt2` utilizes a structured **Intermediate Representation (IR) pipeline** to transform your CLI documentation into a verifiable Abstract Syntax Tree (AST).

## Why docopt2?

Most CLI parsers require you to write code to define your interface. `docopt2` flips the script: **you write the documentation, and the code follows.**

* **Type-Safe:** Fully type-hinted and compliant with PEP 561.
* **Modular Architecture:** Decoupled Lexer, Parser, and Engine for maximum testability.
* **Backtracking Matcher:** A sophisticated tree-walking engine that finds the "best fit" for complex command patterns.
* **Immutability:** Uses frozen dataclasses and immutable match contexts to prevent side effects.
* **Modern Data Structures:** Automatically aggregates repeating arguments into lists (e.g., `{'<file>': ['a.txt', 'b.txt']}`).

## Quick Start

```python
from docopt2 import docopt

doc = """
Nav-CLI: A modern navigation tool.

Usage:
  nav-cli move <source> <dest> [--speed=<kn>]
  nav-cli ship (cargo | tanker) <id>...
  nav-cli -h | --help

Options:
  -h --help       Show this screen.
  --speed=<kn>    Speed in knots [default: 10].
"""

# Case: nav-cli move Port_A Port_B --speed 25
arguments = docopt(doc, ["move", "Port_A", "Port_B", "--speed", "25"])

print(arguments)
# Output:
# {
#   'move': True, 
#   '<source>': 'Port_A', 
#   '<dest>': 'Port_B', 
#   '--speed': '25'
# }
```

## The Pipeline Architecture

`docopt2` processes your input through a four-stage compiler-grade pipeline:

1.  **Extraction:** Isolates the `Usage:` block from your docstring.
2.  **Lexical Analysis:** Scans the DSL into semantic, position-aware tokens.
3.  **Syntactic Analysis:** A Recursive Descent Parser builds a hierarchical AST.
4.  **Matching Engine:** A backtracking visitor traverses the AST against `argv` to produce a result dictionary.

## Installation

```bash
pip install git+https://github.com/dev4dojo/docopt2.git
```

*(Note: This is a 2026-standard library requiring Python 3.12+)*

## Advanced Features

### Repetition (...)

Arguments or groups followed by an ellipsis are automatically aggregated into a list.
* **Usage:** `my-app <id>...`
* **Input:** `my-app 101 102 103`
* **Result:** `{"<id>": ["101", "102", "103"]}`

### Mutual Exclusion (`|`)

Easily handle complex command branches.
* **Usage:** `my-app (remote | local) <path>`
* **Input:** `my-app local /tmp`
* **Result:** `{"local": True, "<path>": "/tmp"}`

## Development & Testing

We believe in **100% testability**. The project is split into granular units that can be tested in isolation.

```bash
# Run the full suite
pytest

# Test components specifically
pytest tests/test_lexer.py
pytest tests/test_parser.py
pytest tests/test_engine.py
```

## License

MIT License. See `LICENSE` for more information.
