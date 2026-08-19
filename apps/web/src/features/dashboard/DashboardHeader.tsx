import { BarChart3, Menu } from "lucide-react";
import { Link, NavLink } from "react-router-dom";

const navigation = [["Resumen", "resumen"], ["Zonas", "zonas"], ["Pagos", "pagos"], ["Calidad", "calidad"]] as const;

export function DashboardHeader() {
  return <header className="sticky top-0 z-20 border-b border-white/[.07] bg-[#080808]/85 backdrop-blur-xl"><div className="mx-auto flex h-16 max-w-[1600px] items-center gap-4 px-4 sm:px-6 lg:px-8"><Link to="/" className="flex shrink-0 items-center gap-2.5"><span className="grid h-8 w-8 place-items-center rounded-lg bg-[#ff4d24] text-white"><BarChart3 size={17} /></span><span className="text-sm font-semibold tracking-[-.02em] text-[#f7f7f5]">Chicago Taxi <span className="hidden text-[#a8a8a3] sm:inline">Analytics</span></span></Link><nav aria-label="Secciones del dashboard" className="ml-auto flex min-w-0 items-center gap-1 overflow-x-auto [scrollbar-width:none]">{navigation.map(([label, target]) => <NavLink key={target} to={target} className={({ isActive }) => `shrink-0 border-b-2 px-3 py-2 text-xs font-medium transition focus:outline-none focus:ring-2 focus:ring-[#ffb547] ${isActive ? "border-[#ff4d24] text-[#ffd1c5]" : "border-transparent text-[#a8a8a3] hover:text-[#f7f7f5]"}`}>{label}</NavLink>)}</nav><Menu className="hidden text-[#a8a8a3]" size={19} /></div></header>;
}
