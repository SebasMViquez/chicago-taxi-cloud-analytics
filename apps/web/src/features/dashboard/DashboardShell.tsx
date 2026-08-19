import { Outlet } from "react-router-dom";
import { DashboardHeader } from "./DashboardHeader";

export function DashboardShell() {
  return <div className="min-h-screen bg-[#080808] pb-12"><DashboardHeader /><main className="mx-auto max-w-[1600px] px-4 pt-8 sm:px-6 lg:px-8"><Outlet /></main></div>;
}
