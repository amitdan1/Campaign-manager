"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { useToast } from "@/components/ui/Toast";

interface Integration {
  name: string;
  key: string;
  connected: boolean;
  icon: string;
  description: string;
  fields: Array<{ key: string; label: string; required: boolean }>;
}

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string }>>({});
  const { showToast } = useToast();

  useEffect(() => {
    fetch("/api/integrations").then((r) => r.json()).then((d) => d.success && setIntegrations(d.integrations)).catch(() => {});
  }, []);

  const testConn = async (key: string) => {
    try {
      const res = await fetch("/api/integrations/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ integration: key }),
      });
      const data = await res.json();
      setTestResults((p) => ({ ...p, [key]: data }));
      showToast(data.success ? "חיבור תקין" : data.message, data.success ? "success" : "error");
    } catch { showToast("שגיאה בבדיקה", "error"); }
  };

  const connected = integrations.filter((i) => i.connected).length;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-[1.75rem] font-bold flex items-center gap-2">
          <i className="fas fa-plug text-accent" /> אינטגרציות
        </h1>
        <p className="text-text-secondary mt-1">חיבור שירותים חיצוניים</p>
      </div>

      <div className="flex gap-6 mb-6 flex-wrap">
        <div className="bg-card-bg rounded-DEFAULT px-6 py-3 shadow-card border border-border-light flex items-center gap-3">
          <span className="text-[1.4rem] font-bold text-accent">{connected}</span>
          <span className="text-[.85rem] text-text-secondary">מחוברים</span>
        </div>
        <div className="bg-card-bg rounded-DEFAULT px-6 py-3 shadow-card border border-border-light flex items-center gap-3">
          <span className="text-[1.4rem] font-bold text-text-secondary">{integrations.length - connected}</span>
          <span className="text-[.85rem] text-text-secondary">לא מחוברים</span>
        </div>
      </div>

      <div className="grid grid-cols-[repeat(auto-fill,minmax(420px,1fr))] gap-5 max-md:grid-cols-1">
        {integrations.map((integ) => (
          <div
            key={integ.key}
            className={`bg-card-bg rounded-DEFAULT shadow-card border border-border-light overflow-hidden hover:shadow-card-md transition-shadow ${integ.connected ? "border-t-[3px] border-t-status-approved" : "border-t-[3px] border-t-border"}`}
          >
            <div className="px-6 py-5 border-b border-border-light flex items-start gap-4">
              <div className="w-11 h-11 rounded-sm bg-bg flex items-center justify-center text-accent text-lg border border-border-light shrink-0">
                <i className={`fas fa-${integ.icon}`} />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-text-primary mb-0.5">{integ.name}</h3>
                <p className="text-[.8rem] text-text-secondary">{integ.description}</p>
              </div>
              <Badge status={integ.connected ? "connected" : "disconnected"} label={integ.connected ? "מחובר" : "לא מחובר"} />
            </div>

            <div className="px-6 py-4">
              {integ.fields.map((f) => (
                <div key={f.key} className="mb-3 last:mb-0">
                  <label className="block text-[.8rem] font-semibold text-text-secondary mb-1">
                    {f.label} {f.required && <span className="text-status-rejected">*</span>}
                  </label>
                  <input
                    type="password"
                    placeholder={`הגדר ב-Vercel Dashboard: ${f.key}`}
                    disabled
                    className="w-full px-3 py-2 border border-border rounded-sm text-[.85rem] bg-bg ltr-input opacity-60"
                  />
                </div>
              ))}
            </div>

            <div className="px-6 py-3 border-t border-border-light flex justify-between items-center">
              <span className="text-[.78rem] text-text-secondary">
                ערכים מוגדרים ב-Vercel Environment Variables
              </span>
              <Button size="sm" variant="secondary" icon="vial" onClick={() => testConn(integ.key)}>
                בדוק חיבור
              </Button>
            </div>

            {testResults[integ.key] && (
              <div className={`px-6 py-2.5 text-[.8rem] flex items-center gap-1.5 border-t border-border-light ${testResults[integ.key].success ? "bg-[#f1f8e9] text-[#33691e]" : "bg-[#fff3e0] text-[#e65100]"}`}>
                <i className={`fas fa-${testResults[integ.key].success ? "check-circle" : "exclamation-circle"}`} />
                {testResults[integ.key].message}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
