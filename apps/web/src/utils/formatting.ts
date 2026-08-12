export function formatNullableMetric(
  value: number | null | undefined,
  prefix = "",
  suffix = "",
): string {
  if (value === null || value === undefined) {
    return "No data";
  }

  return `${prefix}${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}${suffix}`;
}

export function formatMonth(year: number, month: number): string {
  return `${year}-${month.toString().padStart(2, "0")}`;
}

