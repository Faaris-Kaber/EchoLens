import React from "react";
import { Check, X } from "lucide-react";

const ArgumentSection = ({ title, color, icon, points }) => (
    <div className={`flex-1 rounded-xl border border-borderLight bg-panel p-4`}>
    <h4 className={`flex items-center gap-2 text-${color}-300 font-semibold mb-3`}>
      {icon}
      {title}
    </h4>
    <ul className="list-disc ml-4 text-sm space-y-2 text-white leading-snug max-w-[40ch]">
      {points.map((point, i) => (
        <li key={i}>{point}</li>
      ))}
    </ul>
  </div>
);

const DebateResults = ({ claim, forPoints = [], againstPoints = [] }) => {
  const hasFor = Array.isArray(forPoints) && forPoints.length;
  const hasAgainst = Array.isArray(againstPoints) && againstPoints.length;

  return (
    <section className="w-full bg-panel p-6 rounded-2xl shadow-md border border-borderLight mt-0">
      <header className="mb-4">
        <div className="uppercase text-sm text-textMuted">Debate Topic</div>
        <h3 className="text-accent text-lg font-semibold italic max-w-[70ch]">
          {claim}
        </h3>
      </header>

      {(hasFor || hasAgainst) ? (
        <div className="flex flex-col md:flex-row gap-6">
          {hasFor && (
            <ArgumentSection
              title="For"
              color="green"
              icon={<Check size={18} />}
              points={forPoints}
            />
          )}
          {hasAgainst && (
            <ArgumentSection
              title="Against"
              color="red"
              icon={<X size={18} />}
              points={againstPoints}
            />
          )}
        </div>
      ) : (
        <p className="text-textMuted text-sm italic">
          No arguments were found.
        </p>
      )}
    </section>
  );
};

export default DebateResults;
