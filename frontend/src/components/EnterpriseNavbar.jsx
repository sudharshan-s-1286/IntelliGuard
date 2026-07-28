import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Shield, LayoutDashboard, Bot, LineChart, Activity, FileText, Settings, Menu } from "lucide-react";

const NAV_LINKS = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Agents", href: "/agents", icon: Bot },
  { name: "Analytics", href: "/analytics", icon: LineChart },
  { name: "Audit", href: "/audit", icon: Activity },
  { name: "Reports", href: "/reports", icon: FileText },
  { name: "Settings", href: "/settings", icon: Settings },
];

export default function EnterpriseNavbar() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 w-full border-b border-[#4B0F18]/50 bg-[#120809]/80 backdrop-blur-md">
      <div className="w-full flex h-16 items-center justify-between px-6 md:px-8">
        
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 mr-8 group shrink-0">
          <Shield className="h-6 w-6 text-[#DC143C] group-hover:text-[#FF4D6D] transition-colors" />
          <span className="font-bold text-lg tracking-tight text-white hidden sm:inline-block">
            IntelliGuard
          </span>
        </Link>
        
        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center flex-1 gap-6 text-sm font-medium">
          {NAV_LINKS.map((link) => {
            const isActive = location.pathname.startsWith(link.href);
            const Icon = link.icon;
            return (
              <Link
                key={link.name}
                to={link.href}
                className={`flex items-center gap-2 transition-all hover:text-[#FF4D6D] relative py-5 ${
                  isActive ? "text-[#DC143C] drop-shadow-[0_0_8px_rgba(220,20,60,0.5)]" : "text-slate-400"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{link.name}</span>
                {isActive && (
                  <span className="absolute bottom-0 left-0 w-full h-[2px] bg-[#DC143C] shadow-[0_0_8px_rgba(220,20,60,0.8)]" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* User Profile & Mobile Toggle */}
        <div className="flex items-center gap-4 ml-auto shrink-0">
          <div className="h-8 w-8 rounded-full bg-[#2A0B12] border border-[#4B0F18] flex items-center justify-center text-[#FF4D6D] shadow-[0_0_10px_rgba(255,77,109,0.2)] cursor-pointer hover:border-[#DC143C]/50 transition-colors">
            <span className="text-xs font-semibold">U</span>
          </div>
          <button 
            className="md:hidden text-slate-400 hover:text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <Menu className="h-6 w-6" />
          </button>
        </div>
      </div>

      {/* Mobile Navigation Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden absolute top-16 left-0 w-full bg-[#120809]/95 backdrop-blur-xl border-b border-[#4B0F18]/50 py-4 px-6 flex flex-col gap-4 shadow-2xl">
          {NAV_LINKS.map((link) => {
            const isActive = location.pathname.startsWith(link.href);
            const Icon = link.icon;
            return (
              <Link
                key={link.name}
                to={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 p-2 rounded-lg ${
                  isActive ? "bg-[#2A0B12] text-[#DC143C]" : "text-slate-400 hover:bg-[#1a0c0e] hover:text-[#FF4D6D]"
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="font-medium">{link.name}</span>
              </Link>
            );
          })}
        </div>
      )}
    </header>
  );
}
