# pdoc-test

Experiment with building Union and Flytekit SDK docs using the `pdoc`(https://pdoc.dev/) tool.

## Installation

These instructions assume that you have `uv` (https://docs.astral.sh/uv/).

## Build docs with `pdoc`

Set up an environment variable for `pdoc`:

```bash
$ export PDOC_ALLOW_EXEC=1
```

Run `pdoc` on the modules `union` and `flytekit`:

```bash
uv run pdoc -o ./html union flytekit
```

The generated HTML docs will be in `./html`.