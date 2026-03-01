"use client";

import { useEffect, useRef } from "react";
import { clsx } from "clsx";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  large?: boolean;
  footer?: React.ReactNode;
}

export function Modal({ open, onClose, title, children, large, footer }: ModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  if (!open) return null;

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-[1000] bg-black/40 backdrop-blur-[2px] overflow-auto flex items-start justify-center"
      onClick={(e) => e.target === overlayRef.current && onClose()}
    >
      <div
        className={clsx(
          "bg-card-bg rounded-DEFAULT shadow-card-md my-[4%] w-[92%]",
          large ? "max-w-[900px]" : "max-w-[580px]"
        )}
      >
        {/* Header */}
        <div className="px-6 py-5 border-b border-border flex justify-between items-center">
          <h2 className="text-[1.15rem] text-text-primary font-semibold">{title}</h2>
          <button
            onClick={onClose}
            className="text-text-secondary text-2xl font-bold cursor-pointer leading-none bg-transparent border-none hover:text-text-primary"
          >
            &times;
          </button>
        </div>

        {/* Body */}
        <div className="p-6">{children}</div>

        {/* Footer */}
        {footer && (
          <div className="px-6 py-4 border-t border-border flex justify-end gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
