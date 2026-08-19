import { ArrowRight } from "lucide-react";
import { gsap } from "gsap";
import { useRef } from "react";
import { useNavigate } from "react-router-dom";
import { LetterGlitch } from "../../components/landing/LetterGlitch";
import { TextType } from "../../components/landing/TextType";

const glitchColors = ["#35120D", "#6B2014", "#A83218", "#E44A20", "#FF6A32", "#FF9B52"];

export function LandingPage() {
  const navigate = useNavigate();
  const contentRef = useRef<HTMLElement>(null);
  const backgroundRef = useRef<HTMLDivElement>(null);
  const enterDashboard = () => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { navigate("/dashboard/resumen"); return; }
    const timeline = gsap.timeline({ onComplete: () => navigate("/dashboard/resumen") });
    timeline.to("[data-landing-title]", { opacity: 0, y: -12, filter: "blur(5px)", duration: 0.22 }).to("[data-landing-cta]", { opacity: 0, y: 10, duration: 0.16 }, "<0.04").to(backgroundRef.current, { opacity: 0, duration: 0.18 }, "<");
  };
  return (
    <main className="relative isolate flex min-h-[100dvh] w-screen items-center justify-center overflow-hidden px-5">
      <div ref={backgroundRef} className="absolute inset-0"><LetterGlitch glitchColors={glitchColors} glitchSpeed={50} centerVignette outerVignette={false} smooth /><div className="absolute inset-0 bg-[#080808]/18" /></div>
      <section ref={contentRef} className="relative z-10 mx-auto max-w-[900px] text-center">
        <h1 data-landing-title className="text-balance text-[clamp(2rem,5vw,4.5rem)] font-semibold leading-[1.02] tracking-[-.055em] text-[#f7f7f5]"><TextType texts={["De los datos a decisiones claras.", "Datos que se entienden."]} typingSpeed={45} initialDelay={250} pauseDuration={5000} showCursor cursorCharacter="|" /></h1>
        <button data-landing-cta type="button" onClick={enterDashboard} className="group mt-9 inline-flex items-center gap-2 rounded-xl bg-[#ff4d24] px-5 py-3.5 text-sm font-semibold text-white shadow-[0_8px_28px_rgba(255,77,36,.2)] transition duration-200 hover:-translate-y-0.5 hover:bg-[#ff7043] hover:shadow-[0_12px_32px_rgba(255,77,36,.32)] focus:outline-none focus:ring-2 focus:ring-[#ffb547] focus:ring-offset-2 focus:ring-offset-[#080808]">
          Ver estadísticas <ArrowRight size={17} className="transition-transform duration-200 group-hover:translate-x-0.5" aria-hidden="true" />
        </button>
      </section>
    </main>
  );
}
