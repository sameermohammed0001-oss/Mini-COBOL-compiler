
# Mini-COBOL Compiler

A lightweight source-to-source compiler that translates a supported subset of COBOL into Python.

## Features

- Recognizes basic COBOL divisions.
- Supports numeric and alphanumeric variable declarations using PIC clauses.
- Maintains a symbol table.
- Supports MOVE, ADD, DISPLAY, and STOP RUN.
- Reports basic syntax and semantic errors.
- Generates executable Python code.

## Requirements

- Python 3
- Visual Studio Code
- Git

## Run the compiler

```bash
python3 src/compiler.py examples/input.cbl
```

## Run the generated program

```bash
python3 output.py
```

## Project structure

- `src/compiler.py` — compiler implementation
- `examples/input.cbl` — sample COBOL source program
- `tests/` — test cases
- `output.py` — generated Python file (not committed)

## Scope

This is an educational compiler prototype supporting a restricted subset of COBOL. It does not implement the complete COBOL language.
