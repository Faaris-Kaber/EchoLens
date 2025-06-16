"use client";

import React from "react";
import clsx from "clsx";

// map each emotion label to an emoji and background color
const emotionStyles = {
  anger:    { emoji: "😠", color: "bg-red-600" },
  disgust:  { emoji: "🤢", color: "bg-green-700" },
  fear:     { emoji: "😨", color: "bg-purple-600" },
  joy:      { emoji: "😊", color: "bg-yellow-400 text-black" },
  neutral:  { emoji: "😐", color: "bg-gray-400" },
  sadness:  { emoji: "😢", color: "bg-blue-500" },
  surprise: { emoji: "😲", color: "bg-indigo-500" },
};

const EmotionBadge = ({ label = "unknown", confidence = 0 }) => {
  // normalize the label to lowercase just in case
  const safeLabel = label.toLowerCase();

  // get style for the emotion or fall back to question mark and gray
  const style = emotionStyles[safeLabel] || { emoji: "❓", color: "bg-gray-500" };

  return (
    <div
      className={clsx(
        "inline-flex items-center gap-3 px-5 py-3 rounded-full text-lg font-semibold shadow",
        style.color
      )}
      aria-label={`detected emotion is ${label} with ${Math.round(confidence * 100)} percent confidence`}
    >
      <span className="text-2xl">{style.emoji}</span>
      <span className="capitalize">{label}</span>
      <span className="opacity-70 text-sm">({(confidence * 100).toFixed(1)}%)</span>
    </div>
  );
};

export default EmotionBadge;
