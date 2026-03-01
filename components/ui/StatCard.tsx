interface StatCardProps {
  icon: string;
  iconBg: string;
  value: string | number;
  label: string;
  trend?: { value: string; positive: boolean } | null;
}

export function StatCard({ icon, iconBg, value, label, trend }: StatCardProps) {
  return (
    <div className="bg-card-bg rounded-DEFAULT p-5 shadow-card border border-border-light flex items-center gap-4 hover:shadow-card-md transition-shadow">
      <div
        className="w-12 h-12 rounded-sm flex items-center justify-center text-white text-xl shrink-0"
        style={{ background: iconBg }}
      >
        <i className={`fas fa-${icon}`} />
      </div>
      <div>
        <h3 className="text-[1.6rem] font-bold leading-tight text-text-primary">
          {value}
        </h3>
        <p className="text-[.8rem] text-text-secondary">{label}</p>
        {trend && (
          <span
            className={`text-[.78rem] mt-0.5 inline-block ${
              trend.positive ? "text-status-approved" : "text-status-rejected"
            }`}
          >
            {trend.value}
          </span>
        )}
      </div>
    </div>
  );
}
