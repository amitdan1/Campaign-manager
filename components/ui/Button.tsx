import { clsx } from "clsx";
import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "success" | "danger" | "link";
type Size = "default" | "sm";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  icon?: string;
}

const variantStyles: Record<Variant, string> = {
  primary: "bg-accent text-white hover:bg-[#b8993f] hover:shadow-[0_2px_8px_rgba(201,169,110,.35)]",
  secondary: "bg-transparent text-text-primary border border-border hover:bg-bg",
  success: "bg-status-approved text-white hover:bg-[#43a047]",
  danger: "bg-status-rejected text-white hover:bg-[#d32f2f]",
  link: "bg-transparent text-accent hover:underline border-none p-0",
};

export function Button({
  variant = "primary",
  size = "default",
  icon,
  children,
  className,
  ...props
}: ButtonProps) {
  return (
    <button
      className={clsx(
        "rounded-sm cursor-pointer font-medium transition-all inline-flex items-center gap-1.5 no-underline leading-snug border-none",
        variantStyles[variant],
        size === "sm" ? "px-3 py-1.5 text-[.8rem]" : "px-5 py-2.5 text-[.875rem]",
        props.disabled && "opacity-50 cursor-not-allowed",
        className
      )}
      {...props}
    >
      {icon && <i className={`fas fa-${icon}`} />}
      {children}
    </button>
  );
}
