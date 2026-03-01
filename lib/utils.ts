export function formatNumber(n: number | null | undefined, decimals = 0): string {
  if (n == null || isNaN(n)) return "0";
  return Number(n).toLocaleString("he-IL", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatCurrency(n: number | null | undefined): string {
  if (n == null || isNaN(n)) return "₪0";
  return "₪" + formatNumber(n, 0);
}

export function formatPct(n: number | null | undefined): string {
  if (n == null || isNaN(n)) return "0%";
  return Number(n).toFixed(1) + "%";
}

export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return "";
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("he-IL", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(date: string | Date | null | undefined): string {
  if (!date) return "";
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("he-IL", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
