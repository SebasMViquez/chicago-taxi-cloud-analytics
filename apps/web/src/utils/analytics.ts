import type { DemandByHourPoint } from "../types/dashboard";

const dayNames = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"];

export function getPeakDemandInsight(points: DemandByHourPoint[]): string | null {
  if (points.length === 0) return null;
  const peak = points.reduce((highest, point) => point.tripCount > highest.tripCount ? point : highest);
  return `El ${dayNames[peak.dayOfWeek] ?? "día"} a las ${String(peak.hourOfDay).padStart(2, "0")}:00 concentra el mayor volumen registrado.`;
}

export function formatDemandLabel(dayOfWeek: number, hourOfDay: number): string {
  return `${dayNames[dayOfWeek]?.slice(0, 3) ?? "n/a"}. ${String(hourOfDay).padStart(2, "0")}:00`;
}
