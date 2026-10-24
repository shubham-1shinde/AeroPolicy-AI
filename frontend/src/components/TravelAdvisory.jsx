import React from 'react';
import { AlertCircle, Clock, ShieldAlert, Sparkles, Check, HelpCircle } from 'lucide-react';

export default function TravelAdvisory({ onAskPolicyQuestion }) {
  return (
    <section id="travel-advisory" className="py-16 bg-slate-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-slate-950/80 rounded-2xl border border-slate-800 p-8 sm:p-10 shadow-2xl">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-8 border-b border-slate-800">
            <div>
              <div className="flex items-center gap-2 text-aeroblue-400 text-xs font-bold uppercase tracking-wider mb-2">
                <Sparkles className="w-4 h-4" /> Operational Integrity & Travel Advisories
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
                Important Passenger Notice & Policy Cutoffs
              </h2>
            </div>
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> Global Flight Operations Normal
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
            {/* Cutoff Notice */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800/80">
              <div className="w-9 h-9 rounded-lg bg-aeroblue-950 border border-aeroblue-700/40 text-aeroblue-400 flex items-center justify-center mb-3">
                <Clock className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-sm text-slate-100">Boarding Gate Cutoffs (Sec 10.3)</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Gates close firmly <strong>15 minutes</strong> before departure. Arriving past cutoff results in automatic No-Show classification under Section 6.
              </p>
              <button
                onClick={() => onAskPolicyQuestion('What are the rules for missed flights?')}
                className="mt-4 text-xs font-semibold text-aeroblue-400 hover:text-aeroblue-300 flex items-center gap-1"
              >
                Learn about No-Show penalties →
              </button>
            </div>

            {/* Force Majeure Notice */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800/80">
              <div className="w-9 h-9 rounded-lg bg-amber-950 border border-amber-700/40 text-amber-400 flex items-center justify-center mb-3">
                <AlertCircle className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-sm text-slate-100">Weather & Air Traffic Delays (Sec 8.2)</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                For cancellations resulting from severe weather or air traffic control, passengers receive free rebooking or travel vouchers; cash refunds apply only to airline-controllable issues.
              </p>
              <button
                onClick={() => onAskPolicyQuestion('What happens if the airline cancels my flight?')}
                className="mt-4 text-xs font-semibold text-aeroblue-400 hover:text-aeroblue-300 flex items-center gap-1"
              >
                Review passenger delay rights →
              </button>
            </div>

            {/* Special Assistance */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800/80">
              <div className="w-9 h-9 rounded-lg bg-indigo-950 border border-indigo-700/40 text-indigo-400 flex items-center justify-center mb-3">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-sm text-slate-100">Mobility & Medical Equipment (Sec 11)</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Wheelchairs and personal mobility devices are stowed free of charge. Notice must be given at least 48 hours prior to departure for special medical accommodations.
              </p>
              <button
                onClick={() => onAskPolicyQuestion('What is the policy for wheelchair assistance and service animals?')}
                className="mt-4 text-xs font-semibold text-aeroblue-400 hover:text-aeroblue-300 flex items-center gap-1"
              >
                View accessibility regulations →
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
