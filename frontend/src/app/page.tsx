"use client";

import React, { useState } from "react";
import { Plus, BookOpen, Brain } from "lucide-react";
import Dashboard from "@/components/Dashboard";
import TradeTable from "@/components/TradeTable";
import TradeModal from "@/components/TradeModal";
import JournalModal from "@/components/JournalModal";
import JournalTable from "@/components/JournalTable";
import InsightsPanel from "@/components/InsightsPanel";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { UserMenu } from "@/components/auth/UserMenu";
import { LandingPage } from "@/components/LandingPage";
import { useAuth } from "@/contexts/AuthContext";
import { Trade } from "@/types";

export default function HomePage() {
  const { user, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState<
    "dashboard" | "trades" | "journal" | "insights"
  >("dashboard");
  const [tradeModalOpen, setTradeModalOpen] = useState(false);
  const [journalModalOpen, setJournalModalOpen] = useState(false);
  const [selectedTrade, setSelectedTrade] = useState<Trade | null>(null);
  const [tradesTableKey, setTradesTableKey] = useState(0);
  const [journalTableKey, setJournalTableKey] = useState(0);

  // Show landing page if user is not authenticated
  if (!isAuthenticated) {
    return <LandingPage />;
  }

  const handleTradeCreated = () => {
    // Only refresh trades table, stay on current tab
    setActiveTab("trades");
    setTradesTableKey((k) => k + 1); // force TradeTable to reload
    // Optionally, you can trigger a state update or use a ref to reload trades if needed
  };

  const handleJournalCreated = () => {
    // Refresh journal table
    setJournalTableKey((k) => k + 1);
  };

  const handleTradeSelected = (trade: Trade) => {
    setSelectedTrade(trade);
    setJournalModalOpen(true);
  };

  const tabs = [
    { id: "dashboard", label: "Dashboard", icon: null },
    { id: "trades", label: "Trades", icon: Plus },
    { id: "journal", label: "Journal", icon: BookOpen },
    { id: "insights", label: "AI Insights", icon: Brain },
  ];

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <h1 className="text-2xl font-bold text-gray-900">TradeDashPro</h1>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setTradeModalOpen(true)}
                  className="btn-primary flex items-center"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Trade
                </button>
                <button
                  onClick={() => {
                    setSelectedTrade(null);
                    setJournalModalOpen(true);
                  }}
                  className="btn-secondary flex items-center"
                >
                  <BookOpen className="h-4 w-4 mr-2" />
                  Add Journal
                </button>
                <UserMenu />
              </div>
            </div>
          </div>
        </header>

        {/* Navigation Tabs */}
        <nav className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === tab.id
                        ? "border-primary-500 text-primary-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    {Icon && <Icon className="h-4 w-4 mr-2" />}
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {activeTab === "dashboard" && <Dashboard />}

          {activeTab === "trades" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">
                  Trade History
                </h2>
                <button
                  onClick={() => setTradeModalOpen(true)}
                  className="btn-primary flex items-center"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Trade
                </button>
              </div>
              <TradeTable
                key={tradesTableKey}
                onTradeSelected={handleTradeSelected}
                onTradeDeleted={handleTradeCreated}
              />
            </div>
          )}

          {activeTab === "journal" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">
                  Trading Journal
                </h2>
                <button
                  onClick={() => {
                    setSelectedTrade(null);
                    setJournalModalOpen(true);
                  }}
                  className="btn-primary flex items-center"
                >
                  <BookOpen className="h-4 w-4 mr-2" />
                  Add Journal Entry
                </button>
              </div>
              <JournalTable
                key={journalTableKey}
                onJournalDeleted={handleJournalCreated}
              />
            </div>
          )}

          {activeTab === "insights" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">
                AI Trading Insights
              </h2>
              <InsightsPanel />
            </div>
          )}
        </main>

        {/* Modals */}
        <TradeModal
          isOpen={tradeModalOpen}
          onClose={() => setTradeModalOpen(false)}
          onTradeCreated={handleTradeCreated}
        />

        <JournalModal
          isOpen={journalModalOpen}
          onClose={() => setJournalModalOpen(false)}
          onJournalCreated={handleJournalCreated}
          selectedTrade={selectedTrade}
        />
      </div>
    </ProtectedRoute>
  );
}
