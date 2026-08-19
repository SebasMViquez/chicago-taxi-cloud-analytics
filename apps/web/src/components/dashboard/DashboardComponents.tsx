import { ChevronLeft, ChevronRight, CircleAlert, Database, type LucideIcon } from "lucide-react";
import { gsap } from "gsap";
import { type ReactNode, useEffect, useRef, useState } from "react";
import { formatCompactNumber, formatNumber, formatPercentage } from "../../utils/formatting";

export type StatItem = { id: string; label: string; value: string; detail: string; icon: LucideIcon };

export function MetricCard({ item, isLoading = false, featured = false }: { item: StatItem; isLoading?: boolean; featured?: boolean }) {
  const Icon = item.icon;
  return <article className={`group relative flex min-h-[142px] flex-col justify-center overflow-hidden rounded-2xl border border-white/[.08] bg-[#151515] p-4 text-center transition duration-200 hover:-translate-y-0.5 hover:border-[#ff7043]/35 hover:bg-[#1a1a1a] sm:p-5 ${featured ? "bg-[radial-gradient(circle_at_top_right,rgba(255,77,36,.16),transparent_48%),#151515] sm:p-6" : ""}`}>
    <div className="relative"><p className="text-xs font-medium uppercase tracking-[.13em] text-[#a8a8a3]">{item.label}</p><span className="absolute right-0 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-lg bg-[#ff4d24]/10 text-[#ff7043]"><Icon size={16} aria-hidden="true" /></span></div>
    {isLoading ? <div className="mx-auto mt-5 h-7 w-3/4 animate-pulse rounded bg-white/[.08]" /> : <><p className={`mt-4 truncate font-mono font-semibold tracking-[-.04em] text-[#f7f7f5] tabular-nums ${featured ? "text-4xl sm:text-5xl" : "text-2xl"}`}>{item.value}</p><p className="mt-1.5 text-xs text-[#a8a8a3]">{item.detail}</p></>}
  </article>;
}

export function StatsDepthCarousel({ items, isLoading = false }: { items: StatItem[]; isLoading?: boolean }) {
  const [active, setActive] = useState(0);
  const cardRefs = useRef<Array<HTMLElement | null>>([]);
  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) return;
    cardRefs.current.forEach((card, index) => {
      if (card) gsap.to(card, { opacity: index === active ? 1 : 0.5, scale: index === active ? 1 : 0.94, y: index === active ? 0 : 5, duration: 0.28, overwrite: true });
    });
  }, [active]);
  const move = (direction: number) => setActive((current) => (current + direction + items.length) % items.length);
  return <section aria-label="Indicadores principales" className="lg:hidden" onKeyDown={(event) => { if (event.key === "ArrowLeft") move(-1); if (event.key === "ArrowRight") move(1); }}>
    <div className="overflow-hidden py-1" style={{ perspective: "1000px" }}>
      <div className="flex transition-transform duration-300 ease-out" style={{ transform: `translateX(-${active * 100}%)` }}>
        {items.map((item, index) => <article ref={(element) => { cardRefs.current[index] = element; }} key={item.id} className="min-w-full px-1"><MetricCard item={item} isLoading={isLoading} /></article>)}
      </div>
    </div>
    <div className="mt-3 flex items-center justify-center gap-3">
      <button type="button" aria-label="Indicador anterior" onClick={() => move(-1)} className="rounded-lg border border-white/10 p-1.5 text-[#a8a8a3] hover:text-white"><ChevronLeft size={16} /></button>
      <div className="flex gap-1.5">{items.map((item, index) => <button type="button" key={item.id} onClick={() => setActive(index)} aria-label={`Ver ${item.label}`} aria-current={active === index} className={`h-1.5 rounded-full transition-all ${active === index ? "w-5 bg-[#ff4d24]" : "w-1.5 bg-white/20"}`} />)}</div>
      <button type="button" aria-label="Indicador siguiente" onClick={() => move(1)} className="rounded-lg border border-white/10 p-1.5 text-[#a8a8a3] hover:text-white"><ChevronRight size={16} /></button>
    </div>
  </section>;
}

export function ChartPanel({ title, description, isLoading, isError, isEmpty, children, className = "" }: { title: string; description?: string; isLoading: boolean; isError: boolean; isEmpty: boolean; children: ReactNode; className?: string }) {
  return <section className={`min-w-0 rounded-[22px] border border-white/[.08] bg-[#151515] p-4 sm:p-5 ${className}`}>
    <div><h3 className="text-base font-semibold tracking-[-.02em] text-[#f7f7f5]">{title}</h3>{description ? <p className="mt-1 text-xs text-[#a8a8a3]">{description}</p> : null}</div>
    <div className="mt-5 h-[260px]">{isLoading ? <ChartSkeleton /> : isError ? <PanelMessage title="No se pudieron cargar estos datos." /> : isEmpty ? <PanelMessage title="No hay información disponible para este período." /> : children}</div>
  </section>;
}

export function ChartSkeleton() { return <div className="h-full animate-pulse rounded-xl bg-[linear-gradient(135deg,#1a1a1a,#202020,#151515)]" />; }
function PanelMessage({ title }: { title: string }) { return <div className="flex h-full flex-col items-center justify-center rounded-xl border border-dashed border-white/10 px-6 text-center text-sm text-[#a8a8a3]"><CircleAlert size={19} className="mb-2 text-[#ffb547]" aria-hidden="true" />{title}</div>; }

export function DataQualityScore({ sourceRows, acceptedRows, rejectedRows, isLoading, isError, className = "" }: { sourceRows?: number; acceptedRows?: number; rejectedRows?: number; isLoading: boolean; isError: boolean; className?: string }) {
  if (isLoading) return <section className={`rounded-[22px] border border-white/[.08] bg-[#151515] p-5 ${className}`}><ChartSkeleton /></section>;
  if (isError || sourceRows === undefined || acceptedRows === undefined || rejectedRows === undefined) return <section className={`rounded-[22px] border border-white/[.08] bg-[#151515] p-5 ${className}`}><PanelMessage title="No se pudo calcular la calidad del dataset." /></section>;
  const score = sourceRows > 0 ? acceptedRows / sourceRows : 0;
  return <section id="calidad" className={`rounded-[22px] border border-white/[.08] bg-[#151515] p-5 ${className}`}>
    <div className="flex items-start justify-between"><div><p className="text-xs font-medium uppercase tracking-[.13em] text-[#a8a8a3]">Calidad del dataset</p><h3 className="mt-2 text-lg font-semibold">Registros procesados</h3></div><Database className="text-[#ffb547]" size={19} /></div>
    <div className="mt-6 flex items-end gap-5"><div className="grid h-28 w-28 place-items-center rounded-full" style={{ background: `conic-gradient(#ff4d24 ${score * 360}deg, #292929 0deg)` }}><div className="grid h-[88px] w-[88px] place-items-center rounded-full bg-[#151515]"><strong className="font-mono text-xl tabular-nums">{formatPercentage(score)}</strong></div></div><div className="min-w-0 space-y-2 text-sm"><p className="text-[#f7f7f5]"><span className="text-[#a8a8a3]">Válidos </span>{formatCompactNumber(acceptedRows)}</p><p className="text-[#f7f7f5]"><span className="text-[#a8a8a3]">Descartados </span>{formatCompactNumber(rejectedRows)}</p><p className="text-[#a8a8a3]">{formatNumber(sourceRows)} filas de origen</p></div></div>
  </section>;
}
