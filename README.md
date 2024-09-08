# AutoArena

AutoArena helps you stack rank LLM outputs against one another using automated judge evaluation. Get started by:

```
pip install autoarena
python -m autoarena
```

Data is stored in an `autoarena.duckdb` file in the directory where you invoked AutoArena.

## Development

AutoArena uses [uv](https://github.com/astral-sh/uv) to manage dependencies. To set up this repository for development,
run:

```shell
uv venv && source .venv/bin/activate
uv pip install --all-extras -r pyproject.toml
uv tool run pre-commit install
uv run python3 -m autoarena --dev
```

To run AutoArena for development, you will need to run both the backend and frontend service:

- Backend: `uv run python3 -m autoarena --dev` (the `--dev`/`-d` flag enables automatic service reloading when
    source files change)
- Frontend: see [`ui/README.md`](./ui/README.md)

To build a release tarball in the `./dist` directory:

```
./scripts/build.sh
```
