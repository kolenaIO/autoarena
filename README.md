# AutoStack

```shell
poetry update && poetry install
poerty run pre-commit install
poetry run python3 -m autostack
```

To run AutoStack locally, you will need to run both the backend and frontend service:

- Backend: `poetry run python3 -m autostack`
- Frontend: see [`ui/README.md`](./ui/README.md)

To build a release:

```
./scripts/build.sh
```

## Development

Highest priority TODOs as of EOD 9/2:

- [ ] Add tests for tricky SQL logic and Elo calculations
- [ ] Plug in real fine-tuning service with a way to monitor progress and run fine-tuned judge model
- [ ] Settle naming: model, result, judge, head-to-head (with and without judgement)
- [ ] Support multi-turn conversations (accept lists in prompt and response columns?)
- [ ] Better head-to-head surfacing: show samples where other judges disagree?
- [ ] Responsive layout (pages are currently fixed at 1080px content width)
- [ ] Programmatic interface to upload, download, extend (?)
- [x] Lightweight judge resolver to turn e.g. "Option B is better." into "B" (some judges are verbose despite prompting)
- [ ] View responses from other models on head-to-head tab (click to see other responses to prompt)
- [x] Configure judge system prompt (persist, set default, add to frontend)
- [x] Set up backend logger
- [ ] Improve off-happy-path for automated judges, such as Ollama not running or API key missing
