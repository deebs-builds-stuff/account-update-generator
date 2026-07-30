# Account Update Generator

Turns raw account facts into a tone- and audience-tailored update, using the Claude API.

## Setup

```bash
cp .env.example .env
```

Edit `.env` and set `ANTHROPIC_API_KEY` to your own key.

```bash
source venv/bin/activate
python server.py
```

Open http://localhost:5050

## Notes

- Backend (`server.py`) holds the API key server-side and calls Claude; the frontend never sees it.
- No database — each generation is a one-off, nothing persists between sessions.
- Renewal dates within 90–120 days are automatically flagged in the generated update.
