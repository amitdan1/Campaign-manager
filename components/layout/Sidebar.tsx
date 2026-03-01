"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const NAV_SECTIONS = [
  {
    label: "ראשי",
    items: [
      { href: "/", icon: "chart-pie", text: "דשבורד" },
      { href: "/proposals", icon: "clipboard-check", text: "הצעות" },
    ],
  },
  {
    label: "שיווק",
    items: [
      { href: "/leads", icon: "users", text: "לידים" },
      { href: "/campaigns", icon: "bullhorn", text: "קמפיינים" },
      { href: "/landing-pages", icon: "file-alt", text: "דפי נחיתה" },
    ],
  },
  {
    label: "תוכן",
    items: [{ href: "/assets", icon: "images", text: "נכסי מותג" }],
  },
  {
    label: "מערכת",
    items: [
      { href: "/agents", icon: "robot", text: "סוכנים" },
      { href: "/strategy", icon: "lightbulb", text: "אסטרטגיה" },
      { href: "/integrations", icon: "plug", text: "אינטגרציות" },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <nav className="w-sidebar max-md:w-[60px] bg-sidebar-bg text-text-on-dark fixed top-0 right-0 bottom-0 z-[100] flex flex-col overflow-y-auto">
      <div className="px-5 py-6 border-b border-white/[.08] flex items-center gap-3">
        <i className="fas fa-gem text-accent text-[1.1rem]" />
        <span className="text-[.95rem] font-semibold tracking-wide text-accent-light max-md:hidden">
          Ofir Assulin
        </span>
      </div>

      <ul className="list-none py-4 flex-1">
        {NAV_SECTIONS.map((section) => (
          <li key={section.label}>
            <div className="px-5 py-2 text-[.7rem] uppercase tracking-[.1em] text-white/[.35] mt-2 max-md:hidden">
              {section.label}
            </div>
            {section.items.map((item) => {
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={clsx(
                    "flex items-center gap-3 px-5 py-[.7rem] text-[.9rem] text-text-on-dark no-underline transition-colors max-md:justify-center max-md:px-0",
                    isActive
                      ? "bg-[#30305a] border-l-[3px] border-accent text-white font-semibold"
                      : "hover:bg-[#25254a]"
                  )}
                >
                  <i
                    className={clsx(
                      `fas fa-${item.icon} w-5 text-center text-[.95rem]`,
                      isActive ? "opacity-100" : "opacity-70"
                    )}
                  />
                  <span className="max-md:hidden">{item.text}</span>
                </Link>
              );
            })}
          </li>
        ))}
      </ul>

      <div className="px-5 py-4 border-t border-white/[.08] text-[.75rem] text-white/[.3] max-md:hidden">
        &copy; 2026 Performance Marketing
      </div>
    </nav>
  );
}
