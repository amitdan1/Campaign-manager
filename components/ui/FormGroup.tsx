import { clsx } from "clsx";
import { InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";

interface FormGroupProps {
  label: string;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
}

export function FormGroup({ label, required, children, className }: FormGroupProps) {
  return (
    <div className={clsx("mb-5", className)}>
      <label className="block mb-1.5 text-[.85rem] font-semibold text-text-primary">
        {label}
        {required && <span className="text-status-rejected mr-1">*</span>}
      </label>
      {children}
    </div>
  );
}

const inputBase =
  "w-full px-3 py-2.5 border border-border rounded-sm text-[.9rem] bg-card-bg text-text-primary transition-colors focus:outline-none focus:border-accent focus:shadow-[0_0_0_3px_rgba(201,169,110,.15)]";

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={clsx(inputBase, props.className)} />;
}

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} className={clsx(inputBase, props.className)} />;
}

export function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      {...props}
      className={clsx(inputBase, "min-h-[80px] resize-y font-[inherit]", props.className)}
    />
  );
}
