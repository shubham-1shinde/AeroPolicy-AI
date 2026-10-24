import React, { useState } from 'react';
import { PlaneTakeoff, PlaneLanding, Calendar, Users, ArrowRightLeft, Search, Shield, Info, CheckCircle2 } from 'lucide-react';

export default function Hero({ onSearchFlights, onAskPolicyQuestion }) {
  const [activeTab, setActiveTab] = useState('book');
  const [tripType, setTripType] = useState('round');
  const [origin, setOrigin] = useState('JFK');
  const [destination, setDestination] = useState('LHR');
  const [departureDate, setDepartureDate] = useState('2026-11-15');
  const [returnDate, setReturnDate] = useState('2026-11-22');
  const [passengers, setPassengers] = useState('1 Adult');
  const [cabinClass, setCabinClass] = useState('Economy Standard');

  const airports = [
    { code: 'JFK', city: 'New York (JFK)', name: 'John F. Kennedy Intl' },
    { code: 'LHR', city: 'London (LHR)', name: 'Heathrow Airport' },
    { code: 'SFO', city: 'San Francisco (SFO)', name: 'San Francisco Intl' },
    { code: 'HND', city: 'Tokyo (HND)', name: 'Haneda Airport' },
    { code: 'CDG', city: 'Paris (CDG)', name: 'Charles de Gaulle' },
    { code: 'ZRH', city: 'Zurich (ZRH)', name: 'Zurich Airport' },
    { code: 'SYD', city: 'Sydney (SYD)', name: 'Kingsford Smith' },
  ];

  const handleSwapAirports = () => {
    const temp = origin;
    setOrigin(destination);
    setDestination(temp);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    onSearchFlights({
      origin,
      destination,
      departureDate,
      returnDate: tripType === 'round' ? returnDate : null,
      passengers,
      cabinClass,
      tripType
    });
  };

  return (
    <div id="booking-widget" className="relative bg-slate-900 text-white overflow-hidden pb-16">
      {/* Background Graphic / Aviation Gradient */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-900/90 to-aeroblue-950/70" />
        <div className="absolute top-0 right-0 -mr-40 -mt-40 w-96 h-96 rounded-full bg-aeroblue-600/10 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 -mb-20 w-80 h-80 rounded-full bg-cyan-600/10 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-10 lg:pt-14">
        {/* Hero Title & Subtitle */}
        <div className="max-w-3xl mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-aeroblue-500/10 border border-aeroblue-400/30 text-aeroblue-300 text-xs font-semibold uppercase tracking-wider mb-4">
            <Shield className="w-3.5 h-3.5" /> Policy-Grounded Commercial Aviation
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Fly with confidence, <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-aeroblue-400 via-sky-300 to-cyan-300">
              grounded in policy truth.
            </span>
          </h1>
          <p className="mt-4 text-base sm:text-lg text-slate-300 font-normal leading-relaxed">
            Experience world-class flights backed by AeroPolicy AI: our customer assistant verified 
            against official tariff rules to eliminate false promises and policy confusion.
          </p>
        </div>

        {/* Booking Card Widget */}
        <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden text-slate-900">
          {/* Tabs */}
          <div className="flex border-b border-slate-200 bg-slate-50/80 text-sm font-semibold">
            <button
              onClick={() => setActiveTab('book')}
              className={`flex-1 py-4 px-6 text-center border-b-2 transition-colors flex items-center justify-center gap-2 ${
                activeTab === 'book'
                  ? 'border-aeroblue-600 text-aeroblue-700 bg-white font-bold'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <PlaneTakeoff className="w-4 h-4" /> Book a Flight
            </button>
            <button
              onClick={() => setActiveTab('manage')}
              className={`flex-1 py-4 px-6 text-center border-b-2 transition-colors flex items-center justify-center gap-2 ${
                activeTab === 'manage'
                  ? 'border-aeroblue-600 text-aeroblue-700 bg-white font-bold'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Info className="w-4 h-4" /> Manage Booking & Cancellation Rules
            </button>
            <button
              onClick={() => setActiveTab('checkin')}
              className={`flex-1 py-4 px-6 text-center border-b-2 transition-colors flex items-center justify-center gap-2 ${
                activeTab === 'checkin'
                  ? 'border-aeroblue-600 text-aeroblue-700 bg-white font-bold'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <CheckCircle2 className="w-4 h-4" /> Check-in Deadlines
            </button>
          </div>

          {activeTab === 'book' ? (
            <form onSubmit={handleSearchSubmit} className="p-6 sm:p-8 space-y-6">
              {/* Trip type selector */}
              <div className="flex flex-wrap items-center gap-6 text-sm font-medium text-slate-700">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="trip"
                    value="round"
                    checked={tripType === 'round'}
                    onChange={() => setTripType('round')}
                    className="w-4 h-4 text-aeroblue-600 focus:ring-aeroblue-500"
                  />
                  <span>Round Trip</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="trip"
                    value="oneway"
                    checked={tripType === 'oneway'}
                    onChange={() => setTripType('oneway')}
                    className="w-4 h-4 text-aeroblue-600 focus:ring-aeroblue-500"
                  />
                  <span>One Way</span>
                </label>
                <span className="text-slate-400">|</span>
                <span className="text-xs text-slate-500 font-normal">
                  All fares covered by the <strong className="text-slate-700 font-medium">24-Hour Free Cancellation Rule</strong> (Section 3.1)
                </span>
              </div>

              {/* Form grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Origin */}
                <div className="relative border border-slate-300 rounded-xl p-3 hover:border-aeroblue-500 focus-within:border-aeroblue-600 transition bg-slate-50/50">
                  <label className="text-[11px] uppercase font-bold text-slate-500 block">From</label>
                  <div className="flex items-center justify-between mt-1">
                    <select
                      value={origin}
                      onChange={(e) => setOrigin(e.target.value)}
                      className="w-full bg-transparent font-semibold text-slate-900 text-base focus:outline-none cursor-pointer"
                    >
                      {airports.map((a) => (
                        <option key={a.code} value={a.code} disabled={a.code === destination}>
                          {a.city} — {a.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Destination */}
                <div className="relative border border-slate-300 rounded-xl p-3 hover:border-aeroblue-500 focus-within:border-aeroblue-600 transition bg-slate-50/50">
                  <div className="flex items-center justify-between">
                    <label className="text-[11px] uppercase font-bold text-slate-500 block">To</label>
                    <button
                      type="button"
                      onClick={handleSwapAirports}
                      className="text-slate-400 hover:text-aeroblue-600 p-1"
                      title="Swap cities"
                    >
                      <ArrowRightLeft className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <select
                      value={destination}
                      onChange={(e) => setDestination(e.target.value)}
                      className="w-full bg-transparent font-semibold text-slate-900 text-base focus:outline-none cursor-pointer"
                    >
                      {airports.map((a) => (
                        <option key={a.code} value={a.code} disabled={a.code === origin}>
                          {a.city} — {a.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Dates */}
                <div className="border border-slate-300 rounded-xl p-3 hover:border-aeroblue-500 focus-within:border-aeroblue-600 transition bg-slate-50/50">
                  <label className="text-[11px] uppercase font-bold text-slate-500 block flex items-center gap-1">
                    <Calendar className="w-3 h-3 text-aeroblue-600" /> Departure {tripType === 'round' ? '& Return' : ''}
                  </label>
                  <div className="flex items-center gap-2 mt-1">
                    <input
                      type="date"
                      value={departureDate}
                      onChange={(e) => setDepartureDate(e.target.value)}
                      className="w-full bg-transparent font-medium text-slate-800 text-sm focus:outline-none"
                    />
                    {tripType === 'round' && (
                      <>
                        <span className="text-slate-400">-</span>
                        <input
                          type="date"
                          value={returnDate}
                          onChange={(e) => setReturnDate(e.target.value)}
                          className="w-full bg-transparent font-medium text-slate-800 text-sm focus:outline-none"
                        />
                      </>
                    )}
                  </div>
                </div>

                {/* Passengers & Class */}
                <div className="border border-slate-300 rounded-xl p-3 hover:border-aeroblue-500 focus-within:border-aeroblue-600 transition bg-slate-50/50">
                  <label className="text-[11px] uppercase font-bold text-slate-500 block flex items-center gap-1">
                    <Users className="w-3 h-3 text-aeroblue-600" /> Travelers & Class
                  </label>
                  <div className="flex items-center gap-2 mt-1">
                    <select
                      value={cabinClass}
                      onChange={(e) => setCabinClass(e.target.value)}
                      className="w-full bg-transparent font-semibold text-slate-900 text-sm focus:outline-none cursor-pointer"
                    >
                      <option value="Economy Basic">Economy Basic (No Refund/Carry-on)</option>
                      <option value="Economy Standard">Economy Standard (1 Bag, Future Credit)</option>
                      <option value="Economy Flex">Economy Flex (Fully Refundable, 2 Bags)</option>
                      <option value="Business First">Business First (Full Luxury, Refundable)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Action row */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <span className="inline-block w-2 h-2 rounded-full bg-emerald-500" />
                  <span>Fares and baggage allowances displayed strictly per AeroVista Tariff 2026.2</span>
                </div>
                <div className="flex items-center gap-3 w-full sm:w-auto">
                  <button
                    type="button"
                    onClick={() => onAskPolicyQuestion('What is the difference between Economy Basic and Economy Standard refund rules?')}
                    className="text-xs text-aeroblue-700 hover:text-aeroblue-800 underline font-medium"
                  >
                    Compare fare refund policies
                  </button>
                  <button
                    type="submit"
                    className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-aeroblue-600 hover:bg-aeroblue-700 text-white font-bold text-sm shadow-lg shadow-aeroblue-700/30 flex items-center justify-center gap-2 transition hover:-translate-y-0.5"
                  >
                    <Search className="w-4 h-4" /> Search Available Flights
                  </button>
                </div>
              </div>
            </form>
          ) : activeTab === 'manage' ? (
            <div className="p-8 text-slate-700 space-y-4">
              <h3 className="text-lg font-bold text-slate-900">Manage Your Booking or Understand Refund Terms</h3>
              <p className="text-sm text-slate-600">
                To prevent misunderstandings regarding refund eligibility (such as the precedent in the Air Canada ruling), 
                cancellation rights are determined strictly by the fare family of your ticket.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                  <h4 className="font-semibold text-slate-900 text-sm">Need to cancel an existing ticket?</h4>
                  <p className="text-xs text-slate-500 mt-1">
                    Economy Basic tickets are strictly non-refundable. Economy Standard can be cancelled for travel credit up to 2 hours before departure ($125 fee applies).
                  </p>
                  <button
                    onClick={() => onAskPolicyQuestion('Can I get a refund after cancelling my ticket?')}
                    className="mt-3 text-xs font-bold text-aeroblue-600 hover:text-aeroblue-700 flex items-center gap-1"
                  >
                    Ask Chatbot about your fare rules →
                  </button>
                </div>
                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                  <h4 className="font-semibold text-slate-900 text-sm">Compassionate & Bereavement Queries</h4>
                  <p className="text-xs text-slate-500 mt-1">
                    Bereavement discounts require pre-purchase authorization through our phone desk. AeroVista policy forbids retroactive refunds on tickets already purchased.
                  </p>
                  <button
                    onClick={() => onAskPolicyQuestion('Am I eligible for a bereavement refund?')}
                    className="mt-3 text-xs font-bold text-aeroblue-600 hover:text-aeroblue-700 flex items-center gap-1"
                  >
                    Review strict bereavement clause →
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-slate-700 space-y-3">
              <h3 className="text-lg font-bold text-slate-900">Check-In Deadlines & Boarding Gate Closures</h3>
              <p className="text-sm text-slate-600">
                AeroVista enforces firm check-in cutoff times under Section 10 of the Passenger Policy:
              </p>
              <ul className="text-sm space-y-2 list-disc list-inside text-slate-700">
                <li><strong>Online Check-in:</strong> Opens 24 hours prior and closes 60 minutes prior to departure.</li>
                <li><strong>Airport Baggage Drop:</strong> Closes 45 minutes (Domestic) and 60 minutes (International) prior to departure.</li>
                <li><strong>Gate Closures:</strong> Boarding gates close firmly <strong>15 minutes</strong> prior to departure.</li>
              </ul>
              <button
                onClick={() => onAskPolicyQuestion('What are the rules for missed flights?')}
                className="mt-4 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold rounded-lg transition"
              >
                View Missed Flight & No-Show Policies
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
