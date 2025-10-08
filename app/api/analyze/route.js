export async function POST(req) {
  const { text } = await req.json();

  if (!text || text.trim().length < 10) {
    return new Response(
      JSON.stringify({ error: "Input text must be at least 10 characters." }),
      { status: 400 }
    );
  }

  // Simulated ai style output
  const result = {
    bias: "Moderate left-leaning bias with emotionally charged phrases.",
    techniques: "Loaded Language, Appeal to Authority, Strawman",
    credibility: "Moderate — Source has mixed accuracy history",
  };

  return new Response(JSON.stringify(result), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
