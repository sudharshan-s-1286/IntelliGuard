import React from "react";
import { Outlet } from "react-router-dom";
import EnterpriseNavbar from "../components/EnterpriseNavbar";

export default function AppLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-[#120809] pt-16">
      <EnterpriseNavbar />
      <main className="flex-1 w-full relative z-0">
        <Outlet />
      </main>
    </div>
  );
}
