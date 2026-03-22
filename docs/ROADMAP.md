# ROADMAP

## P1: Developer Ergonomics & Type Safety

### Pydantic/Dataclass Integration (The "Model" Pattern)

Instead of returning a raw dictionary (e.g., `{"<source>": "A"}`), allow users to pass a target class. Docopt should map the parsed arguments directly into a validated Pydantic model or standard Dataclass. This provides IDE autocompletion and type safety for the application logic.

### Native Type Casting

The current spec returns strings or lists of strings. Implement an annotation system within the docstring or via a mapping dictionary to automatically cast values to `int`, `float`, `Path`, or `Enum` during the matching phase.

### Middleware & Lifecycle Hooks

Introduce "Before Match" and "After Match" hooks. This allows for global behaviors like initializing a logger, checking for environment variables, or validating a configuration file before the CLI logic executes.

## P2: Modern Interface Features

### Automatic Shell Completion

A CLI tool is incomplete without tab-completion. Add a feature to generate completion scripts for `zsh`, `bash`, and `fish` by traversing the generated AST.

### Subcommand Routing (The "Action" Decorator)

Parsing is only half the battle. Add a router that maps specific `Usage:` patterns to Python functions. 

> *Example:* `@docopt.command("move <source> <dest>")` would automatically trigger a specific function when that pattern is matched.

### Rich/Standard-Out Integration

Integration with libraries like `Rich` to provide beautiful, formatted help output, progress bars, and error messages (e.g., highlighting exactly where a syntax error occurred in the `Usage` string).

## P3: Advanced Logic & Validation

### Dependency-Based Validation

Implement logic for "If Option A is present, Option B is required." While some of this is handled by the `|` and `()` syntax, complex business-rule validation often requires a post-parsing validation pass.

### Interactive Prompting Fallback

If a required argument is missing, allow Docopt to optionally enter an "interactive mode" to prompt the user for the missing data rather than just exiting with an error.
