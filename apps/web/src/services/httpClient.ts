const defaultApiBaseUrl = "";

function toCamelCase(value: string): string {
  return value.charAt(0).toLowerCase() + value.slice(1);
}

function normalizeResponseKeys(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(normalizeResponseKeys);
  }

  if (value === null || typeof value !== "object") {
    return value;
  }

  return Object.fromEntries(
    Object.entries(value).map(([key, entryValue]) => [
      toCamelCase(key),
      normalizeResponseKeys(entryValue),
    ]),
  );
}

export async function getJson<TResponse>(path: string): Promise<TResponse> {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? defaultApiBaseUrl;
  const response = await fetch(`${apiBaseUrl}${path}`);

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return null as TResponse;
  }

  const payload = await response.json();
  return normalizeResponseKeys(payload) as TResponse;
}

