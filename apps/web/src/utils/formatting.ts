export function formatNullableMetric(
  value: number | null,
  prefix = "",
  suffix = "",
): string {
  if (value === null) {
    return "No data";
  }

  return `${prefix}${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}${suffix}`;
}

