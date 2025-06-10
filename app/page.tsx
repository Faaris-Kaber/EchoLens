"use client";

import { useState, useCallback } from "react";
import { Menu, X } from "lucide-react";
import SideNavbar from "./components/SideNavbar";
import Header from "./components/Header";
import MainContent from "./components/MainContent";

export default function HomePage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = useCallback(() => {
    setIsSidebarOpen((prev) => !prev);
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-appBg text-textMain">
      {/* Toggle Button */}
      <button
        onClick={toggleSidebar}
        className="fixed top-4 left-4 z-50 text-textMuted hover:text-white transition"
        aria-label="Toggle sidebar"
      >
        {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      {isSidebarOpen && (
        <SideNavbar
          isOpen={isSidebarOpen}
          setIsOpen={setIsSidebarOpen}
        />
      )}

      {/* Main Content */}
      <main
        className={`flex flex-col flex-1 transition-all duration-200 ${
          isSidebarOpen ? "ml-64" : "ml-0"
        }`}
      >
        <Header isSidebarOpen={isSidebarOpen} />
        <MainContent />
      </main>
    </div>
  );
}
