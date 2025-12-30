"use client";
import React from "react";
import clsx from "clsx";

interface BiasCompassProps {
  label: string;
}

const BiasCompass = ({ label }: BiasCompassProps) => {
  const categories = ["Left", "Center", "Right"];

  return (
    <div className="w-full max-w-md mx-auto text-white">
      <h3 className="text-lg font-semibold mb-4">Detected Bias</h3>

      <div className="flex justify-between items-center bg-panel border border-borderLight rounded-xl overflow-hidden">
        {categories.map((cat) => (
          <div
            key={cat}
            className={clsx(
              "flex-1 py-3 text-center font-medium transition",
              {
                "bg-blue-600 text-white": cat === "Left" && label === "Left",
                "bg-gray-400 text-white": cat === "Center" && label === "Center",
                "bg-red-600 text-white": cat === "Right" && label === "Right",
                "bg-panel": cat !== label,
              }
            )}
          >
            {cat}
          </div>
        ))}
      </div>

      <p className="mt-4 text-center text-lg">
        Final Label: <span className="font-bold text-accent">{label}</span>
      </p>
    </div>
  );
};

export default BiasCompass;

