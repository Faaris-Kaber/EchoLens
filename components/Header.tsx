"use client";

import React from "react";

interface HeaderProps {
  isSidebarOpen: boolean;
}

const Header = ({ isSidebarOpen }: HeaderProps) => {
  return (
    <header className="h-16 w-full bg-header border-b border-borderLight text-textMain flex items-center justify-between px-6">
      <h1 className={`text-lg font-bold ${!isSidebarOpen ? "ml-10" : ""}`}>
        EchoLens
      </h1>
      <span className="text-sm text-textMuted">Your AI assistant</span>
    </header>
  );
};

export default Header;

