interface EmptyStateProps {
  icon?: string;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({
  icon = "inbox",
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="text-center py-12 text-text-secondary">
      <i className={`fas fa-${icon} text-[2.5rem] mb-4 opacity-30 block`} />
      <h3 className="text-[1.1rem] text-text-primary mb-1 font-semibold">
        {title}
      </h3>
      {description && <p className="text-[.9rem] mb-4">{description}</p>}
      {action}
    </div>
  );
}
