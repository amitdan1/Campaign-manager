"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { FormGroup, Input, Select } from "@/components/ui/FormGroup";
import { DataTable } from "@/components/ui/DataTable";
import { Badge } from "@/components/ui/Badge";
import { useToast } from "@/components/ui/Toast";
import { formatCurrency, formatPct } from "@/lib/utils";

interface Campaign {
  id: number;
  campaignId: string;
  campaignName: string;
  platform: string;
  date: string;
  impressions: number;
  clicks: number;
  conversions: number;
  cost: number;
  cpl: number;
  ctr: number;
  conversionRate: number;
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [showModal, setShowModal] = useState(false);
  const { showToast } = useToast();

  useEffect(() => {
    fetch("/api/campaigns").then((r) => r.json()).then((d) => d.success && setCampaigns(d.campaigns)).catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const body = {
      campaignId: fd.get("campaignId"),
      campaignName: fd.get("campaignName"),
      platform: fd.get("platform"),
      impressions: Number(fd.get("impressions")),
      clicks: Number(fd.get("clicks")),
      conversions: Number(fd.get("conversions")),
      cost: Number(fd.get("cost")),
    };
    try {
      const res = await fetch("/api/campaigns/metrics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (data.success) {
        showToast("מטריקות נוספו בהצלחה");
        setShowModal(false);
        fetch("/api/campaigns").then((r) => r.json()).then((d) => d.success && setCampaigns(d.campaigns));
      } else { showToast("שגיאה בהוספה", "error"); }
    } catch { showToast("שגיאה בחיבור", "error"); }
  };

  return (
    <div>
      <div className="mb-8 flex justify-between items-start flex-wrap gap-4">
        <div>
          <h1 className="text-[1.75rem] font-bold flex items-center gap-2">
            <i className="fas fa-bullhorn text-accent" /> קמפיינים
          </h1>
          <p className="text-text-secondary mt-1">ביצועי קמפיינים פרסומיים</p>
        </div>
        <Button icon="plus" onClick={() => setShowModal(true)}>הוסף מטריקות</Button>
      </div>

      <Card noPadding>
        <DataTable
          data={campaigns}
          keyField="id"
          emptyMessage="אין נתוני קמפיינים"
          columns={[
            { key: "campaignName", header: "קמפיין" },
            { key: "platform", header: "פלטפורמה", render: (r) => <Badge status={r.platform} label={r.platform} /> },
            { key: "impressions", header: "חשיפות", render: (r) => (r.impressions as number).toLocaleString() },
            { key: "clicks", header: "קליקים", render: (r) => (r.clicks as number).toLocaleString() },
            { key: "conversions", header: "המרות" },
            { key: "cost", header: "עלות", render: (r) => formatCurrency(r.cost as number) },
            { key: "cpl", header: "CPL", render: (r) => formatCurrency(r.cpl as number) },
            { key: "ctr", header: "CTR", render: (r) => formatPct(r.ctr as number) },
          ]}
        />
      </Card>

      <Modal open={showModal} onClose={() => setShowModal(false)} title="הוסף מטריקות קמפיין">
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-4">
            <FormGroup label="מזהה קמפיין" required><Input name="campaignId" required /></FormGroup>
            <FormGroup label="שם קמפיין" required><Input name="campaignName" required /></FormGroup>
          </div>
          <FormGroup label="פלטפורמה" required>
            <Select name="platform" required>
              <option value="google">Google</option>
              <option value="facebook">Facebook</option>
              <option value="instagram">Instagram</option>
            </Select>
          </FormGroup>
          <div className="grid grid-cols-2 gap-4">
            <FormGroup label="חשיפות"><Input name="impressions" type="number" defaultValue="0" /></FormGroup>
            <FormGroup label="קליקים"><Input name="clicks" type="number" defaultValue="0" /></FormGroup>
            <FormGroup label="המרות"><Input name="conversions" type="number" defaultValue="0" /></FormGroup>
            <FormGroup label="עלות (₪)"><Input name="cost" type="number" step="0.01" defaultValue="0" /></FormGroup>
          </div>
          <div className="flex justify-end gap-3 mt-5">
            <Button variant="secondary" type="button" onClick={() => setShowModal(false)}>ביטול</Button>
            <Button type="submit">שמור</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
