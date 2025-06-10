import React from "react";
import clsx from "clsx";

const SideNavbar = ({ isOpen, setIsOpen }) => {
  // Example static entries, you can replace this with actual session list
  const entries = [
    { id: "session1", label: "Session 1" },
    { id: "session2", label: "Session 2" },
  ];

  return (
    <aside className="fixed top-0 left-0 w-64 h-full bg-panel shadow-lg z-40 p-4">
      <h2 className="text-xl font-bold mb-4 text-white">Sessions</h2>
      <ul className="space-y-2">
        {entries.map((entry) => (
          <li key={entry.id}>
            <button
              // You can replace this or leave it as a placeholder
              onClick={() => console.log("Clicked:", entry.id)}
              className={clsx(
                "w-full text-left px-2 py-1 rounded transition",
                "hover:bg-borderLight text-white"
              )}
            >
              {entry.label}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default SideNavbar;
