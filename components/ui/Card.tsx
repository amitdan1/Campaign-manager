import { clsx } from "clsx";

interface CardProps {
  title?: string;
  headerAction?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export function Card({ title, headerAction, children, className, noPadding }: CardProps) {
  return (
    <div
      className={clsx(
        "bg-card-bg rounded-DEFAULT shadow-card border border-border-light mb-6 overflow-hidden",
        className
      )}
    >
      {title && (
        <div className="px-6 py-5 border-b border-border flex justify-between items-center">
          <h3 className="text-[1.05rem] font-semibold text-text-primary">
            {title}
          </h3>
          {headerAction}
        </div>
      )}
      <div className={noPadding ? "" : "p-6"}>{children}</div>
    </div>
  );
}
