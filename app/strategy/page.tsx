"use client";

import { config } from "@/lib/config";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useState } from "react";
import { useToast } from "@/components/ui/Toast";

export default function StrategyPage() {
  const [loading, setLoading] = useState(false);
  const { showToast } = useToast();

  const runWeekly = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/pipeline/weekly", { method: "POST" });
      const data = await res.json();
      showToast(data.success ? "תוכנית שבועית נוצרה בהצלחה" : "שגיאה ביצירת תוכנית", data.success ? "success" : "error");
    } catch { showToast("שגיאה בחיבור לשרת", "error"); }
    setLoading(false);
  };

  return (
    <div>
      <div className="mb-8 flex justify-between items-start flex-wrap gap-4">
        <div>
          <h1 className="text-[1.75rem] font-bold flex items-center gap-2">
            <i className="fas fa-lightbulb text-accent" /> אסטרטגיה
          </h1>
          <p className="text-text-secondary mt-1">תקציב, קהל יעד ואסטרטגיית שיווק</p>
        </div>
        <Button icon="play" onClick={runWeekly} disabled={loading}>
          {loading ? "מייצר..." : "צור תוכנית שבועית"}
        </Button>
      </div>

      {/* Budget */}
      <Card title="תקציב חודשי">
        <div className="grid gap-4">
          {[
            { label: "סה\"כ תקציב", amount: config.budget.total, color: "#c9a96e" },
            { label: "Google Ads", amount: config.budget.googleAds, color: "#4285f4" },
            { label: "Facebook/Instagram", amount: config.budget.facebook, color: "#1877f2" },
          ].map((b) => (
            <div key={b.label} className="p-5 bg-bg rounded-sm border-r-[3px]" style={{ borderColor: b.color }}>
              <div className="font-semibold text-text-primary mb-1">{b.label}</div>
              <div className="text-[1.4rem] font-bold" style={{ color: b.color }}>₪{b.amount.toLocaleString()}</div>
            </div>
          ))}
        </div>
      </Card>

      {/* Target Audience */}
      <Card title="קהל יעד">
        <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-4">
          <div className="p-4 bg-bg rounded-sm">
            <label className="text-text-secondary text-[.8rem] block mb-1">גיל</label>
            <span className="font-semibold">{config.targets.ageMin}–{config.targets.ageMax}</span>
          </div>
          <div className="p-4 bg-bg rounded-sm">
            <label className="text-text-secondary text-[.8rem] block mb-1">מיקומים</label>
            <span className="font-semibold">{config.targets.locations.join(", ")}</span>
          </div>
          <div className="p-4 bg-bg rounded-sm">
            <label className="text-text-secondary text-[.8rem] block mb-1">תקציב פרויקט מינימלי</label>
            <span className="font-semibold">₪{config.targets.minProjectBudget.toLocaleString()}</span>
          </div>
        </div>
      </Card>

      {/* KPIs */}
      <Card title="יעדי KPI">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="bg-bg px-4 py-3 text-right font-semibold text-[.8rem] text-text-secondary border-b border-border-light">מדד</th>
              <th className="bg-bg px-4 py-3 text-right font-semibold text-[.8rem] text-text-secondary border-b border-border-light">יעד</th>
            </tr>
          </thead>
          <tbody>
            {[
              { label: "עלות לליד (CPL)", value: `₪${config.targets.cpl}` },
              { label: "שיעור ייעוץ", value: `${(config.targets.consultationRate * 100).toFixed(0)}%` },
              { label: "שיעור המרה", value: `${(config.targets.conversionRate * 100).toFixed(0)}%` },
              { label: "עלות רכישת לקוח (CAC)", value: `₪${config.targets.cac}` },
              { label: "ROAS", value: `${config.targets.roas}%` },
            ].map((kpi) => (
              <tr key={kpi.label} className="hover:bg-[#fdfcfa]">
                <td className="px-4 py-3 border-b border-border-light text-[.9rem]">{kpi.label}</td>
                <td className="px-4 py-3 border-b border-border-light text-[.9rem] font-semibold">{kpi.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
