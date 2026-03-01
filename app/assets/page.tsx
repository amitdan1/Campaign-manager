"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { FiltersCard } from "@/components/ui/FiltersCard";
import { EmptyState } from "@/components/ui/EmptyState";
import { useToast } from "@/components/ui/Toast";

interface Asset {
  id: number;
  assetType: string;
  source: string;
  url: string;
  assetMetadata: Record<string, unknown> | null;
  createdAt: string;
}

export default function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const { showToast } = useToast();

  const loadAssets = () => {
    const params = new URLSearchParams();
    if (filters.source) params.set("source", filters.source);
    if (filters.type) params.set("type", filters.type);
    fetch(`/api/assets?${params}`).then((r) => r.json()).then((d) => d.success && setAssets(d.assets)).catch(() => {});
  };

  useEffect(() => { loadAssets(); }, [filters]);

  const scrape = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/assets/scrape", { method: "POST" });
      const data = await res.json();
      showToast(data.success ? `נסרקו ${data.saved ?? 0} נכסים חדשים` : "שגיאה בסריקה", data.success ? "success" : "error");
      if (data.success) loadAssets();
    } catch { showToast("שגיאה בחיבור", "error"); }
    setLoading(false);
  };

  return (
    <div>
      <div className="mb-8 flex justify-between items-start flex-wrap gap-4">
        <div>
          <h1 className="text-[1.75rem] font-bold flex items-center gap-2">
            <i className="fas fa-images text-accent" /> נכסי מותג
          </h1>
          <p className="text-text-secondary mt-1">תמונות ותוכן שנאספו מהמותג</p>
        </div>
        <Button icon="search" onClick={scrape} disabled={loading}>
          {loading ? "סורק..." : "סרוק נכסים"}
        </Button>
      </div>

      <FiltersCard
        filters={[
          { key: "source", label: "מקור", options: [{ value: "", label: "הכל" }, { value: "website", label: "אתר" }, { value: "instagram", label: "Instagram" }, { value: "facebook", label: "Facebook" }] },
          { key: "type", label: "סוג", options: [{ value: "", label: "הכל" }, { value: "image", label: "תמונה" }, { value: "text", label: "טקסט" }, { value: "video", label: "וידאו" }] },
        ]}
        values={filters}
        onChange={(k, v) => setFilters((p) => ({ ...p, [k]: v }))}
      />

      {assets.length === 0 ? (
        <EmptyState icon="images" title="אין נכסי מותג" description="לחצו על 'סרוק נכסים' לסריקת האתר" />
      ) : (
        <div className="grid grid-cols-[repeat(auto-fill,minmax(180px,1fr))] gap-4">
          {assets.map((a) => (
            <div key={a.id} className="rounded-sm overflow-hidden border border-border-light bg-card-bg hover:shadow-card-md transition-shadow">
              {a.assetType === "image" && (
                <img src={a.url} alt="" className="w-full h-[140px] object-cover" loading="lazy" />
              )}
              <div className="p-2.5 text-[.78rem] text-text-secondary">
                <span className="bg-bg px-1.5 py-0.5 rounded text-[.7rem]">{a.source}</span>
                <span className="mr-2 bg-bg px-1.5 py-0.5 rounded text-[.7rem]">{a.assetType}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
