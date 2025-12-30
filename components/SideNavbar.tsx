"use client";

import React, { useState } from "react";
import clsx from "clsx";
import { Pencil } from "lucide-react";
import type { Session } from "@/lib/types";

interface SideNavbarProps {
  sessions: Session[];
  onNewChat: () => void;
  onSelectSession: (session: Session, index: number) => void;
  activeSessionIndex: number;
  setSessions: React.Dispatch<React.SetStateAction<Session[]>>;
}

const SideNavbar = ({
  sessions,
  onNewChat,
  onSelectSession,
  activeSessionIndex,
  setSessions,
}: SideNavbarProps) => {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [tempLabel, setTempLabel] = useState("");

  // start renaming a session
  const startEditing = (index: number) => {
    setEditingIndex(index);
    setTempLabel(sessions[index].label);
  };

  // save the updated label or fallback if left empty
  const finishEditing = (index: number) => {
    const updated = [...sessions];
    const cleanLabel = tempLabel.trim();
    updated[index].label = cleanLabel || `Session ${index + 1}`;
    setSessions(updated);
    setEditingIndex(null);
  };

  return (
    <aside className="fixed top-0 left-0 w-64 h-full bg-panel shadow-lg z-40 p-4 pt-16">
      <button
        onClick={onNewChat}
        className="w-full bg-borderLight text-white py-2 rounded-lg mb-4 hover:bg-accent transition"
      >
        + New chat
      </button>

      <h2 className="text-sm font-semibold text-textMuted mb-2">sessions</h2>

      <ul className="space-y-1 overflow-y-auto max-h-[80vh] pr-1">
        {sessions.map((entry, index) => (
          <li key={index} className="flex items-center">
            <button
              onClick={() => onSelectSession(entry, index)}
              className={clsx(
                "flex-1 text-left px-3 py-2 rounded transition truncate",
                activeSessionIndex === index
                  ? "bg-borderLight text-white"
                  : "text-white hover:bg-borderLight/50"
              )}
            >
              {editingIndex === index ? (
                <input
                  type="text"
                  value={tempLabel}
                  onChange={(e) => setTempLabel(e.target.value)}
                  onBlur={() => finishEditing(index)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") finishEditing(index);
                  }}
                  autoFocus
                  className="w-full bg-panel text-white px-2 py-1 rounded border border-borderLight"
                />
              ) : (
                <span>{entry.label}</span>
              )}
            </button>

            {editingIndex !== index && (
              <button
                onClick={() => startEditing(index)}
                title="rename"
                aria-label="rename session"
                className="ml-2 text-textMuted hover:text-white transition"
              >
                <Pencil size={16} />
              </button>
            )}
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default SideNavbar;

