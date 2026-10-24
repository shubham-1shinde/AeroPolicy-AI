import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import FlightSearchModal from './components/FlightSearchModal';
import PolicyHighlights from './components/PolicyHighlights';
import Destinations from './components/Destinations';
import TravelAdvisory from './components/TravelAdvisory';
import Footer from './components/Footer';
import ChatbotDrawer from './components/ChatbotDrawer';
import { fetchPolicyStatus } from './services/api';

export default function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [externalQuestion, setExternalQuestion] = useState(null);
  const [searchModalOpen, setSearchModalOpen] = useState(false);
  const [searchParams, setSearchParams] = useState(null);
  const [policyStatus, setPolicyStatus] = useState(null);

  useEffect(() => {
    // Check policy status on app load
    fetchPolicyStatus()
      .then(data => setPolicyStatus(data))
      .catch(err => console.log('Policy status fetch error:', err));
  }, []);

  const handleAskPolicyQuestion = (question) => {
    setExternalQuestion(question);
    setIsChatOpen(true);
  };

  const handleSearchFlights = (params) => {
    setSearchParams(params);
    setSearchModalOpen(true);
  };

  const handleSelectDestination = (airportCode) => {
    setSearchParams({
      origin: 'JFK',
      destination: airportCode,
      departureDate: '2026-11-20',
      passengers: '1 Adult',
      cabinClass: 'Economy Standard',
    });
    setSearchModalOpen(true);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      {/* Top Navbar */}
      <Navbar
        onOpenChat={() => setIsChatOpen(true)}
        onSelectPolicyTab={() => {
          const el = document.getElementById('policy-explorer');
          el?.scrollIntoView({ behavior: 'smooth' });
        }}
        policyStatus={policyStatus}
      />

      {/* Main Content Sections */}
      <main className="flex-1">
        {/* Hero & Flight Booking Widget */}
        <Hero
          onSearchFlights={handleSearchFlights}
          onAskPolicyQuestion={handleAskPolicyQuestion}
        />

        {/* Policy Highlights Explorer (Air Canada safe grounding) */}
        <PolicyHighlights
          onAskPolicyQuestion={handleAskPolicyQuestion}
        />

        {/* Featured Global Destinations */}
        <Destinations
          onSelectDestination={handleSelectDestination}
        />

        {/* Operational & Travel Advisories */}
        <TravelAdvisory
          onAskPolicyQuestion={handleAskPolicyQuestion}
        />
      </main>

      {/* Footer */}
      <Footer
        onAskPolicyQuestion={handleAskPolicyQuestion}
      />

      {/* Flight Search Results Demonstration Modal */}
      <FlightSearchModal
        isOpen={searchModalOpen}
        onClose={() => setSearchModalOpen(false)}
        searchParams={searchParams}
        onAskPolicyQuestion={handleAskPolicyQuestion}
      />

      {/* Floating Integrated AI Policy Chatbot */}
      <ChatbotDrawer
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(!isChatOpen)}
        externalQuestion={externalQuestion}
        onClearExternalQuestion={() => setExternalQuestion(null)}
      />
    </div>
  );
}
