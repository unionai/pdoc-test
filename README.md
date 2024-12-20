# pdoc-test

Experiment with building Union and Flytekit SDK docs using the `pdoc`(https://pdoc.dev/) tool.

## Installation

These instructions assume that you have `uv` (https://docs.astral.sh/uv/).

## Build docs with `pdoc`

Set up or update your virtual environment in `./.venv`:

```bash
$ uv sync
```

Set up an environment variable for `pdoc`:

```bash
$ export PDOC_ALLOW_EXEC=1
```

Run `pdoc` on the modules `union` and `flytekit` (using the virtual environment in `./.venv`):

```bash
uv run pdoc -o ./html union flytekit
```

The generated HTML docs will be in `./html`.