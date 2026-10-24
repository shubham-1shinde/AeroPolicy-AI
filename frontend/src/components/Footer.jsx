import React from 'react';
import { Plane, ShieldCheck, HeartHandshake, FileText, Phone, Mail, MapPin } from 'lucide-react';

export default function Footer({ onAskPolicyQuestion }) {
  return (
    <footer className="bg-slate-950 text-slate-400 border-t border-slate-800 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10">
          {/* Brand Info (2 cols) */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg bg-aeroblue-600 flex items-center justify-center">
                <Plane className="w-5 h-5 text-white transform -rotate-45" />
              </div>
              <span className="text-xl font-bold tracking-tight text-white">
                AeroVista <span className="text-aeroblue-400 font-light">Airlines</span>
              </span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed max-w-sm">
              AeroVista Airlines is a fictional air carrier created to benchmark AI grounding, 
              strict tariff compliance, and anti-hallucination guardrails against historical airline customer support rulings.
            </p>
            <div className="pt-2 text-slate-500 space-y-1">
              <p className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5 text-aeroblue-500" /> AeroVista Aviation Center, Dallas, TX 75261</p>
              <p className="flex items-center gap-1.5"><Phone className="w-3.5 h-3.5 text-aeroblue-500" /> General Reservations: 1-800-AEROVISTA</p>
              <p className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5 text-aeroblue-500" /> Appeals Board: appeals@aerovista.example.com</p>
            </div>
          </div>

          {/* Quick Policy Questions */}
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider text-[11px] mb-3">Policy Inquiries</h4>
            <ul className="space-y-2">
              <li>
                <button
                  onClick={() => onAskPolicyQuestion('Can I get a refund after cancelling my ticket?')}
                  className="hover:text-aeroblue-400 text-left transition"
                >
                  Refunds & Cancellations
                </button>
              </li>
              <li>
                <button
                  onClick={() => onAskPolicyQuestion('Am I eligible for a bereavement refund?')}
                  className="hover:text-aeroblue-400 text-left transition"
                >
                  Bereavement & Compassion
                </button>
              </li>
              <li>
                <button
                  onClick={() => onAskPolicyQuestion('What is the baggage allowance?')}
                  className="hover:text-aeroblue-400 text-left transition"
                >
                  Baggage Allowances & Fees
                </button>
              </li>
              <li>
                <button
                  onClick={() => onAskPolicyQuestion('Can I change my flight after booking?')}
                  className="hover:text-aeroblue-400 text-left transition"
                >
                  Flight Change Fees
                </button>
              </li>
              <li>
                <button
                  onClick={() => onAskPolicyQuestion('What are the rules for missed flights?')}
                  className="hover:text-aeroblue-400 text-left transition"
                >
                  No-Show & Standby Policy
                </button>
              </li>
            </ul>
          </div>

          {/* Passenger Rights */}
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider text-[11px] mb-3">Passenger Rights</h4>
            <ul className="space-y-2">
              <li><a href="#policy-explorer" className="hover:text-aeroblue-400 transition">24-Hour Purchase Rule (Sec 3.1)</a></li>
              <li><a href="#policy-explorer" className="hover:text-aeroblue-400 transition">Delays & Cancellations (Sec 8)</a></li>
              <li><a href="#policy-explorer" className="hover:text-aeroblue-400 transition">Check-in Deadlines (Sec 10)</a></li>
              <li><a href="#policy-explorer" className="hover:text-aeroblue-400 transition">Accessibility & Mobility (Sec 11)</a></li>
              <li><a href="#policy-explorer" className="hover:text-aeroblue-400 transition">Unaccompanied Minors (Sec 12)</a></li>
            </ul>
          </div>

          {/* Governance & Compliance */}
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider text-[11px] mb-3">Tariff Governance</h4>
            <div className="space-y-2 text-[11px]">
              <p><strong>Document ID:</strong> AV-POL-2026-REV4</p>
              <p><strong>Policy Version:</strong> 2026.2</p>
              <p><strong>Verification:</strong> SHA-256 Vector Guard</p>
              <p><strong>LLM Engine:</strong> Gemini 2.5 Flash</p>
              <div className="pt-2">
                <span className="inline-block px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-semibold">
                  Air Canada Case Compliant
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Legal Disclaimer Box */}
        <div className="mt-12 pt-8 border-t border-slate-900 text-slate-500 text-[11px] leading-relaxed">
          <p className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80">
            <strong>LEGAL FICTIONAL DISCLAIMER:</strong> AeroVista Airlines, its brand, trademarks, flight schedules, 
            and tariff rules are wholly fictional entities designed specifically for research and testing of policy-grounded 
            conversational AI systems. Nothing on this website constitutes actual passenger carriage or legally binding promises.
          </p>
          <div className="mt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p>© 2026 AeroVista Airlines Demonstrator • Built with React, FastAPI, FAISS & Gemini 2.5 Flash.</p>
            <div className="flex gap-4">
              <span className="hover:text-slate-400 cursor-pointer">Conditions of Carriage</span>
              <span className="hover:text-slate-400 cursor-pointer">Privacy Notice</span>
              <span className="hover:text-slate-400 cursor-pointer">Appeals Dossier</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
