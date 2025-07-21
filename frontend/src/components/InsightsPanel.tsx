"use client";

import React, { useState, useEffect } from "react";
import { Brain, RefreshCw } from "lucide-react";
import { apiClient } from "@/lib/api";

export default function InsightsPanel() {
  const [insights, setInsights] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadInsights = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.getInsights();

      if (response.success) {
        setInsights(response.insights || "No insights available");
      } else {
        setError(response.error || "Failed to load insights");
      }
    } catch (err) {
      setError("An error occurred while loading insights");
      console.error("Error loading insights:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInsights();
  }, []);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Brain className="h-6 w-6 text-primary-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">
            AI Trading Insights
          </h3>
        </div>
        <button
          onClick={loadInsights}
          disabled={loading}
          className="flex items-center text-sm text-primary-600 hover:text-primary-700 disabled:opacity-50"
        >
          <RefreshCw
            className={`h-4 w-4 mr-1 ${loading ? "animate-spin" : ""}`}
          />
          Refresh
        </button>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-danger-50 border border-danger-200 rounded-lg">
          <p className="text-danger-700 text-sm">{error}</p>
        </div>
      )}

      {!loading && !error && insights && (
        <div className="prose prose-sm max-w-none">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-700 whitespace-pre-wrap">{insights}</p>
          </div>
        </div>
      )}

      {!loading && !error && !insights && (
        <div className="text-center py-8">
          <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No journal entries found to analyze</p>
          <p className="text-gray-400 text-sm mt-2">
            Add some journal entries to get AI insights
          </p>
        </div>
      )}
    </div>
  );
}
