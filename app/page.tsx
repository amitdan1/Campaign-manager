"use client";

import { useEffect, useState } from "react";
import { StatCard } from "@/components/ui/StatCard";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ChartCard } from "@/components/charts/ChartWrapper";
import { formatCurrency, formatPct, formatDate } from "@/lib/utils";

interface DashboardStats {
  totalLeads: number;
  qualifiedLeads: number;
  consultations: number;
  conversions: number;
  totalSpend: number;
  avgCpl: number;
  consultationRate: number;
  conversionRate: number;
  cac: number;
  recentLeadsCount: number;
  leadsBySource: Record<string, number>;
  statusBreakdown: Record<string, number>;
  trend: { leads: number; percentage: number };
  pendingProposals: number;
}

interface Recommendation {
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recs, setRecs] = useState<Recommendation[]>([]);

  useEffect(() => {
    fetch("/api/dashboard/stats")
      .then((r) => r.json())
      .then((d) => d.success && setStats(d.stats))
      .catch(() => {});

    fetch("/api/recommendations")
      .then((r) => r.json())
      .then((d) => d.success && setRecs(d.recommendations))
      .catch(() => {});
  }, []);

  const sourceColors: Record<string, string> = {
    google: "#4285f4",
    facebook: "#1877f2",
    instagram: "#e1306c",
    organic: "#8a8a8a",
    manual: "#c9a96e",
    website: "#2ecc71",
  };

  const statusLabels: Record<string, string> = {
    new: "חדש",
    contacted: "נוצר קשר",
    qualified: "מתאים",
    consultation_booked: "נקבע ייעוץ",
    converted: "הומר",
    lost: "אבוד",
  };

  const statusColors: Record<string, string> = {
    new: "#9b59b6",
    contacted: "#3498db",
    qualified: "#f39c12",
    consultation_booked: "#2ecc71",
    converted: "#27ae60",
    lost: "#95a5a6",
  };

  const priorityStyles: Record<string, string> = {
    high: "bg-[#ffebee] text-[#c62828]",
    medium: "bg-[#fff8e1] text-[#f57f17]",
    low: "bg-[#f5f5f5] text-[#757575]",
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-[1.75rem] font-bold flex items-center gap-2">
          <i className="fas fa-chart-pie text-accent" /> דשבורד
        </h1>
        <p className="text-text-secondary mt-1">סקירה כללית של ביצועי השיווק</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-4 mb-8">
        <StatCard
          icon="users" iconBg="#9b59b6"
          value={stats?.totalLeads ?? "—"}
          label="לידים חדשים (30 יום)"
          trend={stats?.trend ? { value: `${stats.trend.leads >= 0 ? "+" : ""}${stats.trend.leads} השבוע`, positive: stats.trend.leads >= 0 } : null}
        />
        <StatCard icon="bullhorn" iconBg="#3498db" value={stats?.pendingProposals ?? "—"} label="הצעות ממתינות" />
        <StatCard icon="shekel-sign" iconBg="#c9a96e" value={stats ? formatCurrency(stats.avgCpl) : "—"} label="עלות ממוצעת לליד" />
        <StatCard icon="chart-line" iconBg="#2ecc71" value={stats ? formatPct(stats.conversionRate) : "—"} label="שיעור המרה" />
      </div>

      {/* Charts */}
      {stats && (
        <div className="grid grid-cols-[repeat(auto-fit,minmax(380px,1fr))] gap-6 mb-8">
          <ChartCard
            title="לידים לפי מקור"
            type="doughnut"
            data={{
              labels: Object.keys(stats.leadsBySource),
              datasets: [{
                data: Object.values(stats.leadsBySource),
                backgroundColor: Object.keys(stats.leadsBySource).map((s) => sourceColors[s] ?? "#ccc"),
              }],
            }}
          />
          <ChartCard
            title="משפך לידים"
            type="bar"
            data={{
              labels: Object.keys(stats.statusBreakdown).map((s) => statusLabels[s] ?? s),
              datasets: [{
                label: "לידים",
                data: Object.values(stats.statusBreakdown),
                backgroundColor: Object.keys(stats.statusBreakdown).map((s) => statusColors[s] ?? "#ccc"),
              }],
            }}
          />
        </div>
      )}

      {/* Two-column: Recent Leads + Recommendations */}
      <div className="grid grid-cols-[repeat(auto-fit,minmax(380px,1fr))] gap-6">
        <Card title="מטריקות ביצוע">
          {stats ? (
            <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-5">
              {[
                { label: "סה\"כ הוצאה", value: formatCurrency(stats.totalSpend) },
                { label: "לידים מתאימים", value: String(stats.qualifiedLeads) },
                { label: "ייעוצים שנקבעו", value: String(stats.consultations) },
                { label: "שיעור ייעוץ", value: formatPct(stats.consultationRate) },
                { label: "לקוחות שהומרו", value: String(stats.conversions) },
                { label: "עלות רכישת לקוח", value: formatCurrency(stats.cac) },
              ].map((m) => (
                <div key={m.label} className="p-4 bg-bg rounded-sm">
                  <label className="block text-text-secondary text-[.8rem] mb-1">{m.label}</label>
                  <span className="text-[1.35rem] font-bold">{m.value}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="skeleton h-[200px] rounded-sm" />
          )}
        </Card>

        <Card title="המלצות">
          {recs.length > 0 ? (
            <div className="divide-y divide-border-light">
              {recs.map((r, i) => (
                <div key={i} className="py-3 flex gap-3 items-start first:pt-0 last:pb-0">
                  <span className={`px-2 py-0.5 rounded-sm text-[.7rem] font-bold uppercase shrink-0 ${priorityStyles[r.priority] ?? ""}`}>
                    {r.priority}
                  </span>
                  <div>
                    <strong className="block text-[.9rem] mb-0.5">{r.title}</strong>
                    <p className="text-text-secondary text-[.8rem]">{r.description}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-text-secondary text-[.85rem]">אין המלצות כרגע</p>
          )}
        </Card>
      </div>
    </div>
  );
}
