"use client";

import { useState } from "react";
import { Menu, X } from "lucide-react";
import SideNavbar from "./components/SideNavbar";
import Header from "./components/Header";
import MainContent from "./components/MainContent";

// structure for analyze result
type AnalyzeResult = {
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

// structure for debate result
type DebateResult = {
  claim: string;
  for: string[];
  against: string[];
};

// structure for each chat session
type Session = {
  label: string;
  text: string;
  analyzeResult?: AnalyzeResult | null;
  debateResult?: DebateResult | null;
  mode: "analyze" | "debate";
};

export default function HomePage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // toggle sidebar visibility
  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  // initialize with one session
  const [sessions, setSessions] = useState<Session[]>([
    {
      label: "Session 1",
      text: "",
      analyzeResult: null,
      debateResult: null,
      mode: "analyze",
    },
  ]);
  const [activeSessionIndex, setActiveSessionIndex] = useState(0);

  // state for main panel
  const [text, setText] = useState("");
  const [analysisResult, setAnalysisResult] = useState<AnalyzeResult | null>(null);
  const [debateResult, setDebateResult] = useState<DebateResult | null>(null);
  const [mode, setMode] = useState<"analyze" | "debate">("analyze");

  // update only the current session's values without mutating others
  const updateCurrentSession = (updatedFields: Partial<Session>) => {
    setSessions((prev) => {
      const updated = [...prev];
      updated[activeSessionIndex] = {
        ...updated[activeSessionIndex],
        ...updatedFields,
      };
      return updated;
    });
  };

  // creates a new chat session with numbered label
  const handleNewChat = () => {
    const newSessionNumber = sessions.length + 1;
    const newSession: Session = {
      label: `Session ${newSessionNumber}`,
      text: "",
      analyzeResult: null,
      debateResult: null,
      mode: "analyze",
    };
    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionIndex(0);
    setText("");
    setAnalysisResult(null);
    setDebateResult(null);
    setMode("analyze");
  };

  // loads session values into UI when user clicks one
  const handleSessionClick = (session: Session, index: number) => {
    setText(session.text);
    setMode(session.mode);
    setAnalysisResult(session.analyzeResult || null);
    setDebateResult(session.debateResult || null);
    setActiveSessionIndex(index);
    setIsSidebarOpen(false);
  };

  return (
    <div className="flex flex-col min-h-screen bg-appBg text-textMain">
      <button
        onClick={toggleSidebar}
        className="fixed top-4 left-4 z-50 text-textMuted hover:text-white transition"
        aria-label="Toggle sidebar"
      >
        {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {isSidebarOpen && (
        <SideNavbar
          isOpen={isSidebarOpen}
          setIsOpen={setIsSidebarOpen}
          sessions={sessions}
          onNewChat={handleNewChat}
          onSelectSession={handleSessionClick}
          activeSessionIndex={activeSessionIndex}
          setSessions={setSessions}
        />
      )}

      <main
        className={`flex flex-col flex-1 transition-all duration-200 ${
          isSidebarOpen ? "ml-64" : "ml-0"
        }`}
      >
        <Header isSidebarOpen={isSidebarOpen} />
        <MainContent
          text={text}
          setText={setText}
          analysisResult={analysisResult}
          setAnalysisResult={setAnalysisResult}
          debateResult={debateResult}
          setDebateResult={setDebateResult}
          mode={mode}
          setMode={setMode}
          updateCurrentSession={updateCurrentSession}
        />
      </main>
    </div>
  );
}
