# Cloud.ru AI for EONVERSE (optional)

EONVERSE keeps its deterministic Python simulation as the authority. Cloud.ru
can give one resident a limited recommendation every 120 ticks. The recommendation
may adjust a *memory preference* only; it cannot mint resources, move residents,
override laws or call external tools.

## Setup

Create a Foundation Models API key in Cloud.ru, then set these environment variables
in the server's operating environment (never commit credentials):

- `EONVERSE_AI_ENABLED=1`
- `CLOUDRU_API_KEY=<your secret>`
- `CLOUDRU_MODEL=<exact model ID returned by Cloud.ru /v1/models>`

The user-preferred model is DeepSeek-V4-Flash; **verify it is actually offered in
your account and copy its exact model ID**. Do not silently substitute V4-Pro
or a different model.

The server connects to the official
`https://foundation-models.api.cloud.ru/v1/chat/completions` endpoint with
Bearer authentication. See the [Cloud.ru API specification](https://cloud.ru/docs/foundation-models/ug/topics/api-ref__specs).

## Operational controls

- Default OFF until enabled with credentials and a model ID.
- Maximum 60 Cloud.ru requests per server session.
- At most one new request per 120 simulation ticks (normally 120 seconds).
- Each call has a 12-second network timeout and a 15-second async watchdog.
- Cloud requests run outside the world step; errors fall back to normal Python AI.
- No API key is persisted to a world save, logged, or exposed via the web API.
- The current integration is an initial bounded reasoning hook, **not** free-form
  intelligence or autonomous code execution.
- Real usage costs, actual model availability, long-running performance and
  credential authentication require live verification in your Cloud.ru account.
