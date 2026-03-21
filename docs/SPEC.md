# Architecture Specification: Docopt v2.0

## 1. Vision & Objective

To provide a high-performance, modular, and type-safe CLI parsing engine where the **usage string is the specification**. By moving away from legacy procedural regex-heavy logic toward a structured **Intermediate Representation (IR)** pipeline, we ensure 100% testability and long-term maintainability.

## 2. System Overview

The system is a unidirectional transformation pipeline. Each stage is decoupled via a formal contract (Tokens or AST Nodes).

### The Four Pillars:

1.  **Preprocessing:** Isolating the "Usage" DSL from descriptive docstring text.
2.  **Lexical Analysis:** Converting raw text into a stream of semantic, position-aware tokens.
3.  **Syntactic Analysis (The Parser):** Building a type-safe **Abstract Syntax Tree (AST)**.
4.  **Pattern Matching (The Engine):** Backtracking tree traversal using an **Immutable Match Context**.

## 3. The Data Model (The AST)

We use Python **frozen dataclasses** and a **Visitor Pattern** to ensure immutability and extensibility.

| Node Type | Hierarchy | Description | Key Properties |
| :--- | :--- | :--- | :--- |
| `Argument` | `Leaf` | A positional requirement. | `name: str`, `repeats: bool` |
| `Option` | `Leaf` | A flagged requirement. | `short`, `long`, `argcount` |
| `Command` | `Leaf` | A fixed keyword. | `name: str` |
| `Required` | `Branch` | An all-or-nothing group. | `children: tuple` |
| `Optional` | `Branch` | A non-blocking group. | `children: tuple` |
| `Choice` | `Branch` | Mutual exclusion (OR). | `children: tuple` |


## 4. Component Requirements

### 4.1. The Lexer

* **Stateful Streaming:** Tracks `line` and `column` for error reporting.
* **Tab-Stop Logic:** Correctly calculates column offsets using standard **8-character tab stops**.
* **Case Sensitivity:** Distinguishes between `lower` (Commands) and `UPPER` (Arguments).

### 4.2. The Parser (Recursive Descent)

* **Lookahead Parsing:** Identifies `--option=<arg>` as a single atomic `OptionNode` with `argcount=1`.
* **Type Narrowing:** Uses local variables to guarantee `token.value` is a `str` for all content nodes.
* **Precedence:** Implements "Choice" (OR) at the highest level to correctly handle `a b | c d`.

### 4.3. The Matcher Engine (Backtracking)

* **Immutable Context:** Uses a `MatchContext` that "forks" on match, allowing for easy backtracking in `ChoiceGroup` branches without side effects.
* **List Aggregation:** Automatically converts single values into lists (e.g., `{'<id>': ['S1', 'S2']}`) when the `repeats` flag is detected.

### 4.4. The Orchestrator

* **Extraction:** Uses regex to isolate the `Usage:` block from the full `__doc__` string.
* **Pattern Normalization:** Automatically skips the "Program Name" (the first token of each line) to match `sys.argv[1:]` directly.

## 5. Extensibility Hooks

* **Visitor Pattern:** New functionality (like Man-page generation or JSON export) can be added by creating a new `NodeVisitor` subclass without modifying the `Parser` or `Engine`.
* **Type Coercion:** A post-processing visitor can traverse the `MatchResult` and convert strings to `int`, `pathlib.Path`, or `bool`.

## 6. Project Directory Structure

```text
docopt2/
├── src/
│   └── docopt2/
│       ├── __init__.py      # Orchestrator & Preprocessor
│       ├── tokens.py        # Token Enum & Dataclass
│       ├── lexer.py         # Stateful Scanner (8-char tabs)
│       ├── nodes.py         # Frozen AST Nodes (Visitor Base)
│       ├── parser.py        # Recursive Descent (Lookahead)
│       ├── engine.py        # Backtracking Engine (List Aggregation)
│       ├── exceptions.py    # Language vs. User Error Hierarchy
│       └── py.typed         # PEP 561 compliance
└── tests/
    ├── test_lexer.py        # Unit tests for scanner
    ├── test_parser.py       # Unit tests for AST construction
    ├── test_engine.py       # Unit tests for matching logic
    └── test_smoke.py        # E2E Integration tests
```

### Final Implementation Check

We have verified this specification against a complex "Smoke Test" involving:
* Nested choices: `(cargo | tanker)`
* Repeated arguments: `<id>...`
* Options with values: `--speed=<kn>`
* Multiple usage patterns.
