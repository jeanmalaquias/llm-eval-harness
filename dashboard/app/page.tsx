import history from "@/data/history.json";
import TrendChart from "./TrendChart";

type Run = { timestamp: string; aggregate: Record<string, number> };

export default function Page() {
  const runs = history as Run[];

  // Flatten each run into one row, and collect the metric names across runs.
  const metrics = Array.from(
    new Set(runs.flatMap((r) => Object.keys(r.aggregate))),
  ).sort();

  const data = runs.map((r) => ({ timestamp: r.timestamp, ...r.aggregate }));

  const latest = runs.at(-1);
  const first = runs[0];

  return (
    <main style={{ maxWidth: 960, margin: "0 auto" }}>
      <h1>LLM Eval Dashboard</h1>
      <p style={{ color: "#555" }}>
        Metric trends across {runs.length} eval runs. Feed it real data with{" "}
        <code>lleval run --history history.jsonl</code>.
      </p>

      <section
        style={{ display: "flex", gap: "1rem", flexWrap: "wrap", margin: "1rem 0" }}
      >
        {metrics.map((m) => {
          const now = latest?.aggregate[m] ?? 0;
          const then = first?.aggregate[m] ?? 0;
          const delta = now - then;
          return (
            <div
              key={m}
              style={{
                border: "1px solid #ddd",
                borderRadius: 8,
                padding: "0.75rem 1rem",
                minWidth: 160,
              }}
            >
              <div style={{ fontSize: 12, color: "#666" }}>{m}</div>
              <div style={{ fontSize: 24, fontWeight: 600 }}>{now.toFixed(3)}</div>
              <div style={{ color: delta >= 0 ? "#0a7d28" : "#b00020" }}>
                {delta >= 0 ? "▲" : "▼"} {Math.abs(delta).toFixed(3)} since start
              </div>
            </div>
          );
        })}
      </section>

      <TrendChart data={data} metrics={metrics} />
    </main>
  );
}
