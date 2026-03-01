"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { useToast } from "@/components/ui/Toast";
import { formatDateTime } from "@/lib/utils";

interface Proposal {
  id: number;
  agentName: string;
  proposalType: string;
  title: string;
  summary: string | null;
  status: string;
  createdAt: string;
  feedback: string | null;
}

const COLUMNS = [
  { status: "pending_review", label: "ממתין לאישור", color: "#f0ad4e" },
  { status: "approved", label: "מאושר", color: "#4caf50" },
  { status: "executing", label: "בביצוע", color: "#2196f3" },
  { status: "completed", label: "הושלם", color: "#8bc34a" },
];

export default function ProposalsPage() {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [selected, setSelected] = useState<Proposal | null>(null);
  const [feedback, setFeedback] = useState("");
  const { showToast } = useToast();

  const load = () => {
    fetch("/api/proposals").then((r) => r.json()).then((d) => d.success && setProposals(d.proposals)).catch(() => {});
  };

  useEffect(() => { load(); }, []);

  const updateStatus = async (id: number, status: string, fb?: string) => {
    try {
      const res = await fetch(`/api/proposals/${id}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status, feedback: fb }),
      });
      const data = await res.json();
      if (data.success) { showToast("סטטוס עודכן"); setSelected(null); load(); }
      else showToast(data.error || "שגיאה", "error");
    } catch { showToast("שגיאה בחיבור", "error"); }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-[1.75rem] font-bold flex items-center gap-2">
          <i className="fas fa-clipboard-check text-accent" /> הצעות
        </h1>
        <p className="text-text-secondary mt-1">אישור והפעלת הצעות מסוכנים</p>
      </div>

      <div className="grid grid-cols-4 gap-4 min-h-[500px] max-lg:grid-cols-2 max-md:grid-cols-1">
        {COLUMNS.map((col) => {
          const items = proposals.filter((p) => p.status === col.status);
          return (
            <div key={col.status} className="bg-bg rounded-DEFAULT p-4 border border-border-light">
              <div className="font-semibold text-[.85rem] mb-3 pb-2 border-b-2 border-border flex justify-between items-center">
                {col.label}
                <span className="bg-border px-2 py-0.5 rounded-full text-[.7rem] text-text-secondary">{items.length}</span>
              </div>
              {items.map((p) => (
                <div
                  key={p.id}
                  onClick={() => setSelected(p)}
                  className="bg-card-bg rounded-sm p-4 mb-3 shadow-card border border-border-light cursor-pointer hover:shadow-card-md transition-shadow"
                >
                  <h4 className="text-[.9rem] font-semibold mb-1">{p.title}</h4>
                  <p className="text-[.78rem] text-text-secondary mb-2 line-clamp-2">{p.summary}</p>
                  <div className="flex justify-between items-center text-[.72rem] text-text-secondary">
                    <Badge status={p.proposalType} label={p.proposalType} />
                    <span>{p.agentName}</span>
                  </div>
                </div>
              ))}
              {items.length === 0 && (
                <p className="text-center text-text-secondary text-[.82rem] py-8 opacity-50">אין הצעות</p>
              )}
            </div>
          );
        })}
      </div>

      {/* Detail Modal */}
      <Modal open={!!selected} onClose={() => setSelected(null)} title={selected?.title ?? ""} large>
        {selected && (
          <div>
            <div className="flex gap-3 mb-4">
              <Badge status={selected.status} />
              <Badge status={selected.proposalType} label={selected.proposalType} />
              <span className="text-[.8rem] text-text-secondary">{formatDateTime(selected.createdAt)}</span>
            </div>
            <p className="text-[.9rem] mb-4">{selected.summary}</p>

            {selected.status === "pending_review" && (
              <div className="border-t border-border pt-4 mt-4">
                <textarea
                  placeholder="הערות / פידבק (אופציונלי)..."
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-sm text-[.9rem] mb-4 min-h-[80px]"
                />
                <div className="flex gap-3 justify-end">
                  <Button variant="danger" onClick={() => updateStatus(selected.id, "rejected", feedback)}>
                    דחה
                  </Button>
                  <Button variant="secondary" onClick={() => updateStatus(selected.id, "revision_requested", feedback)}>
                    בקש תיקון
                  </Button>
                  <Button variant="success" onClick={() => updateStatus(selected.id, "approved")}>
                    אשר
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
