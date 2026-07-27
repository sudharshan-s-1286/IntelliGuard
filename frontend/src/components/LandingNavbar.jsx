import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Shield, Menu, X } from 'lucide-react';

export default function LandingNavbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Home', href: '#' },
    { name: 'Architecture', href: '#architecture' },
    { name: 'Features', href: '#features' },
    { name: 'About', href: '#about' },
  ];

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrolled ? 'bg-[#120809]/80 backdrop-blur-md border-b border-[#4B0F18]' : 'bg-transparent py-2'}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <div className="flex items-center gap-2">
            <Shield className="h-8 w-8 text-[#DC143C]" />
            <span className="font-bold text-2xl tracking-tight text-white">IntelliGuard</span>
          </div>
          
          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <a key={link.name} href={link.href} className="text-sm font-medium text-slate-300 hover:text-white transition-colors">
                {link.name}
              </a>
            ))}
          </div>

          <div className="hidden md:flex items-center">
            <Link to="/dashboard" className="bg-[#DC143C] hover:bg-[#FF4D6D] text-white px-6 py-2.5 rounded-md font-medium text-sm transition-all shadow-[0_0_15px_rgba(220,20,60,0.4)] hover:shadow-[0_0_25px_rgba(255,77,109,0.6)]">
              Launch Dashboard
            </Link>
          </div>

          <div className="md:hidden flex items-center">
            <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="text-slate-300 hover:text-white">
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>
      
      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-[#120809] border-b border-[#4B0F18] px-4 pt-2 pb-4 space-y-1 shadow-2xl">
          {navLinks.map((link) => (
            <a 
              key={link.name} 
              href={link.href} 
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 text-base font-medium text-slate-300 hover:text-white hover:bg-[#2A0B12] rounded-md transition-colors"
            >
              {link.name}
            </a>
          ))}
          <Link 
            to="/dashboard" 
            className="block px-3 py-2 text-base font-medium text-[#DC143C] hover:text-[#FF4D6D] hover:bg-[#2A0B12] rounded-md transition-colors"
          >
            Launch Dashboard
          </Link>
        </div>
      )}
    </nav>
  );
}
