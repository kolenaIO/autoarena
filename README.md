# AutoStack

AutoStack helps you stack rank LLM outputs against one another using automated judge evaluation. Run with:

```
python3 -m autostack
```

Data is stored in an `autostack.duckdb` file on your local machine.

## Development

To set up this repository for development, run:

```shell
poetry update && poetry install
poerty run pre-commit install
poetry run python3 -m autostack
```

To run AutoStack for development, you will need to run both the backend and frontend service:

- Backend: `poetry run python3 -m autostack --dev` (the `--dev`/`-d` flag enables automatic service reloading when
    source files change)
- Frontend: see [`ui/README.md`](./ui/README.md)

To build a release tarball in the `./dist` directory:

```
./scripts/build.sh
```
