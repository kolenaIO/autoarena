# AutoArena

AutoArena helps you stack rank LLM outputs against one another using automated judge evaluation. Run with:

```
python3 -m autoarena
```

Data is stored in an `autoarena.duckdb` file on your local machine.

## Development

To set up this repository for development, run:

```shell
uv venv
uv pip install -r pyproject.toml
uv run pre-commit install
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
