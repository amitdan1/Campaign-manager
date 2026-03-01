"use client";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Bar, Doughnut, Line } from "react-chartjs-2";
import type { ChartData, ChartOptions } from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler
);

const defaultOptions: ChartOptions<"bar"> & ChartOptions<"line"> & ChartOptions<"doughnut"> = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      rtl: true,
      position: "top" as const,
      labels: { font: { family: "Inter" } },
    },
  },
} as never;

interface ChartCardProps {
  title: string;
  type: "bar" | "line" | "doughnut";
  data: ChartData<"bar"> | ChartData<"line"> | ChartData<"doughnut">;
  options?: Record<string, unknown>;
  className?: string;
}

export function ChartCard({ title, type, data, options, className }: ChartCardProps) {
  const merged = { ...defaultOptions, ...options };

  return (
    <div
      className={`bg-card-bg rounded-DEFAULT p-6 shadow-card border border-border-light ${className ?? ""}`}
    >
      <h3 className="text-base text-text-primary mb-4 font-semibold">{title}</h3>
      <div className="max-h-[280px]">
        {type === "bar" && (
          <Bar data={data as ChartData<"bar">} options={merged as ChartOptions<"bar">} />
        )}
        {type === "line" && (
          <Line data={data as ChartData<"line">} options={merged as ChartOptions<"line">} />
        )}
        {type === "doughnut" && (
          <Doughnut data={data as ChartData<"doughnut">} options={merged as ChartOptions<"doughnut">} />
        )}
      </div>
    </div>
  );
}
