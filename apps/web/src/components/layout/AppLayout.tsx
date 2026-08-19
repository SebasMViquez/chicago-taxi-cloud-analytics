import { Outlet } from "react-router-dom";

export function AppLayout() {
  return <div className="min-h-screen bg-[#080808] text-[#f7f7f5]"><Outlet /></div>;
}

