"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Row = Record<string, number | string>;

const COLORS = ["#0a7d28", "#2563eb", "#b00020", "#9333ea", "#d97706"];

export default function TrendChart({
  data,
  metrics,
}: {
  data: Row[];
  metrics: string[];
}) {
  return (
    <ResponsiveContainer width="100%" height={420}>
      <LineChart data={data} margin={{ top: 16, right: 24, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" />
        <YAxis domain={[0, 1]} />
        <Tooltip />
        <Legend />
        {metrics.map((metric, i) => (
          <Line
            key={metric}
            type="monotone"
            dataKey={metric}
            stroke={COLORS[i % COLORS.length]}
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
