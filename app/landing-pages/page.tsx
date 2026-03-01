"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { FormGroup, Input } from "@/components/ui/FormGroup";
import { EmptyState } from "@/components/ui/EmptyState";
import { Badge } from "@/components/ui/Badge";
import { useToast } from "@/components/ui/Toast";
import { formatDate } from "@/lib/utils";

interface LPProposal {
  id: number;
  title: string;
  summary: string | null;
  content: string | null;
  status: string;
  createdAt: string;
}

function parseContent(raw: string | null): { html?: string } | null {
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

const VARIANTS = [
  { id: "hero_gallery", icon: "images", label: "Hero Gallery" },
  { id: "split_layout", icon: "columns", label: "Split Layout" },
  { id: "story_flow", icon: "stream", label: "Story Flow" },
];

const statusLabels: Record<string, string> = {
  pending_review: "ממתין לאישור",
  approved: "מאושר",
  executing: "בביצוע",
  completed: "הושלם",
};

export default function LandingPagesPage() {
  const [pages, setPages] = useState<LPProposal[]>([]);
  const [showGen, setShowGen] = useState(false);
  const [variant, setVariant] = useState("hero_gallery");
  const [preview, setPreview] = useState<string | null>(null);
  const [device, setDevice] = useState<"desktop" | "tablet" | "mobile">("desktop");
  const [loading, setLoading] = useState(false);
  const { showToast } = useToast();

  useEffect(() => {
    fetch("/api/proposals?proposal_type=landing_page")
      .then((r) => r.json())
      .then((d) => d.success && setPages(d.proposals))
      .catch(() => {});
  }, []);

  const generate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    const fd = new FormData(e.currentTarget);
    try {
      const res = await fetch("/api/landing-pages/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ campaignName: fd.get("campaignName"), variant }),
      });
      const data = await res.json();
      if (data.success && data.html) {
        showToast("דף נחיתה נוצר!");
        setShowGen(false);
        setPreview(data.html);
      } else showToast("שגיאה ביצירה", "error");
    } catch { showToast("שגיאה בחיבור", "error"); }
    setLoading(false);
  };

  const deviceWidths = { desktop: "100%", tablet: "768px", mobile: "375px" };

  return (
    <div>
      <div className="mb-8 flex justify-between items-start flex-wrap gap-4">
        <div>
          <h1 className="text-[1.75rem] font-bold flex items-center gap-2">
            <i className="fas fa-file-alt text-accent" /> דפי נחיתה
          </h1>
          <p className="text-text-secondary mt-1">יצירת וניהול דפי נחיתה</p>
        </div>
        <Button icon="plus" onClick={() => setShowGen(true)}>צור דף נחיתה</Button>
      </div>

      {pages.length === 0 && !preview ? (
        <EmptyState icon="file-alt" title="אין דפי נחיתה" description="לחצו 'צור דף נחיתה' ליצירת דף חדש" />
      ) : (
        <div className="grid grid-cols-[repeat(auto-fill,minmax(340px,1fr))] gap-6">
          {pages.map((p) => {
            const content = parseContent(p.content);
            return (
              <div key={p.id} className="bg-card-bg rounded-DEFAULT overflow-hidden border border-border-light hover:shadow-card-md transition-shadow group">
                {/* Thumbnail preview via scaled iframe */}
                <div className="h-[220px] bg-[#f5f0e8] relative overflow-hidden">
                  {content?.html ? (
                    <iframe
                      srcDoc={content.html}
                      className="absolute top-0 left-0 pointer-events-none border-none"
                      style={{
                        width: "1440px",
                        height: "900px",
                        transform: "scale(0.236)",
                        transformOrigin: "top left",
                      }}
                      tabIndex={-1}
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full text-text-secondary">
                      <i className="fas fa-file-alt text-4xl opacity-30" />
                    </div>
                  )}
                  {/* Hover overlay */}
                  {content?.html && (
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                      <button
                        onClick={() => setPreview(content.html!)}
                        className="bg-white text-text-primary px-4 py-2 rounded-sm font-semibold text-[.85rem] shadow-lg hover:bg-accent hover:text-white transition-colors"
                      >
                        <i className="fas fa-eye ml-1.5" />
                        תצוגה מקדימה
                      </button>
                    </div>
                  )}
                </div>

                <div className="p-5">
                  <h3 className="font-semibold mb-1 text-[1rem]">{p.title}</h3>
                  <p className="text-[.82rem] text-text-secondary mb-3 line-clamp-2">{p.summary}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex gap-2 items-center">
                      <Badge status={p.status} label={statusLabels[p.status] ?? p.status} />
                    </div>
                    <span className="text-[.75rem] text-text-secondary">{formatDate(p.createdAt)}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Generate Modal */}
      <Modal open={showGen} onClose={() => setShowGen(false)} title="צור דף נחיתה">
        <form onSubmit={generate}>
          <FormGroup label="שם קמפיין" required><Input name="campaignName" required /></FormGroup>
          <p className="text-[.85rem] font-semibold mb-3">בחר סגנון:</p>
          <div className="grid grid-cols-3 gap-4 mb-6">
            {VARIANTS.map((v) => (
              <div
                key={v.id}
                onClick={() => setVariant(v.id)}
                className={`p-4 border-2 rounded-sm cursor-pointer text-center transition-colors ${variant === v.id ? "border-accent bg-accent/5" : "border-border hover:border-accent/50"}`}
              >
                <i className={`fas fa-${v.icon} text-accent text-2xl block mb-2`} />
                <span className="text-[.82rem] font-semibold">{v.label}</span>
              </div>
            ))}
          </div>
          <div className="flex justify-end gap-3">
            <Button variant="secondary" type="button" onClick={() => setShowGen(false)}>ביטול</Button>
            <Button type="submit" disabled={loading}>{loading ? "מייצר..." : "צור"}</Button>
          </div>
        </form>
      </Modal>

      {/* Full Preview Overlay */}
      {preview && (
        <div className="fixed inset-0 z-[500] bg-sidebar-bg flex flex-col">
          <div className="flex justify-between items-center px-6 py-3 bg-[#111] border-b border-[#333] shrink-0">
            <h3 className="text-white text-[.9rem] font-semibold">
              <i className="fas fa-eye ml-2 text-accent" />
              תצוגה מקדימה
            </h3>
            <div className="flex gap-2">
              {(["desktop", "tablet", "mobile"] as const).map((d) => (
                <button
                  key={d}
                  onClick={() => setDevice(d)}
                  className={`px-3 py-1.5 border rounded text-[.78rem] cursor-pointer transition-colors ${device === d ? "border-accent text-accent bg-accent/10" : "border-[#555] text-[#aaa] bg-transparent"}`}
                >
                  <i className={`fas fa-${d === "desktop" ? "desktop" : d === "tablet" ? "tablet-alt" : "mobile-alt"} ml-1`} />
                  {d === "desktop" ? "דסקטופ" : d === "tablet" ? "טאבלט" : "מובייל"}
                </button>
              ))}
              <button onClick={() => setPreview(null)} className="px-4 py-1.5 border border-red-500/50 rounded text-red-400 cursor-pointer bg-transparent text-[.78rem] mr-4 hover:bg-red-500/10 transition-colors">
                <i className="fas fa-times ml-1" />
                סגור
              </button>
            </div>
          </div>
          <div className="flex-1 flex justify-center items-stretch p-6 bg-[#222] overflow-auto">
            <iframe
              srcDoc={preview}
              className="border-none bg-white rounded shadow-[0_0_40px_rgba(0,0,0,.4)] h-full transition-[width] duration-300"
              style={{ width: deviceWidths[device], maxWidth: device === "desktop" ? "1440px" : undefined }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
