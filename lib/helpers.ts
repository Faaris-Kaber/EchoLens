// Helper utility functions

export const extractDomain = (url: string): string | null => {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return null;
  }
};

export const fetchJSON = async <T>(url: string, body: Record<string, unknown>): Promise<T & { error?: string }> => {
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return await res.json();
  } catch {
    return { error: "Network error. Please try again." } as T & { error: string };
  }
};

