"use client";

interface FilterOption {
  value: string;
  label: string;
}

interface FilterDef {
  key: string;
  label: string;
  options: FilterOption[];
}

interface FiltersCardProps {
  filters: FilterDef[];
  values: Record<string, string>;
  onChange: (key: string, value: string) => void;
}

export function FiltersCard({ filters, values, onChange }: FiltersCardProps) {
  return (
    <div className="bg-card-bg rounded-DEFAULT px-5 py-4 mb-6 shadow-card border border-border-light flex gap-6 flex-wrap items-center">
      {filters.map((f) => (
        <div key={f.key} className="flex items-center gap-1.5 text-[.85rem]">
          <label className="font-semibold text-text-secondary text-[.8rem]">
            {f.label}
          </label>
          <select
            value={values[f.key] ?? ""}
            onChange={(e) => onChange(f.key, e.target.value)}
            className="px-2.5 py-1.5 border border-border rounded-sm text-[.85rem] bg-card-bg"
          >
            {f.options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      ))}
    </div>
  );
}
