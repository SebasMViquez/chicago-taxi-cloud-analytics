import { gsap } from "gsap";
import { type ReactNode, useLayoutEffect, useRef } from "react";

export function DashboardPageLayout({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    if (!ref.current || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const context = gsap.context(() => { gsap.from("[data-page-entry]", { opacity: 0, y: 10, duration: 0.38, stagger: 0.07, ease: "power2.out" }); }, ref);
    return () => context.revert();
  }, []);
  return <div ref={ref}><header data-page-entry><h1 className="text-3xl font-semibold tracking-[-.045em] text-[#f7f7f5] sm:text-4xl">{title}</h1><p className="mt-3 text-sm leading-6 text-[#a8a8a3]">{description}</p></header>{children}</div>;
}
