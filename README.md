# AutoArena

AutoArena helps you stack rank LLM outputs against one another using automated judge evaluation.

Install from [PyPI](https://pypi.org/project/autoarena/) and run with:

```
pip install autoarena
python -m autoarena
```

## Usage

Getting started with AutoArena is simple:

1. Run AutoArena via `python -m autoarena` and visit [localhost:8899](http://localhost:8899/) in your browser.
2. Create a project via the UI.
3. Add responses from a model by selecting a CSV file with `prompt` and `response` columns.
4. Configure an automated judge via the UI. Note that most judges require credentials, e.g. `X_API_KEY` in the
   environment where you're running AutoArena.
5. Add responses from a second model to kick off an automated judging task using the judges you configured in the
   previous step to decide which of the models you've uploaded provided a better `response` to a given `prompt`.

That's it! After these steps you're fully set up for automated evaluation on AutoArena.

### Data Storage

Data is stored in `./data/<project>.duckdb` files in the directory where you invoked AutoArena. See
[`data/README.md`](./data/README.md) for more details on data storage in AutoArena.

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
