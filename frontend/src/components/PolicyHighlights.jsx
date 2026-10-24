import React, { useState } from 'react';
import { ShieldCheck, Luggage, HeartHandshake, AlertTriangle, Clock, RefreshCw, ChevronRight, FileText, BookOpen } from 'lucide-react';

export default function PolicyHighlights({ onAskPolicyQuestion }) {
  const [selectedTopic, setSelectedTopic] = useState('bereavement');

  const policyTopics = [
    {
      id: 'bereavement',
      title: 'Bereavement & Compassionate Fares',
      section: 'Section 4.1 - 4.3',
      badge: 'Air Canada Safety Safeguard',
      badgeColor: 'bg-rose-100 text-rose-800 border-rose-300',
      icon: HeartHandshake,
      summary: 'Bereavement discounts must be booked prior to ticket purchase via telephone reservations. The airline does NOT issue retroactive bereavement refunds or price adjustments for tickets already purchased.',
      details: [
        'Discount must be requested PRIOR to ticket payment and issuance.',
        'Requires death certificate or physician letter within 7 days.',
        'Tickets already purchased remain strictly bound by their original fare rules.',
        'Automated assistants and agents cannot promise cash refunds after purchase.'
      ],
      suggestedQuery: 'Am I eligible for a bereavement refund?'
    },
    {
      id: 'cancellation',
      title: 'Ticket Cancellation & Refundability',
      section: 'Section 2.1 - 2.4',
      badge: 'Fare Conditions',
      badgeColor: 'bg-blue-100 text-blue-800 border-blue-300',
      icon: RefreshCw,
      summary: 'Refund eligibility is determined strictly by the purchased fare class. Economy Basic is non-refundable; Economy Flex and Business First are fully refundable.',
      details: [
        'Economy Basic: Non-refundable under all standard circumstances.',
        'Economy Standard: Cancellation for 12-month travel voucher ($125 fee applies).',
        'Economy Flex: 100% refundable to original payment up to 2h prior to flight.',
        'Business First: 100% refundable at any time with $0 penalty.'
      ],
      suggestedQuery: 'Can I get a refund after cancelling my ticket?'
    },
    {
      id: 'baggage',
      title: 'Baggage Allowances & Dimensions',
      section: 'Section 7.1 - 7.3',
      badge: 'Standard Limits',
      badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-300',
      icon: Luggage,
      summary: 'Strict size limits apply across all cabins. Personal item (40x30x15cm) free for all. Carry-on (55x40x23cm, max 10kg) requires Economy Standard or higher.',
      details: [
        'Personal item: 40 x 30 x 15 cm (16 x 12 x 6 in) must fit under seat.',
        'Carry-on bag: 55 x 40 x 23 cm (max 10 kg). Extra fee on Economy Basic ($35).',
        'Checked baggage: 1 included in Standard (23kg), 2 in Flex (23kg), 2 in Business (32kg).',
        'Overweight bag (23.1kg - 32kg): $100 USD surcharge per bag.'
      ],
      suggestedQuery: 'What is the baggage allowance?'
    },
    {
      id: 'cooling',
      title: '24-Hour Purchase Guarantee',
      section: 'Section 3.1',
      badge: 'Full Consumer Protection',
      badgeColor: 'bg-indigo-100 text-indigo-800 border-indigo-300',
      icon: Clock,
      summary: 'Full 100% refund without fees if cancelled within 24 hours of booking, provided the flight is scheduled at least 7 days (168 hours) in advance.',
      details: [
        'Mandatory 24-hour cooling-off window for direct digital bookings.',
        'Must be booked at least 7 days before departure.',
        'Ticket must be unused and unredeemed.',
        'Processed directly to the original method of payment.'
      ],
      suggestedQuery: 'Can I cancel my flight within 24 hours for a full refund?'
    },
    {
      id: 'delays',
      title: 'Delays & Airline Cancellations',
      section: 'Section 8.1 - 8.2',
      badge: 'Passenger Rights',
      badgeColor: 'bg-amber-100 text-amber-800 border-amber-300',
      icon: AlertTriangle,
      summary: 'Controllable airline cancellations entitle passengers to a 100% refund or rebooking. Force majeure weather delays receive travel credits and rebooking.',
      details: [
        'Carrier cancellations: Rebooking or 100% full cash refund on all fare classes.',
        'Over 3-hour delay: Meal vouchers provided.',
        'Overnight controllable delays: Hotel accommodations and airport transfer included.',
        'Weather & Force Majeure: Rebooking or Future Travel Credit (no cash refund).'
      ],
      suggestedQuery: 'What happens if the airline cancels my flight?'
    }
  ];

  const currentTopic = policyTopics.find(t => t.id === selectedTopic) || policyTopics[0];

  return (
    <section id="policy-explorer" className="py-20 bg-slate-100 border-t border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-200 text-slate-700 text-xs font-bold uppercase tracking-wider mb-3">
            <BookOpen className="w-3.5 h-3.5 text-aeroblue-600" /> Grounded Policy Library
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Clear, Verified Passenger Rights
          </h2>
          <p className="mt-3 text-base text-slate-600">
            AeroVista operates on total tariff transparency. Explore verified policy terms or ask our AI assistant 
            which is restricted to factual clauses from our official policy document.
          </p>
        </div>

        {/* Policy Interactive Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Navigation Pills (Left 5 Cols) */}
          <div className="lg:col-span-5 space-y-3">
            {policyTopics.map((topic) => {
              const Icon = topic.icon;
              const isSelected = selectedTopic === topic.id;
              return (
                <div
                  key={topic.id}
                  onClick={() => setSelectedTopic(topic.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-white border-aeroblue-500 shadow-md ring-2 ring-aeroblue-500/20 translate-x-1'
                      : 'bg-white/80 border-slate-200 hover:bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        isSelected ? 'bg-aeroblue-600 text-white' : 'bg-slate-100 text-slate-600'
                      }`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-bold text-sm text-slate-900">{topic.title}</h3>
                        <span className="text-xs text-slate-400 font-medium">{topic.section}</span>
                      </div>
                    </div>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${topic.badgeColor}`}>
                      {topic.badge}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Detailed Policy Card (Right 7 Cols) */}
          <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 shadow-lg p-6 sm:p-8">
            <div className="flex items-center justify-between pb-6 border-b border-slate-100">
              <div>
                <span className="text-xs font-bold text-aeroblue-600 tracking-wider uppercase">
                  AeroVista Tariff Document • {currentTopic.section}
                </span>
                <h3 className="text-2xl font-extrabold text-slate-900 mt-1">{currentTopic.title}</h3>
              </div>
              <span className={`text-xs font-bold px-3 py-1 rounded-full border ${currentTopic.badgeColor}`}>
                {currentTopic.badge}
              </span>
            </div>

            <p className="mt-6 text-sm text-slate-700 leading-relaxed font-normal bg-slate-50 p-4 rounded-xl border border-slate-100">
              {currentTopic.summary}
            </p>

            <div className="mt-6">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Key Policy Rules:</h4>
              <ul className="space-y-2.5">
                {currentTopic.details.map((detail, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-sm text-slate-700">
                    <ShieldCheck className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Direct query trigger */}
            <div className="mt-8 pt-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="text-xs text-slate-500">
                Want to test how our AI answers this?
              </div>
              <button
                onClick={() => onAskPolicyQuestion(currentTopic.suggestedQuery)}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-aeroblue-600 text-white font-semibold text-xs transition flex items-center justify-center gap-2 shadow-sm"
              >
                <span>Ask AI: "{currentTopic.suggestedQuery}"</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
