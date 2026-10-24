import React from 'react';
import { Plane, ArrowRight, Star } from 'lucide-react';

export default function Destinations({ onSelectDestination }) {
  const destinations = [
    {
      city: 'Tokyo',
      country: 'Japan',
      airport: 'HND',
      price: 689,
      tag: 'Popular',
      image: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80',
      description: 'Daily nonstop flights from JFK and SFO on the Boeing 787-9 Dreamliner.'
    },
    {
      city: 'London',
      country: 'United Kingdom',
      airport: 'LHR',
      price: 499,
      tag: 'Best Value',
      image: 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=800&q=80',
      description: 'Experience 3x daily service to London Heathrow with full baggage flexibility.'
    },
    {
      city: 'Paris',
      country: 'France',
      airport: 'CDG',
      price: 529,
      tag: 'Special Offer',
      image: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=800&q=80',
      description: 'Nonstop evening flights arriving in Paris with lie-flat Business First cabins.'
    },
    {
      city: 'Zurich',
      country: 'Switzerland',
      airport: 'ZRH',
      price: 599,
      tag: 'Alpine Gateway',
      image: 'https://images.unsplash.com/photo-1515488764276-beab7607c1e6?auto=format&fit=crop&w=800&q=80',
      description: 'Direct connections to the Swiss Alps with complimentary ski gear handling on Flex fares.'
    },
    {
      city: 'San Francisco',
      country: 'United States',
      airport: 'SFO',
      price: 249,
      tag: 'Domestic Route',
      image: 'https://images.unsplash.com/photo-1501594907352-04cda38ebc29?auto=format&fit=crop&w=800&q=80',
      description: 'Coast-to-coast flagship transcontinental service with premium Wi-Fi.'
    },
    {
      city: 'Sydney',
      country: 'Australia',
      airport: 'SYD',
      price: 989,
      tag: 'Long Haul',
      image: 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=800&q=80',
      description: 'Ultra-long range Airbus A350-900 service with multi-course dining.'
    }
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12">
          <div>
            <div className="text-xs uppercase font-bold text-aeroblue-600 tracking-wider">
              Featured Global Network
            </div>
            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1">
              Popular AeroVista Destinations
            </h2>
            <p className="text-slate-600 text-sm mt-2">
              Book with guaranteed tariff transparency and 24-hour penalty-free cancellation.
            </p>
          </div>
          <div className="mt-4 md:mt-0 text-xs text-slate-500">
            *All promotional fares subject to AeroVista Conditions of Carriage (Section 2)
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {destinations.map((dest) => (
            <div
              key={dest.city}
              className="group rounded-2xl overflow-hidden border border-slate-200 bg-white shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col"
            >
              {/* Image container */}
              <div className="relative h-48 overflow-hidden">
                <img
                  src={dest.image}
                  alt={dest.city}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent" />
                <span className="absolute top-3 left-3 bg-slate-900/80 backdrop-blur text-white text-[10px] font-bold px-2.5 py-1 rounded-md border border-slate-700">
                  {dest.tag}
                </span>
                <div className="absolute bottom-3 left-3 text-white">
                  <span className="text-xs font-semibold text-aeroblue-300 uppercase">{dest.country}</span>
                  <h3 className="text-xl font-bold">{dest.city} ({dest.airport})</h3>
                </div>
              </div>

              {/* Card body */}
              <div className="p-5 flex-1 flex flex-col justify-between">
                <p className="text-xs text-slate-600 leading-relaxed">
                  {dest.description}
                </p>

                <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] text-slate-400 block uppercase font-medium">Starting from</span>
                    <span className="text-xl font-extrabold text-slate-900">
                      ${dest.price} <span className="text-xs font-normal text-slate-500">USD</span>
                    </span>
                  </div>

                  <button
                    onClick={() => onSelectDestination(dest.airport)}
                    className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-aeroblue-600 hover:text-white text-slate-800 text-xs font-bold transition flex items-center gap-1.5"
                  >
                    <span>View Flights</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
