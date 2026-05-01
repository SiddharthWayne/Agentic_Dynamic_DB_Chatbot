import { useState, type ReactNode } from "react";

export function Accordion({
  title,
  defaultOpen = false,
  children,
}: {
  title: ReactNode;
  defaultOpen?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-md border border-[var(--la-border)] bg-[#0f1117] overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-3 py-2 text-sm font-medium text-white hover:bg-[#1a1d27] transition-colors"
      >
        <span>{title}</span>
        <span className={`transition-transform duration-200 ${open ? "rotate-180" : ""}`}>▾</span>
      </button>
      <div
        className="overflow-hidden transition-all duration-300 ease-in-out"
        style={{ maxHeight: open ? "1000px" : "0px" }}
      >
        <div className="p-3 border-t border-[var(--la-border)]">{children}</div>
      </div>
    </div>
  );
}
