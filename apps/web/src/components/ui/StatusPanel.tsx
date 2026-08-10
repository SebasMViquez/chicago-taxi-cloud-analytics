import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

type StatusPanelProps = {
  status: "loading" | "ready" | "error";
  title: string;
  message: string;
};

export function StatusPanel({ status, title, message }: StatusPanelProps) {
  const Icon = status === "loading" ? Loader2 : status === "error" ? AlertCircle : CheckCircle2;

  return (
    <section className="rounded border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start gap-3">
        <Icon
          aria-hidden="true"
          className={status === "loading" ? "mt-0.5 animate-spin text-lake" : "mt-0.5 text-lake"}
          size={22}
        />
        <div>
          <h2 className="text-base font-semibold text-ink">{title}</h2>
          <p className="mt-1 text-sm leading-6 text-slate-600">{message}</p>
        </div>
      </div>
    </section>
  );
}

