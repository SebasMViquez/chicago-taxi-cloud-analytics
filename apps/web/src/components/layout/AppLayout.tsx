import { BarChart3 } from "lucide-react";
import { Outlet } from "react-router-dom";

export function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-6 py-4">
          <div className="flex h-10 w-10 items-center justify-center rounded bg-lake text-white">
            <BarChart3 aria-hidden="true" size={22} />
          </div>
          <div>
            <p className="text-sm font-medium text-lake">Chicago Taxi Trips</p>
            <h1 className="text-xl font-semibold text-ink">Analytics Platform</h1>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}

