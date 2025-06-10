"use client";
import React from "react";
import clsx from "clsx";

const emotionStyles = {
  anger:    { emoji: "😠", color: "bg-red-600" },
  disgust:  { emoji: "🤢", color: "bg-green-700" },
  fear:     { emoji: "😨", color: "bg-purple-600" },
  joy:      { emoji: "😊", color: "bg-yellow-400 text-black" },
  neutral:  { emoji: "😐", color: "bg-gray-400" },
  sadness:  { emoji: "😢", color: "bg-blue-500" },
  surprise: { emoji: "😲", color: "bg-indigo-500" },
};

const EmotionBadge = ({ label = "Unknown", confidence = 0 }) => {
  const safeLabel = label.toLowerCase();
  const { emoji, color } = emotionStyles[safeLabel] || { emoji: "❓", color: "bg-gray-500" };

  return (
    <div
      className={clsx(
        "inline-flex items-center gap-3 px-5 py-3 rounded-full text-lg font-semibold shadow",
        color
      )}
      aria-label={`Detected emotion is ${label} with ${Math.round(confidence * 100)}% confidence`}
    >
      <span className="text-2xl">{emoji}</span>
      <span className="capitalize">{label}</span>
      <span className="opacity-70 text-sm">({(confidence * 100).toFixed(1)}%)</span>
    </div>
  );
};

export default EmotionBadge;
