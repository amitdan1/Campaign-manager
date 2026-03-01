import { clsx } from "clsx";

const BADGE_STYLES: Record<string, string> = {
  new: "bg-[#e3f2fd] text-[#1565c0]",
  contacted: "bg-[#f3e5f5] text-[#7b1fa2]",
  qualified: "bg-[#fff3e0] text-[#e65100]",
  consultation_booked: "bg-[#e8f5e9] text-[#2e7d32]",
  converted: "bg-[#e8f5e9] text-[#1b5e20]",
  lost: "bg-[#ffebee] text-[#c62828]",
  // Proposal statuses
  draft: "bg-[#f5f5f5] text-[#757575]",
  pending_review: "bg-[#fff8e1] text-[#f57f17]",
  approved: "bg-[#e8f5e9] text-[#2e7d32]",
  revision_requested: "bg-[#fff3e0] text-[#e65100]",
  rejected: "bg-[#ffebee] text-[#c62828]",
  executing: "bg-[#e3f2fd] text-[#1565c0]",
  completed: "bg-[#e8f5e9] text-[#1b5e20]",
  failed: "bg-[#ffebee] text-[#b71c1c]",
  // Sources
  google: "bg-[#e8f0fe] text-[#1967d2]",
  facebook: "bg-[#e7f0ff] text-[#1877f2]",
  instagram: "bg-[#fce4ec] text-[#c2185b]",
  organic: "bg-[#f5f5f5] text-[#616161]",
  manual: "bg-[#f5f5f5] text-[#616161]",
  website: "bg-[#f5f5f5] text-[#616161]",
  score: "bg-[#fdf6e3] text-[#8a6d1b]",
  // Integration
  connected: "bg-[#e8f5e9] text-[#2e7d32]",
  disconnected: "bg-[#f5f5f5] text-[#9e9e9e]",
  active: "bg-[#e8f5e9] text-[#2e7d32]",
  paused: "bg-[#fff8e1] text-[#f57f17]",
};

interface BadgeProps {
  status: string;
  label?: string;
  className?: string;
}

export function Badge({ status, label, className }: BadgeProps) {
  const style = BADGE_STYLES[status] ?? "bg-[#f5f5f5] text-[#616161]";
  return (
    <span
      className={clsx(
        "px-2.5 py-0.5 rounded-full text-[.75rem] font-semibold inline-block leading-relaxed",
        style,
        className
      )}
    >
      {label ?? status}
    </span>
  );
}
