import React, { useState } from 'react';
import { Plane, ShieldCheck, Globe, Menu, X, HelpCircle, ChevronDown, Bell } from 'lucide-react';

export default function Navbar({ onOpenChat, onSelectPolicyTab, policyStatus }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 bg-slate-900/95 backdrop-blur border-b border-slate-800 text-white">
      {/* Top micro-bar */}
      <div className="bg-slate-950 px-4 py-1 text-xs text-slate-400 border-b border-slate-800/60 hidden sm:block">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1 text-aeroblue-400 font-medium">
              <ShieldCheck className="w-3.5 h-3.5" /> Fictional Demonstration Airline • Air Canada Safe RAG
            </span>
            <span className="text-slate-500">|</span>
            <span>Policy Version: <strong className="text-slate-300">2026.2 (Active)</strong></span>
          </div>
          <div className="flex items-center gap-4">
            <span className="hover:text-slate-200 cursor-pointer flex items-center gap-1">
              <Globe className="w-3 h-3" /> EN - USD ($)
            </span>
            <span className="hover:text-slate-200 cursor-pointer">Support: 1-800-AEROVISTA</span>
          </div>
        </div>
      </div>

      {/* Main navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Brand Logo */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-aeroblue-500 to-aeroblue-700 flex items-center justify-center shadow-lg shadow-aeroblue-600/30">
              <Plane className="w-6 h-6 text-white transform -rotate-45" />
            </div>
            <div>
              <div className="text-2xl font-bold tracking-tight text-white flex items-center gap-1.5">
                AeroVista <span className="text-aeroblue-400 font-light text-xl">Airlines</span>
              </div>
              <p className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">Precision Aviation & Policy Safety</p>
            </div>
          </div>

          {/* Desktop Nav Links */}
          <nav className="hidden lg:flex items-center gap-8 text-sm font-medium text-slate-200">
            <a href="#booking-widget" className="hover:text-aeroblue-400 transition-colors">Book a Flight</a>
            <a href="#policy-explorer" onClick={onSelectPolicyTab} className="hover:text-aeroblue-400 transition-colors">Manage Booking</a>
            <a href="#travel-advisory" className="hover:text-aeroblue-400 transition-colors">Check-in</a>
            <a href="#travel-advisory" className="hover:text-aeroblue-400 transition-colors">Flight Status</a>
            <a href="#policy-explorer" className="hover:text-aeroblue-400 transition-colors flex items-center gap-1">
              Policy & Fare Rules <span className="bg-aeroblue-900/60 text-aeroblue-300 text-[10px] px-2 py-0.5 rounded-full border border-aeroblue-500/30">Grounded</span>
            </a>
          </nav>

          {/* Right actions */}
          <div className="hidden sm:flex items-center gap-4">
            <button
              onClick={() => onOpenChat()}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-aeroblue-600 hover:bg-aeroblue-500 text-white text-sm font-medium shadow-md shadow-aeroblue-900/40 transition-all hover:shadow-aeroblue-600/30"
            >
              <HelpCircle className="w-4 h-4 text-aeroblue-200" />
              <span>Ask AI Policy Assistant</span>
            </button>
            <button className="text-sm font-medium text-slate-300 hover:text-white px-3 py-2 rounded-lg hover:bg-slate-800 transition">
              Sign In
            </button>
          </div>

          {/* Mobile hamburger */}
          <div className="lg:hidden flex items-center gap-2">
            <button
              onClick={() => onOpenChat()}
              className="p-2 text-aeroblue-400 hover:text-aeroblue-300"
              title="Open Chatbot"
            >
              <HelpCircle className="w-6 h-6" />
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-slate-400 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-slate-900 border-b border-slate-800 px-4 pt-2 pb-6 space-y-3">
          <a
            href="#booking-widget"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-slate-200 hover:text-aeroblue-400 py-2 border-b border-slate-800/80"
          >
            Book a Flight
          </a>
          <a
            href="#policy-explorer"
            onClick={() => { onSelectPolicyTab(); setMobileMenuOpen(false); }}
            className="block text-slate-200 hover:text-aeroblue-400 py-2 border-b border-slate-800/80"
          >
            Manage Booking & Fare Rules
          </a>
          <a
            href="#travel-advisory"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-slate-200 hover:text-aeroblue-400 py-2 border-b border-slate-800/80"
          >
            Check-in & Flight Status
          </a>
          <a
            href="#policy-explorer"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-slate-200 hover:text-aeroblue-400 py-2 border-b border-slate-800/80"
          >
            AeroVista Policy Documentation (v2026.2)
          </a>
          <div className="pt-2">
            <button
              onClick={() => { onOpenChat(); setMobileMenuOpen(false); }}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-aeroblue-600 text-white font-medium"
            >
              <HelpCircle className="w-4 h-4" /> Open Policy Chatbot
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
