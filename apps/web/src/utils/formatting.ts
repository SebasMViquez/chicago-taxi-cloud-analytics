const numberFormatter = new Intl.NumberFormat("es-ES", { maximumFractionDigits: 2 });
const compactNumberFormatter = new Intl.NumberFormat("es-ES", { notation: "compact", maximumFractionDigits: 1 });
const currencyFormatter = new Intl.NumberFormat("es-ES", { style: "currency", currency: "USD", maximumFractionDigits: 2 });

export function formatNumber(value: number): string {
  return numberFormatter.format(value);
}

export function formatCompactNumber(value: number): string {
  return compactNumberFormatter.format(value);
}

export function formatCurrency(value: number): string {
  return currencyFormatter.format(value);
}

export function formatPercentage(value: number): string {
  return new Intl.NumberFormat("es-ES", { style: "percent", maximumFractionDigits: 1 }).format(value);
}

export function formatNullableMetric(value: number | null | undefined, prefix = "", suffix = ""): string {
  if (value === null || value === undefined) {
    return "Sin datos";
  }

  return `${prefix}${formatNumber(value)}${suffix}`;
}

export function formatMonth(year: number, month: number): string {
  return new Intl.DateTimeFormat("es-ES", { month: "short", year: "2-digit" }).format(new Date(year, month - 1));
}

export function formatPaymentMethod(paymentType: string): string {
  const labels: Record<string, string> = { "Credit Card": "Tarjeta de crédito", Cash: "Efectivo", "No Charge": "Sin cargo", Dispute: "En disputa", Unknown: "Desconocido", Mobile: "Pago móvil", Prcard: "Tarjeta prepago" };
  return labels[paymentType] ?? paymentType;
}

