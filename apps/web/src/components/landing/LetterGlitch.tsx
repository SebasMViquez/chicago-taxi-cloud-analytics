import { useEffect, useRef } from "react";

type Letter = { char: string; color: string; targetColor: string; colorProgress: number };
type LetterGlitchProps = { glitchColors: string[]; glitchSpeed?: number; centerVignette?: boolean; outerVignette?: boolean; smooth?: boolean; characters?: string };

export function LetterGlitch({ glitchColors, glitchSpeed = 50, centerVignette = true, outerVignette = false, smooth = true, characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$&*()-_+=/[]{};:<>.,0123456789" }: LetterGlitchProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null); const animationRef = useRef<number | null>(null); const letters = useRef<Letter[]>([]); const grid = useRef({ columns: 0, rows: 0 }); const context = useRef<CanvasRenderingContext2D | null>(null); const lastGlitchTime = useRef(0);
  useEffect(() => {
    const canvas = canvasRef.current; if (!canvas) return; const ctx = canvas.getContext("2d"); if (!ctx) return; context.current = ctx;
    const symbols = Array.from(characters); const randomChar = () => symbols[Math.floor(Math.random() * symbols.length)]; const randomColor = () => glitchColors[Math.floor(Math.random() * glitchColors.length)];
    const toRgb = (color: string) => {
      const rgb = color.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
      if (rgb) return { r: Number(rgb[1]), g: Number(rgb[2]), b: Number(rgb[3]) };
      const value = color.replace("#", "");
      return { r: Number.parseInt(value.slice(0, 2), 16), g: Number.parseInt(value.slice(2, 4), 16), b: Number.parseInt(value.slice(4, 6), 16) };
    };
    const draw = () => { const current = context.current; if (!current || !canvas) return; const { width, height } = canvas.getBoundingClientRect(); current.globalAlpha = 1; current.fillStyle = "#080808"; current.fillRect(0, 0, width, height); current.font = "16px monospace"; current.textBaseline = "top"; current.globalAlpha = 0.62; letters.current.forEach((letter, index) => { current.fillStyle = letter.color; current.fillText(letter.char, (index % grid.current.columns) * 10, Math.floor(index / grid.current.columns) * 20); }); current.globalAlpha = 1; };
    const resize = () => { const parent = canvas.parentElement; if (!parent) return; const rect = parent.getBoundingClientRect(); const dpr = Math.min(window.devicePixelRatio || 1, 2); canvas.width = rect.width * dpr; canvas.height = rect.height * dpr; canvas.style.width = `${rect.width}px`; canvas.style.height = `${rect.height}px`; context.current?.setTransform(dpr, 0, 0, dpr, 0, 0); grid.current = { columns: Math.ceil(rect.width / 10), rows: Math.ceil(rect.height / 20) }; letters.current = Array.from({ length: grid.current.columns * grid.current.rows }, () => ({ char: randomChar(), color: randomColor(), targetColor: randomColor(), colorProgress: 1 })); draw(); };
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches; const update = () => { const count = Math.max(1, Math.floor(letters.current.length * 0.05)); for (let index = 0; index < count; index += 1) { const letter = letters.current[Math.floor(Math.random() * letters.current.length)]; if (!letter) continue; letter.char = randomChar(); letter.targetColor = randomColor(); letter.colorProgress = smooth ? 0 : 1; if (!smooth) letter.color = letter.targetColor; } };
    const transition = () => { let changed = false; letters.current.forEach((letter) => { if (letter.colorProgress >= 1) return; letter.colorProgress = Math.min(1, letter.colorProgress + 0.05); const start = toRgb(letter.color); const end = toRgb(letter.targetColor); letter.color = `rgb(${Math.round(start.r + (end.r - start.r) * letter.colorProgress)}, ${Math.round(start.g + (end.g - start.g) * letter.colorProgress)}, ${Math.round(start.b + (end.b - start.b) * letter.colorProgress)})`; changed = true; }); return changed; };
    const animate = (time: number) => { if (time - lastGlitchTime.current >= glitchSpeed) { update(); draw(); lastGlitchTime.current = time; } if (smooth && transition()) draw(); animationRef.current = requestAnimationFrame(animate); };
    resize(); if (!reduced) animationRef.current = requestAnimationFrame(animate); const observer = new ResizeObserver(resize); observer.observe(canvas.parentElement ?? canvas); return () => { if (animationRef.current !== null) cancelAnimationFrame(animationRef.current); observer.disconnect(); };
  }, [characters, glitchColors, glitchSpeed, smooth]);
  return <div className="relative h-full w-full overflow-hidden bg-[#080808]"><canvas ref={canvasRef} aria-hidden="true" className="block h-full w-full" />{centerVignette ? <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle,rgba(8,8,8,.52)_0%,rgba(8,8,8,0)_62%)]" /> : null}{outerVignette ? <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle,rgba(0,0,0,0)_58%,rgba(0,0,0,.9)_100%)]" /> : null}</div>;
}
