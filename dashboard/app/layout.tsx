import type { ReactNode } from "react";

export const metadata = {
  title: "LLM Eval Dashboard",
  description: "Metric trends over time from lleval run history.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body
        style={{
          fontFamily: "system-ui, sans-serif",
          margin: 0,
          padding: "2rem",
          color: "#1a1a1a",
        }}
      >
        {children}
      </body>
    </html>
  );
}
