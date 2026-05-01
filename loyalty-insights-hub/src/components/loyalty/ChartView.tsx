import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend,
} from "recharts";
import type { ChartSpec } from "@/api/client";

const COLORS = ["#4F8EF7", "#F7874F", "#4FF7A0", "#F74F6E", "#A04FF7", "#F7D44F"];

const tooltipStyle = {
  backgroundColor: "#1a1d27",
  border: "1px solid #2a2d3a",
  borderRadius: 6,
  color: "#fff",
};

export function ChartView({ spec, data }: { spec: ChartSpec; data: Record<string, unknown>[] }) {
  if (!spec || spec.chart === "none" || !data?.length) return null;

  const title = "title" in spec ? spec.title : undefined;

  return (
    <div className="mt-3 rounded-lg border border-[var(--la-border)] bg-[#0f1117] p-3">
      {title && <div className="text-sm font-bold text-white mb-2">{title}</div>}
      <div style={{ width: "100%", height: 280 }}>
        <ResponsiveContainer>
          {spec.chart === "bar" ? (
            <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
              <CartesianGrid stroke="#2a2d3a" strokeDasharray="3 3" />
              <XAxis dataKey={spec.x} stroke="#8b8fa8" tick={{ fill: "#8b8fa8", fontSize: 11 }} />
              <YAxis stroke="#8b8fa8" tick={{ fill: "#8b8fa8", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey={spec.y} fill="#4F8EF7" />
            </BarChart>
          ) : spec.chart === "line" ? (
            <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
              <CartesianGrid stroke="#2a2d3a" strokeDasharray="3 3" />
              <XAxis dataKey={spec.x} stroke="#8b8fa8" tick={{ fill: "#8b8fa8", fontSize: 11 }} />
              <YAxis stroke="#8b8fa8" tick={{ fill: "#8b8fa8", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey={spec.y} stroke="#4F8EF7" strokeWidth={2} dot={{ fill: "#4F8EF7" }} />
            </LineChart>
          ) : (
            <PieChart>
              <Pie
                data={data}
                dataKey={spec.values}
                nameKey={spec.names}
                cx="50%"
                cy="50%"
                outerRadius={90}
                label
              >
                {data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ color: "#8b8fa8" }} />
            </PieChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
