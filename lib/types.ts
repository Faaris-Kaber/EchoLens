// Shared types for the application

export type AnalyzeResult = {
  bias: {
    label: string;
    confidence: number;
    raw_scores: Record<string, number>;
  };
  emotion: {
    label: string;
    confidence: number;
    raw_scores: Record<string, number>;
  };
};

export type DebateResult = {
  claim: string;
  for: string[];
  against: string[];
};

export type Session = {
  label: string;
  text: string;
  sourceUrl: string;
  analyzeResult?: AnalyzeResult | null;
  debateResult?: DebateResult | null;
  mode: "analyze" | "debate";
};

export type SourceBias = {
  domain: string;
  label: string;
} | null;

