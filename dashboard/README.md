# LLM Eval Dashboard

A Next.js 15 dashboard that charts `lleval` metric trends over time.

## Data

Reads `data/history.json` — an array of run records:

```json
[{ "timestamp": "2026-06-05", "aggregate": { "llm_judge": 0.66 } }]
```

Produce real history from the harness:

```bash
lleval run --config eval.yaml --history history.jsonl
```

`--history` appends one `{timestamp, aggregate}` line per run. Convert the JSONL
to the `data/history.json` array (or point the loader at your own source).

## Develop

```bash
cd dashboard
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
```

## Stack

Next.js 15 (App Router) · React 19 · Recharts · TypeScript.
