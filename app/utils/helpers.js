// utils/helpers.js

export const extractDomain = (url) => {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return null;
  }
};

export const fetchJSON = async (url, body) => {
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return await res.json();
  } catch  {
    return { error: "Network error. Please try again." };
  }
};
