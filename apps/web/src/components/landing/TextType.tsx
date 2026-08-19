import { useEffect, useState } from "react";

type TextTypeProps = { texts: string[]; typingSpeed?: number; initialDelay?: number; pauseDuration?: number; showCursor?: boolean; cursorCharacter?: string };
export function TextType({ texts, typingSpeed = 45, initialDelay = 250, pauseDuration = 5000, showCursor = false, cursorCharacter = "|" }: TextTypeProps) {
  const reduced = typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const [index, setIndex] = useState(0); const [length, setLength] = useState(() => reduced ? texts[0]?.length ?? 0 : 0); const [deleting, setDeleting] = useState(false);
  const current = texts[index] ?? "";
  useEffect(() => { if (reduced) return; const complete = length === current.length; const delay = deleting ? Math.max(18, typingSpeed / 2) : complete ? pauseDuration : length === 0 ? initialDelay : typingSpeed; const timer = window.setTimeout(() => { if (complete && !deleting) setDeleting(true); else if (deleting && length === 0) { setDeleting(false); setIndex((value) => (value + 1) % texts.length); } else setLength((value) => value + (deleting ? -1 : 1)); }, delay); return () => window.clearTimeout(timer); }, [current.length, deleting, initialDelay, length, pauseDuration, reduced, texts.length, typingSpeed]);
  return <>{current.slice(0, length)}{showCursor ? <span aria-hidden="true" className="ml-1 inline-block text-[#ff7043] animate-pulse">{cursorCharacter}</span> : null}</>;
}
