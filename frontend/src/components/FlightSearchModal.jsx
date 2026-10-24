import React from 'react';
import { X, Plane, Clock, ShieldAlert, Check, HelpCircle, AlertCircle } from 'lucide-react';

export default function FlightSearchModal({ isOpen, onClose, searchParams, onAskPolicyQuestion }) {
  if (!isOpen) return null;

  const mockFlights = [
    {
      flightNumber: 'AVA 104',
      aircraft: 'Boeing 787-9 Dreamliner',
      departTime: '08:30 AM',
      arriveTime: '08:45 PM',
      duration: '7h 15m',
      stops: 'Non-stop',
      fares: [
        { name: 'Economy Basic', price: 249, refund: 'Non-refundable', baggage: 'Personal item only' },
        { name: 'Economy Standard', price: 329, refund: 'Future Credit ($125 fee)', baggage: 'Carry-on + 1 Checked bag (23kg)' },
        { name: 'Economy Flex', price: 449, refund: '100% Refundable ($0 fee)', baggage: 'Carry-on + 2 Checked bags' },
        { name: 'Business First', price: 899, refund: '100% Refundable ($0 fee)', baggage: '2 Checked bags (32kg) + Lounge' }
      ]
    },
    {
      flightNumber: 'AVA 208',
      aircraft: 'Airbus A350-900',
      departTime: '01:15 PM',
      arriveTime: '01:30 AM (+1)',
      duration: '7h 15m',
      stops: 'Non-stop',
      fares: [
        { name: 'Economy Basic', price: 279, refund: 'Non-refundable', baggage: 'Personal item only' },
        { name: 'Economy Standard', price: 359, refund: 'Future Credit ($125 fee)', baggage: 'Carry-on + 1 Checked bag (23kg)' },
        { name: 'Economy Flex', price: 489, refund: '100% Refundable ($0 fee)', baggage: 'Carry-on + 2 Checked bags' },
        { name: 'Business First', price: 949, refund: '100% Refundable ($0 fee)', baggage: '2 Checked bags (32kg) + Lounge' }
      ]
    },
    {
      flightNumber: 'AVA 412',
      aircraft: 'Boeing 777-300ER',
      departTime: '06:45 PM',
      arriveTime: '07:05 AM (+1)',
      duration: '7h 20m',
      stops: 'Non-stop',
      fares: [
        { name: 'Economy Basic', price: 239, refund: 'Non-refundable', baggage: 'Personal item only' },
        { name: 'Economy Standard', price: 319, refund: 'Future Credit ($125 fee)', baggage: 'Carry-on + 1 Checked bag (23kg)' },
        { name: 'Economy Flex', price: 439, refund: '100% Refundable ($0 fee)', baggage: 'Carry-on + 2 Checked bags' },
        { name: 'Business First', price: 879, refund: '100% Refundable ($0 fee)', baggage: '2 Checked bags (32kg) + Lounge' }
      ]
    }
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full border border-slate-200 overflow-hidden my-8 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-slate-900 text-white p-6 flex items-center justify-between border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2">
              <Plane className="w-5 h-5 text-aeroblue-400" />
              <h2 className="text-xl font-bold">
                Available Flights: {searchParams?.origin || 'JFK'} → {searchParams?.destination || 'LHR'}
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Date: {searchParams?.departureDate || '2026-11-15'} • Passenger: {searchParams?.passengers || '1 Adult'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Demo Disclaimer Banner */}
        <div className="bg-amber-50 border-b border-amber-200 px-6 py-3 flex items-center gap-3 text-xs text-amber-900">
          <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <div>
            <strong className="font-semibold">Simulated Demonstration Inventory:</strong> The flights and prices listed below are realistic mock data for interface testing and policy evaluation. They do not constitute live bookable tickets.
          </div>
        </div>

        {/* Flight Cards List */}
        <div className="overflow-y-auto p-6 space-y-6 flex-1 bg-slate-50">
          {mockFlights.map((flight) => (
            <div key={flight.flightNumber} className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 hover:shadow-md transition">
              {/* Flight schedule banner */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-4">
                <div className="flex items-center gap-4">
                  <div className="text-center font-bold">
                    <span className="text-2xl text-slate-900">{flight.departTime}</span>
                    <span className="block text-xs font-semibold text-slate-500 uppercase">{searchParams?.origin || 'JFK'}</span>
                  </div>
                  <div className="flex flex-col items-center px-4">
                    <span className="text-xs font-medium text-slate-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" /> {flight.duration}
                    </span>
                    <div className="w-24 sm:w-32 h-0.5 bg-slate-300 relative my-1">
                      <Plane className="w-3.5 h-3.5 text-aeroblue-600 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
                    </div>
                    <span className="text-[11px] font-semibold text-emerald-600">{flight.stops}</span>
                  </div>
                  <div className="text-center font-bold">
                    <span className="text-2xl text-slate-900">{flight.arriveTime}</span>
                    <span className="block text-xs font-semibold text-slate-500 uppercase">{searchParams?.destination || 'LHR'}</span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-xs font-bold text-slate-800 bg-slate-100 px-2.5 py-1 rounded-md">
                    {flight.flightNumber}
                  </span>
                  <span className="block text-xs text-slate-400 mt-1">{flight.aircraft}</span>
                </div>
              </div>

              {/* Fare classes breakdown */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-4">
                {flight.fares.map((fare) => (
                  <div
                    key={fare.name}
                    className={`p-3.5 rounded-lg border flex flex-col justify-between transition ${
                      fare.name === 'Economy Flex'
                        ? 'border-aeroblue-400 bg-aeroblue-50/40 ring-1 ring-aeroblue-400'
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-sm text-slate-900">{fare.name}</span>
                        {fare.name === 'Economy Flex' && (
                          <span className="text-[10px] font-bold bg-aeroblue-600 text-white px-1.5 py-0.5 rounded">
                            Refundable
                          </span>
                        )}
                      </div>
                      <div className="mt-2 text-xl font-extrabold text-slate-900">
                        ${fare.price} <span className="text-xs font-normal text-slate-500">USD</span>
                      </div>
                      <div className="mt-3 space-y-1 text-xs text-slate-600">
                        <p className="flex items-start gap-1">
                          <strong className="text-slate-700">Refund:</strong> {fare.refund}
                        </p>
                        <p className="flex items-start gap-1">
                          <strong className="text-slate-700">Baggage:</strong> {fare.baggage}
                        </p>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => {
                        onClose();
                        onAskPolicyQuestion(`What are the refund and cancellation rules for ${fare.name}?`);
                      }}
                      className="mt-4 w-full py-1.5 px-2 rounded-md bg-slate-100 hover:bg-aeroblue-50 text-slate-700 hover:text-aeroblue-700 text-xs font-semibold flex items-center justify-center gap-1 transition border border-slate-200"
                    >
                      <HelpCircle className="w-3.5 h-3.5" /> Check Policy Rules
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="bg-slate-100 px-6 py-4 flex items-center justify-between border-t border-slate-200 text-xs text-slate-500">
          <span>All fare rules strictly adhere to AeroVista Policy Document AV-POL-2026-REV4</span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-lg transition"
          >
            Close Search
          </button>
        </div>
      </div>
    </div>
  );
}
