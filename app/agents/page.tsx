"use client";

import { useEffect, useState } from "react";

interface AgentStatus {
  healthy: boolean;
  agents: Record<string, { healthy: boolean; totalLeads?: number }>;
}

const AGENT_DEFS = [
  { id: "leadCapture", name: "Lead Capture", icon: "user-plus", desc: "קליטת לידים מכל המקורות, וולידציה, ודדופליקציה" },
  { id: "leadScoring", name: "Lead Scoring", icon: "star", desc: "ציון איכות לידים על בסיס AI או חוקים" },
  { id: "funnelAutomation", name: "Funnel Automation", icon: "filter", desc: "אוטומציית מייל, וואטסאפ ומעקב" },
  { id: "campaignTracking", name: "Campaign Tracking", icon: "chart-line", desc: "שליפת מטריקות מגוגל ופייסבוק" },
  { id: "content", name: "Content Agent", icon: "pen-fancy", desc: "יצירת תוכן שיווקי, מודעות ואימיילים" },
  { id: "strategy", name: "Strategy Agent", icon: "lightbulb", desc: "תכנון אסטרטגיה שבועית" },
  { id: "landingPage", name: "Landing Page Agent", icon: "file-alt", desc: "יצירת דפי נחיתה" },
  { id: "brandScraper", name: "Brand Scraper", icon: "search", desc: "סריקת אתר ורשתות חברתיות לנכסי מותג" },
  { id: "budgetOptimizer", name: "Budget Optimizer", icon: "balance-scale", desc: "אופטימיזציית תקציב והמלצות" },
  { id: "campaignManager", name: "Campaign Manager", icon: "bullhorn", desc: "יצירת הצעות קמפיינים" },
];

export default function AgentsPage() {
  const [status, setStatus] = useState<AgentStatus | null>(null);

  useEffect(() => {
    fetch("/api/agents/status").then((r) => r.json()).then(setStatus).catch(() => {});
  }, []);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-[1.75rem] font-bold flex items-center gap-2">
          <i className="fas fa-robot text-accent" /> סוכנים
        </h1>
        <p className="text-text-secondary mt-1">סטטוס ובריאות סוכני המערכת</p>
      </div>

      <div className="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-4">
        {AGENT_DEFS.map((agent) => {
          const agentHealth = status?.agents?.[agent.id];
          const healthy = agentHealth?.healthy ?? true;
          return (
            <div key={agent.id} className="bg-card-bg rounded-DEFAULT p-5 shadow-card border border-border-light">
              <h4 className="text-[.95rem] font-semibold mb-2 flex items-center gap-2">
                <i className={`fas fa-${agent.icon} text-accent`} />
                {agent.name}
                <span className={`inline-block w-2 h-2 rounded-full mr-1.5 ${healthy ? "bg-status-approved" : "bg-status-rejected"}`} />
              </h4>
              <p className="text-[.82rem] text-text-secondary">{agent.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
