import type { ReactNode } from "react";

type ChartPanelProps = {
  title: string;
  isEmpty?: boolean;
  children: ReactNode;
};

export function ChartPanel({ title, isEmpty = false, children }: ChartPanelProps) {
  return (
    <section className="rounded border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-semibold uppercase text-slate-500">{title}</h3>
      <div className="mt-4 h-72">
        {isEmpty ? (
          <div className="flex h-full items-center justify-center rounded border border-dashed border-slate-300 text-sm text-slate-500">
            No data available
          </div>
        ) : (
          children
        )}
      </div>
    </section>
  );
}
