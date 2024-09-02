# autostack

TODO, EOD 8/31:

- [x] query error handling -- particularly queries that can fail, like:
    - deletion of a judge with ratings
    - adding a model with a duplicate name
- [x] creation of non-Ollama judge types: OpenAI, Anthropic, Cohere, Gemini
- [x] flow to create fine-tuned custom judge (placeholder)
- [ ] restarts of failed, crashed, or partial judge runs
- [x] delete a model
- [x] view the responses submitted by a model
- [x] download a model's responses from the UI
- [x] view existing votes on h2h matchups
- [ ] tests for tricky queries and calculations
