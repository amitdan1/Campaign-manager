"use client";

import { useEffect, useState, useCallback } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { FormGroup, Input, Select, Textarea } from "@/components/ui/FormGroup";
import { DataTable } from "@/components/ui/DataTable";
import { Badge } from "@/components/ui/Badge";
import { FiltersCard } from "@/components/ui/FiltersCard";
import { useToast } from "@/components/ui/Toast";
import { formatDate } from "@/lib/utils";

interface Lead {
  id: string;
  name: string;
  phone: string;
  email: string;
  source: string;
  status: string;
  qualityScore: number | null;
  location: string | null;
  budget: string | null;
  projectType: string | null;
  createdAt: string;
}

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [showAdd, setShowAdd] = useState(false);
  const [showStatus, setShowStatus] = useState<Lead | null>(null);
  const { showToast } = useToast();

  const loadLeads = useCallback(() => {
    const params = new URLSearchParams();
    if (filters.status) params.set("status", filters.status);
    if (filters.source) params.set("source", filters.source);
    fetch(`/api/leads?${params}`).then((r) => r.json()).then((d) => d.success && setLeads(d.leads)).catch(() => {});
  }, [filters]);

  useEffect(() => { loadLeads(); }, [loadLeads]);

  const addLead = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const body = Object.fromEntries(fd.entries());
    try {
      const res = await fetch("/api/leads", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const data = await res.json();
      if (data.success) { showToast("ליד נוסף בהצלחה"); setShowAdd(false); loadLeads(); }
      else showToast(data.message || "שגיאה", "error");
    } catch { showToast("שגיאה בחיבור", "error"); }
  };

  const updateStatus = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!showStatus) return;
    const fd = new FormData(e.currentTarget);
    try {
      const res = await fetch(`/api/leads/${showStatus.id}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: fd.get("status"), notes: fd.get("notes") }),
      });
      const data = await res.json();
      if (data.success) { showToast("סטטוס עודכן"); setShowStatus(null); loadLeads(); }
      else showToast("שגיאה בעדכון", "error");
    } catch { showToast("שגיאה בחיבור", "error"); }
  };

  return (
    <div>
      <div className="mb-8 flex justify-between items-start flex-wrap gap-4">
        <div>
          <h1 className="text-[1.75rem] font-bold flex items-center gap-2">
            <i className="fas fa-users text-accent" /> לידים
          </h1>
          <p className="text-text-secondary mt-1">ניהול לידים ומעקב</p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary" icon="download" onClick={() => window.open("/api/export/leads?format=csv")}>ייצוא CSV</Button>
          <Button icon="plus" onClick={() => setShowAdd(true)}>הוסף ליד</Button>
        </div>
      </div>

      <FiltersCard
        filters={[
          { key: "status", label: "סטטוס", options: [{ value: "", label: "הכל" }, { value: "new", label: "חדש" }, { value: "contacted", label: "נוצר קשר" }, { value: "qualified", label: "מתאים" }, { value: "consultation_booked", label: "נקבע ייעוץ" }, { value: "converted", label: "הומר" }, { value: "lost", label: "אבוד" }] },
          { key: "source", label: "מקור", options: [{ value: "", label: "הכל" }, { value: "google", label: "Google" }, { value: "facebook", label: "Facebook" }, { value: "instagram", label: "Instagram" }, { value: "organic", label: "אורגני" }, { value: "manual", label: "ידני" }] },
        ]}
        values={filters}
        onChange={(k, v) => setFilters((p) => ({ ...p, [k]: v }))}
      />

      <Card noPadding>
        <DataTable
          data={leads as unknown as Record<string, unknown>[]}
          keyField="id"
          onRowClick={(r) => setShowStatus(r as unknown as Lead)}
          emptyMessage="אין לידים להצגה"
          columns={[
            { key: "name", header: "שם" },
            { key: "phone", header: "טלפון", className: "ltr-input" },
            { key: "source", header: "מקור", render: (r) => <Badge status={r.source as string} /> },
            { key: "status", header: "סטטוס", render: (r) => <Badge status={r.status as string} /> },
            { key: "qualityScore", header: "ציון", render: (r) => r.qualityScore != null ? <Badge status="score" label={String(r.qualityScore)} /> : "—" },
            { key: "createdAt", header: "תאריך", render: (r) => formatDate(r.createdAt as string) },
          ]}
        />
      </Card>

      {/* Add Lead Modal */}
      <Modal open={showAdd} onClose={() => setShowAdd(false)} title="הוסף ליד חדש">
        <form onSubmit={addLead}>
          <div className="grid grid-cols-2 gap-4">
            <FormGroup label="שם" required><Input name="name" required /></FormGroup>
            <FormGroup label="טלפון" required><Input name="phone" required className="ltr-input" /></FormGroup>
          </div>
          <FormGroup label="אימייל"><Input name="email" type="email" className="ltr-input" /></FormGroup>
          <div className="grid grid-cols-2 gap-4">
            <FormGroup label="מקור">
              <Select name="source"><option value="manual">ידני</option><option value="google">Google</option><option value="facebook">Facebook</option><option value="instagram">Instagram</option><option value="organic">אורגני</option></Select>
            </FormGroup>
            <FormGroup label="סוג פרויקט">
              <Select name="projectType"><option value="">—</option><option value="villa">וילה</option><option value="new_build">בנייה חדשה</option><option value="renovation">שיפוץ</option><option value="penthouse">פנטהאוז</option></Select>
            </FormGroup>
          </div>
          <FormGroup label="הערות"><Textarea name="notes" /></FormGroup>
          <div className="flex justify-end gap-3 mt-5">
            <Button variant="secondary" type="button" onClick={() => setShowAdd(false)}>ביטול</Button>
            <Button type="submit">שמור</Button>
          </div>
        </form>
      </Modal>

      {/* Status Update Modal */}
      <Modal open={!!showStatus} onClose={() => setShowStatus(null)} title={`עדכון סטטוס — ${showStatus?.name ?? ""}`}>
        <form onSubmit={updateStatus}>
          <FormGroup label="סטטוס חדש" required>
            <Select name="status" defaultValue={showStatus?.status}>
              <option value="new">חדש</option><option value="contacted">נוצר קשר</option><option value="qualified">מתאים</option>
              <option value="consultation_booked">נקבע ייעוץ</option><option value="converted">הומר</option><option value="lost">אבוד</option>
            </Select>
          </FormGroup>
          <FormGroup label="הערות"><Textarea name="notes" /></FormGroup>
          <div className="flex justify-end gap-3 mt-5">
            <Button variant="secondary" type="button" onClick={() => setShowStatus(null)}>ביטול</Button>
            <Button type="submit">עדכן</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
