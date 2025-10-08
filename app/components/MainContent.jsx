"use client";

import React, { useState, useEffect } from "react";
import BiasCompass from "../components/BiasCompass";
import EmotionBadge from "../components/EmotionBadge";
import DebateResults from "../components/DebateResults";
import { extractDomain, fetchJSON } from "../utils/helpers";

const MainContent = ({
  text,
  setText,
  sourceUrl,
  setSourceUrl,
  analysisResult,
  setAnalysisResult,
  debateResult,
  setDebateResult,
  mode,
  setMode,
  updateCurrentSession,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sourceBias, setSourceBias] = useState(null);
  const [isScraping, setIsScraping] = useState(false);

  // if user provides a source url during analyze mode, try to map its domain to known bias
  useEffect(() => {
    if (mode !== "analyze" || !sourceUrl) {
      setSourceBias(null);
      return;
    }

    const domain = extractDomain(sourceUrl);
    fetch("/data/domain_to_bias.json")
      .then((res) => res.json())
      .then((map) => {
        if (domain && map[domain]) {
          setSourceBias({ domain, label: map[domain] });
        } else {
          setSourceBias(null);
        }
      })
      .catch(() => setSourceBias(null));
  }, [sourceUrl, mode]);

  // handle fetching article from URL
  const handleFetchArticle = async () => {
    if (!sourceUrl) return;
    
    setIsScraping(true);
    setError("");
    
    try {
      const response = await fetch("http://localhost:8000/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: sourceUrl }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setText(data.text);
      } else {
        setError(data.detail || "Failed to scrape article");
      }
    } catch (err) {
      setError("Error fetching article. Please check the URL and try again.");
      console.error("Scraping error:", err);
    } finally {
      setIsScraping(false);
    }
  };

  // Handle sourceUrl change and save to session
  const handleSourceUrlChange = (newUrl) => {
    setSourceUrl(newUrl);
    updateCurrentSession({ sourceUrl: newUrl });
  };

  // handle bias and emotion analysis
  const handleAnalyze = async () => {
    setLoading(true);
    setError("");
    setAnalysisResult(null);

    const data = await fetchJSON("http://localhost:8000/analyze", { text });

    if (data.error) {
      setError(data.error);
    } else {
      setAnalysisResult(data);
      updateCurrentSession({
        text,
        sourceUrl,
        analyzeResult: data,
        mode: "analyze",
      });
    }

    setLoading(false);
  };

  // handle argument breakdown generation
  const handleDebate = async () => {
    setLoading(true);
    setError("");
    setDebateResult(null);

    const data = await fetchJSON("http://localhost:8000/debate", { text });

    if (data.error) {
      setError(data.error);
    } else {
      setDebateResult(data);
      updateCurrentSession({
        text,
        sourceUrl,
        debateResult: data,
        mode: "debate",
      });
    }

    setLoading(false);
  };

  return (
    <main className="flex-1 p-6 bg-appBg text-white overflow-auto">
      <div className="flex flex-col lg:flex-row items-start gap-6 max-w-7xl mx-auto">
        {/* left input section */}
        <section className="lg:w-3/5 w-full bg-panel p-6 rounded-2xl shadow-md border border-borderLight">
          <h2 className="text-2xl font-bold mb-4">Input</h2>

          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste article or text here..."
            className="w-full h-[360px] p-4 rounded-xl border border-borderLight bg-panel text-white placeholder-textMuted resize-none focus:outline-none focus:ring-2 focus:ring-accent"
          />

          <div className="flex gap-4 mt-4">
            <button
              onClick={() => setMode("analyze")}
              className={`px-4 py-2 rounded-xl font-semibold text-sm shadow-md ${
                mode === "analyze"
                  ? "bg-accent text-white"
                  : "bg-borderLight text-white/70"
              }`}
            >
              Analyze
            </button>
            <button
              onClick={() => setMode("debate")}
              className={`px-4 py-2 rounded-xl font-semibold text-sm shadow-md ${
                mode === "debate"
                  ? "bg-accent text-white"
                  : "bg-borderLight text-white/70"
              }`}
            >
              Debate
            </button>
          </div>

          {/* only show source url input in analyze mode */}
          {mode === "analyze" && (
            <div className="mt-4">
              <label className="block text-sm font-medium text-textMuted mb-1">
                Source URL (optional)
              </label>
              <div className="flex gap-2">
                <input
                  type="url"
                  value={sourceUrl}
                  onChange={(e) => handleSourceUrlChange(e.target.value)}
                  placeholder="https://example.com/news/article"
                  className="flex-1 p-2 rounded-xl border border-borderLight bg-panel text-white placeholder-textMuted focus:outline-none focus:ring-2 focus:ring-accent"
                />
                <button
                  onClick={handleFetchArticle}
                  disabled={!sourceUrl || isScraping}
                  className="px-4 py-2 bg-blue-500 text-white rounded-xl font-semibold text-sm shadow-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {isScraping ? "Fetching..." : "Fetch"}
                </button>
              </div>
            </div>
          )}

          <button
            onClick={mode === "analyze" ? handleAnalyze : handleDebate}
            disabled={loading}
            className="mt-4 w-full bg-gradient-to-r from-blue-500 to-violet-600 text-white py-2 rounded-xl font-semibold shadow-md hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading && "Processing..."}
            {!loading && mode === "analyze" && "Analyze"}
            {!loading && mode === "debate" && "Explore Both Sides"}
          </button>

          {error && <p className="mt-4 text-red-500 text-sm">{error}</p>}
        </section>

        {/* right results section */}
        <div className="flex-1 flex flex-col gap-6 self-start">
          {mode === "analyze" && analysisResult && (
            <>
              {analysisResult.bias?.label && (
                <div className="bg-panel p-6 rounded-2xl border-l-4 border-yellow-400 shadow-md">
                  <div className="text-sm text-textMuted uppercase mb-2">Bias Breakdown</div>
                  <BiasCompass label={analysisResult.bias.label} />
                </div>
              )}

              {analysisResult.emotion?.label && (
                <div className="bg-panel p-6 rounded-2xl border-l-4 border-blue-400 shadow-md">
                  <div className="text-sm text-textMuted uppercase mb-2">Emotion Analysis</div>
                  <EmotionBadge
                    label={analysisResult.emotion.label}
                    confidence={analysisResult.emotion.confidence}
                  />
                </div>
              )}

              {sourceBias && (
                <div className="bg-panel p-4 rounded-xl border-l-4 border-accent shadow">
                  <div className="text-sm text-textMuted uppercase mb-2">Source Bias</div>
                  <p>
                    <strong>{sourceBias.domain}</strong> is rated as{" "}
                    <span className="text-accent font-semibold">{sourceBias.label}</span> by AllSides.
                  </p>
                </div>
              )}
            </>
          )}

          {mode === "debate" && debateResult && (
            <DebateResults
              claim={debateResult.claim}
              forPoints={debateResult.for}
              againstPoints={debateResult.against}
            />
          )}
        </div>
      </div>
    </main>
  );
};

export default MainContent;
