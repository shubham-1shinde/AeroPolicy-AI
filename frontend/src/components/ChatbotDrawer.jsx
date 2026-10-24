import React, { useState, useRef, useEffect } from 'react';
import { 
  MessageSquare, X, Send, Bot, User, ShieldCheck, AlertCircle, 
  RotateCcw, Sparkles, ChevronDown, ChevronUp, BookOpen, ExternalLink,
  Info, CheckCircle, RefreshCw, HelpCircle
} from 'lucide-react';
import { sendChatMessage } from '../services/api';

const SUGGESTED_QUESTIONS = [
  'Can I get a refund after cancelling my ticket?',
  'What is the baggage allowance?',
  'Can I change my flight after booking?',
  'What happens if the airline cancels my flight?',
  'Am I eligible for a bereavement refund?',
  'What are the rules for missed flights?',
];

export default function ChatbotDrawer({ isOpen, onClose, externalQuestion, onClearExternalQuestion }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      text: "Hello! I am AeroPolicy AI, the official policy assistant for AeroVista Airlines. I answer customer questions strictly grounded in our verified tariff policy document (`AV-POL-2026-REV4`). I never guess, fabricate exceptions, or promise unapproved refunds.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      grounded: true,
      sources: []
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorState, setErrorState] = useState(null);
  const [expandedCitations, setExpandedCitations] = useState({});
  const [selectedSourceDetail, setSelectedSourceDetail] = useState(null);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Handle external question passed from website buttons
  useEffect(() => {
    if (externalQuestion) {
      handleSendMessage(externalQuestion);
      onClearExternalQuestion();
    }
  }, [externalQuestion]);

  const toggleCitation = (msgId) => {
    setExpandedCitations(prev => ({
      ...prev,
      [msgId]: !prev[msgId]
    }));
  };

  const handleSendMessage = async (textToSend = null) => {
    const query = (textToSend || inputText).trim();
    if (!query || isLoading) return;

    setErrorState(null);
    const userMsgId = `user_${Date.now()}`;
    const userMsg = {
      id: userMsgId,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInputText('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(query);
      const assistantMsg = {
        id: `assistant_${Date.now()}`,
        sender: 'assistant',
        text: response.answer,
        grounded: response.grounded,
        sources: response.sources || [],
        needs_clarification: response.needs_clarification,
        suggested_question: response.suggested_question,
        policy_version: response.policy_version,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      setErrorState({
        message: err.message || 'Failed to connect to the policy engine.',
        lastQuery: query
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: 'welcome_reset',
        sender: 'assistant',
        text: "Chat cleared. I am ready to answer any questions regarding AeroVista Airlines policies, fare rules, baggage allowances, or cancellation terms.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        grounded: true,
        sources: []
      }
    ]);
    setErrorState(null);
  };

  const renderFormattedText = (text) => {
    // Basic markdown support for bold, headings, bullets
    const lines = text.split('\n');
    return (
      <div className="space-y-2 text-sm leading-relaxed">
        {lines.map((line, idx) => {
          if (line.startsWith('### ')) {
            return (
              <h4 key={idx} className="font-bold text-slate-900 text-sm mt-3 pb-1 border-b border-slate-200">
                {line.replace('### ', '')}
              </h4>
            );
          }
          if (line.startsWith('## ')) {
            return (
              <h3 key={idx} className="font-extrabold text-slate-900 text-base mt-3">
                {line.replace('## ', '')}
              </h3>
            );
          }
          if (line.startsWith('- ') || line.startsWith('* ')) {
            return (
              <li key={idx} className="list-disc list-inside text-slate-700 ml-2">
                <span dangerouslySetInnerHTML={{ __html: formatBold(line.substring(2)) }} />
              </li>
            );
          }
          if (line.trim().startsWith('> ')) {
            return (
              <blockquote key={idx} className="border-l-4 border-amber-400 bg-amber-50 p-2 text-xs italic text-amber-900 rounded-r">
                {line.replace('> ', '')}
              </blockquote>
            );
          }
          if (!line.trim()) {
            return <div key={idx} className="h-1" />;
          }
          return (
            <p key={idx} dangerouslySetInnerHTML={{ __html: formatBold(line) }} />
          );
        })}
      </div>
    );
  };

  const formatBold = (str) => {
    return str.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  };

  return (
    <>
      {/* Floating Trigger Button (Bottom Right) */}
      {!isOpen && (
        <button
          onClick={onClose} // acts as toggle
          className="fixed bottom-6 right-6 z-40 flex items-center gap-3 px-5 py-3.5 rounded-full bg-gradient-to-r from-aeroblue-600 to-aeroblue-700 hover:from-aeroblue-500 hover:to-aeroblue-600 text-white font-bold shadow-2xl shadow-aeroblue-900/50 hover:shadow-aeroblue-600/40 transition-all duration-300 transform hover:-translate-y-1 group"
        >
          <div className="relative">
            <Bot className="w-6 h-6 text-white group-hover:scale-110 transition-transform" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-aeroblue-700 animate-pulse" />
          </div>
          <div className="text-left hidden sm:block">
            <span className="block text-xs uppercase tracking-wider font-extrabold text-aeroblue-200">AeroVista AI</span>
            <span className="text-sm font-semibold">Policy Assistant</span>
          </div>
        </button>
      )}

      {/* Slide-over / Modal Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-0 right-0 sm:bottom-6 sm:right-6 z-50 w-full sm:w-[460px] h-[92vh] sm:h-[680px] bg-white rounded-t-2xl sm:rounded-2xl shadow-2xl border border-slate-300 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Header */}
          <div className="bg-slate-900 text-white px-5 py-4 flex items-center justify-between border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-aeroblue-600 flex items-center justify-center text-white shadow-md shadow-aeroblue-600/40">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-sm tracking-tight">AeroPolicy Assistant</h3>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                    Live RAG
                  </span>
                </div>
                <p className="text-[11px] text-slate-400">Policy Document: AV-POL-2026-REV4 (v2026.2)</p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={handleClearChat}
                className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
                title="Clear conversation"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={onClose}
                className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
                title="Close chat"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Air Canada Precedent Safety Banner */}
          <div className="bg-aeroblue-50 px-4 py-2 border-b border-aeroblue-100 flex items-center gap-2 text-[11px] text-aeroblue-900 font-medium">
            <ShieldCheck className="w-3.5 h-3.5 text-aeroblue-600 flex-shrink-0" />
            <span>Anti-Hallucination active: Grounded strictly in official published tariff rules.</span>
          </div>

          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-slate-50">
            {messages.map((msg) => {
              const isAssistant = msg.sender === 'assistant';
              return (
                <div
                  key={msg.id}
                  className={`flex flex-col ${isAssistant ? 'items-start' : 'items-end'}`}
                >
                  <div className="flex items-center gap-1.5 text-[10px] text-slate-400 mb-1 px-1">
                    <span>{isAssistant ? 'AeroPolicy AI' : 'You'}</span>
                    <span>•</span>
                    <span>{msg.timestamp}</span>
                  </div>

                  <div
                    className={`max-w-[88%] rounded-2xl p-4 shadow-sm ${
                      isAssistant
                        ? 'bg-white border border-slate-200 text-slate-800'
                        : 'bg-aeroblue-600 text-white font-normal'
                    }`}
                  >
                    {/* Assistant Verification Pill */}
                    {isAssistant && msg.id !== 'welcome' && msg.id !== 'welcome_reset' && (
                      <div className="mb-2 pb-2 border-b border-slate-100 flex items-center justify-between">
                        {msg.grounded ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                            <CheckCircle className="w-3 h-3 text-emerald-600" /> Grounded in Policy
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-300">
                            <AlertCircle className="w-3 h-3 text-amber-600" /> Policy Abstention — Unverified
                          </span>
                        )}
                        <span className="text-[10px] text-slate-400">AeroVista Tariffs</span>
                      </div>
                    )}

                    {/* Message Body */}
                    {isAssistant ? renderFormattedText(msg.text) : <p className="text-sm">{msg.text}</p>}

                    {/* Clarification prompt */}
                    {isAssistant && msg.needs_clarification && msg.suggested_question && (
                      <div className="mt-3 p-2.5 rounded-lg bg-sky-50 border border-sky-200 text-xs text-sky-900">
                        <strong className="block font-semibold mb-1">Clarification Required:</strong>
                        <button
                          onClick={() => handleSendMessage(msg.suggested_question)}
                          className="text-left font-medium text-aeroblue-700 hover:underline"
                        >
                          → {msg.suggested_question}
                        </button>
                      </div>
                    )}

                    {/* Source Citations Accordion */}
                    {isAssistant && msg.sources && msg.sources.length > 0 && (
                      <div className="mt-3 pt-2.5 border-t border-slate-100">
                        <button
                          onClick={() => toggleCitation(msg.id)}
                          className="flex items-center justify-between w-full text-left text-xs font-semibold text-slate-600 hover:text-aeroblue-600 transition"
                        >
                          <span className="flex items-center gap-1.5">
                            <BookOpen className="w-3.5 h-3.5 text-aeroblue-600" />
                            <span>Supporting Policy Sources ({msg.sources.length})</span>
                          </span>
                          {expandedCitations[msg.id] ? (
                            <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
                          ) : (
                            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                          )}
                        </button>

                        {expandedCitations[msg.id] && (
                          <div className="mt-2 space-y-2 pt-1">
                            {msg.sources.map((src, idx) => (
                              <div
                                key={idx}
                                className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs"
                              >
                                <div className="flex items-center justify-between font-bold text-slate-800">
                                  <span>{src.section || 'Policy Clause'}</span>
                                  <span className="text-[10px] text-slate-400 font-normal">
                                    {src.document}
                                  </span>
                                </div>
                                <p className="mt-1 text-slate-600 italic font-mono text-[11px] bg-white p-2 rounded border border-slate-100">
                                  "{src.excerpt}"
                                </p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex items-start gap-2">
                <div className="w-7 h-7 rounded-lg bg-aeroblue-600 flex items-center justify-center text-white text-xs">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-3.5 shadow-sm">
                  <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
                    <RefreshCw className="w-3.5 h-3.5 text-aeroblue-600 animate-spin" />
                    <span>Verifying against AeroVista policy document...</span>
                  </div>
                </div>
              </div>
            )}

            {/* Error & Retry State */}
            {errorState && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs flex flex-col gap-2">
                <div className="flex items-center gap-2 font-bold">
                  <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                  <span>Connection or Verification Error</span>
                </div>
                <p>{errorState.message}</p>
                <button
                  onClick={() => handleSendMessage(errorState.lastQuery)}
                  className="self-start px-3 py-1 bg-rose-600 hover:bg-rose-700 text-white rounded-md font-semibold text-xs transition"
                >
                  Retry Question
                </button>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Questions Carousel / Pill Bar */}
          <div className="bg-white border-t border-slate-200 px-4 py-2.5">
            <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider mb-1.5">
              Suggested Policy Inquiries:
            </div>
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 custom-scrollbar">
              {SUGGESTED_QUESTIONS.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(q)}
                  disabled={isLoading}
                  className="whitespace-nowrap px-2.5 py-1 rounded-full bg-slate-100 hover:bg-aeroblue-50 hover:text-aeroblue-700 text-slate-700 text-xs font-medium transition border border-slate-200 disabled:opacity-50 flex-shrink-0"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="p-3 bg-white border-t border-slate-200 flex items-center gap-2"
          >
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Ask any policy question (e.g. refund, baggage, delay)..."
              disabled={isLoading}
              className="flex-1 bg-slate-100 text-slate-900 placeholder:text-slate-400 px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-aeroblue-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!inputText.trim() || isLoading}
              className="p-2.5 rounded-xl bg-aeroblue-600 hover:bg-aeroblue-700 disabled:bg-slate-300 text-white transition shadow-sm"
              title="Send message"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
