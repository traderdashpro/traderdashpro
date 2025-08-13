"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  Brain,
  RefreshCw,
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  Target,
  CheckCircle,
  XCircle,
  Clock,
  BarChart3,
  Search,
  ThumbsUp,
  ArrowUp,
  Heart,
  List,
  Zap,
  FileText,
  Crown,
  Calendar,
  Lock,
  Sparkles,
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { AIInsights } from "@/types";

interface InsightSection {
  title: string;
  content: string[];
  icon: React.ReactNode;
  type:
    | "patterns"
    | "strengths"
    | "improvements"
    | "emotions"
    | "performance"
    | "recommendations";
}

interface InsightsData {
  key_patterns?: string[];
  strengths?: string[];
  areas_for_improvement?: string[];
  emotional_state_analysis?: string;
  trading_performance_insights?: string;
  recommendations?: string[];
}

interface PlanInfo {
  plan: string;
  can_get_insights: boolean | null;
  last_insights_date?: string;
  next_available_date?: string;
  insights_created_at?: string;
}

export default function InsightsPanel() {
  const [insights, setInsights] = useState<InsightsData | null>(null);
  const [planInfo, setPlanInfo] = useState<PlanInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isStoredInsights, setIsStoredInsights] = useState(false);
  const [hasCheckedStored, setHasCheckedStored] = useState(false);

  // Check for stored insights on component mount
  useEffect(() => {
    checkForStoredInsights();
  }, []);

  // Force re-render when planInfo changes to update button states
  useEffect(() => {
    console.log("PlanInfo changed:", planInfo);
  }, [planInfo]);

  const checkForStoredInsights = async () => {
    try {
      const response = await apiClient.getStoredInsights();
      if (response.success) {
        setInsights(response.insights || null);
        setPlanInfo({
          plan: response.plan || "free",
          can_get_insights: response.can_get_insights ?? false,
          last_insights_date: response.last_insights_date,
          next_available_date: response.next_available_date,
          insights_created_at: response.insights_created_at,
        });
        setIsStoredInsights(true);
      }
    } catch (err: any) {
      // Check if this is a 404 with plan info (first-time user)
      if (err.message?.includes("404") && err.response?.data) {
        const errorData = err.response.data;
        if (errorData.plan) {
          // First-time user - set plan info but no insights
          setPlanInfo({
            plan: errorData.plan || "free",
            can_get_insights: errorData.can_get_insights ?? false,
            last_insights_date: errorData.last_insights_date,
            next_available_date: errorData.next_available_date,
          });
          setInsights(null);
          setIsStoredInsights(false);
        }
      }
      console.log("No stored insights available");
    } finally {
      setHasCheckedStored(true);
    }
  };

  const getNewInsights = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log("Getting new AI insights...");
      const response = await apiClient.getInsights();
      console.log("API Response:", response);

      if (response.success) {
        console.log("Insights data:", response.insights);
        console.log("Plan info from response:", {
          plan: response.plan,
          can_get_insights: response.can_get_insights,
          last_insights_date: response.last_insights_date,
          next_available_date: response.next_available_date,
        });

        // Update both insights and plan info immediately
        setInsights(response.insights || null);
        setPlanInfo({
          plan: response.plan || "free",
          can_get_insights: response.can_get_insights ?? false,
          last_insights_date: response.last_insights_date,
          next_available_date: response.next_available_date,
          insights_created_at: response.insights_created_at,
        });

        setIsStoredInsights(false);
      } else {
        console.error("API returned error:", response.error);
        setError(response.error || "Failed to get insights");
      }
    } catch (err: any) {
      console.error("Error getting insights:", err);
      setError("An error occurred while getting insights");
    } finally {
      setLoading(false);
    }
  };

  // Convert JSON insights to sections
  const parseInsights = (insightsData: InsightsData): InsightSection[] => {
    const sections: InsightSection[] = [];

    // Key Patterns
    if (insightsData.key_patterns && insightsData.key_patterns.length > 0) {
      sections.push({
        title: "Key Patterns",
        content: insightsData.key_patterns,
        icon: <Search className="h-5 w-5" />,
        type: "patterns",
      });
    }

    // Strengths
    if (insightsData.strengths && insightsData.strengths.length > 0) {
      sections.push({
        title: "Strengths",
        content: insightsData.strengths,
        icon: <ThumbsUp className="h-5 w-5" />,
        type: "strengths",
      });
    }

    // Areas for Improvement
    if (
      insightsData.areas_for_improvement &&
      insightsData.areas_for_improvement.length > 0
    ) {
      sections.push({
        title: "Areas for Improvement",
        content: insightsData.areas_for_improvement,
        icon: <ArrowUp className="h-5 w-5" />,
        type: "improvements",
      });
    }

    // Emotional State Analysis
    if (insightsData.emotional_state_analysis) {
      sections.push({
        title: "Emotional State Analysis",
        content: [insightsData.emotional_state_analysis],
        icon: <Heart className="h-5 w-5" />,
        type: "emotions",
      });
    }

    // Trading Performance Insights
    if (insightsData.trading_performance_insights) {
      sections.push({
        title: "Performance Insights",
        content: [insightsData.trading_performance_insights],
        icon: <List className="h-5 w-5" />,
        type: "performance",
      });
    }

    // Recommendations
    if (
      insightsData.recommendations &&
      insightsData.recommendations.length > 0
    ) {
      sections.push({
        title: "Recommendations",
        content: insightsData.recommendations,
        icon: <Lightbulb className="h-5 w-5" />,
        type: "recommendations",
      });
    }

    return sections;
  };

  const getSectionStyles = (type: InsightSection["type"]) => {
    switch (type) {
      case "patterns":
        return {
          container: "bg-blue-50 border-blue-200",
          icon: "text-blue-600",
          title: "text-blue-800",
          content: "text-blue-700",
        };
      case "strengths":
        return {
          container: "bg-green-50 border-green-200",
          icon: "text-green-600",
          title: "text-green-800",
          content: "text-green-700",
        };
      case "improvements":
        return {
          container: "bg-orange-50 border-orange-200",
          icon: "text-orange-600",
          title: "text-orange-800",
          content: "text-orange-700",
        };
      case "emotions":
        return {
          container: "bg-pink-50 border-pink-200",
          icon: "text-pink-600",
          title: "text-pink-800",
          content: "text-pink-700",
        };
      case "performance":
        return {
          container: "bg-purple-50 border-purple-200",
          icon: "text-purple-600",
          title: "text-purple-800",
          content: "text-purple-700",
        };
      case "recommendations":
        return {
          container: "bg-indigo-50 border-indigo-200",
          icon: "text-indigo-600",
          title: "text-indigo-800",
          content: "text-indigo-700",
        };
      default:
        return {
          container: "bg-gray-50 border-gray-200",
          icon: "text-gray-600",
          title: "text-gray-800",
          content: "text-gray-700",
        };
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getPlanDisplayName = (plan: string) => {
    switch (plan) {
      case "free":
        return "Free Plan";
      case "premium":
        return "Premium Plan";
      case "pro":
        return "Pro Plan";
      default:
        return plan;
    }
  };

  const getDaysUntilNext = () => {
    if (!planInfo?.next_available_date) return null;
    const nextDate = new Date(planInfo.next_available_date);
    const now = new Date();
    const diffTime = nextDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };

  const parsedSections = insights ? parseInsights(insights) : [];
  const daysUntilNext = getDaysUntilNext();

  // Calculate canRefresh using useMemo for better reactivity
  const canRefresh = useMemo(() => {
    if (!planInfo) return false;

    const canGetInsights = planInfo.can_get_insights === true;
    const hasNextDate = planInfo.next_available_date;
    const isNextDateReached =
      !hasNextDate ||
      (planInfo.next_available_date &&
        new Date(planInfo.next_available_date) <= new Date());

    console.log("canRefresh calculation:", {
      canGetInsights,
      hasNextDate,
      isNextDateReached,
      result: canGetInsights && isNextDateReached,
    });

    return canGetInsights && isNextDateReached;
  }, [planInfo]);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Brain className="h-6 w-6 text-primary-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">
            AI Trading Insights
          </h3>
          {planInfo && (
            <div className="ml-3 flex items-center">
              {planInfo.plan === "free" ? (
                <div className="flex items-center text-sm text-gray-600">
                  <Crown className="h-4 w-4 mr-1" />
                  {getPlanDisplayName(planInfo.plan)}
                </div>
              ) : (
                <div className="flex items-center text-sm text-yellow-600">
                  <Crown className="h-4 w-4 mr-1" />
                  {getPlanDisplayName(planInfo.plan)}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Last Pulled Date */}
        {planInfo?.last_insights_date && (
          <div className="flex items-center text-sm text-gray-500">
            <Calendar className="h-4 w-4 mr-1" />
            <span>Last pulled: {formatDate(planInfo.last_insights_date)}</span>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-600 mr-2" />
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Analyzing your trading patterns...</p>
          </div>
        </div>
      )}

      {/* No Insights Available - Show CTA */}
      {!loading && !error && !insights && hasCheckedStored && (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <Brain className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">
              Get AI-Powered Insights
            </h4>
            <p className="text-gray-500 mb-6">
              Improve your performance by getting intelligent insights and
              analysis through AI
            </p>
            <button
              onClick={getNewInsights}
              disabled={loading || !canRefresh}
              className="bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center mx-auto"
            >
              <Sparkles className="h-5 w-5 mr-2" />
              {loading ? "Getting Insights..." : "Get AI Insights"}
            </button>
            {!canRefresh && planInfo?.next_available_date && (
              <p className="text-sm text-gray-500 mt-2">
                Available in {daysUntilNext} day{daysUntilNext !== 1 ? "s" : ""}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Insights Display */}
      {!loading && !error && insights && parsedSections.length > 0 && (
        <div>
          {/* Refresh Button */}
          <div className="flex justify-end mb-6">
            <button
              onClick={getNewInsights}
              disabled={loading || !canRefresh}
              className="flex items-center text-sm text-primary-600 hover:text-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <RefreshCw
                className={`h-4 w-4 mr-1 ${loading ? "animate-spin" : ""}`}
              />
              {loading
                ? "Getting Insights..."
                : !canRefresh
                ? `Refresh in ${daysUntilNext} day${
                    daysUntilNext !== 1 ? "s" : ""
                  }`
                : "Refresh"}
            </button>
          </div>

          {/* Insights Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {parsedSections.map((section, index) => {
              const styles = getSectionStyles(section.type);
              return (
                <div
                  key={index}
                  className={`p-4 rounded-lg border ${styles.container} transition-all hover:shadow-sm`}
                >
                  <div className="flex items-center mb-3">
                    <div className={`${styles.icon} mr-3`}>{section.icon}</div>
                    <h4 className={`font-semibold text-sm ${styles.title}`}>
                      {section.title}
                    </h4>
                  </div>
                  <div className={`text-sm leading-relaxed ${styles.content}`}>
                    {section.content.map((item, itemIndex) => (
                      <div key={itemIndex} className="mb-2 last:mb-0">
                        <div className="flex items-start">
                          <div
                            className={`w-2 h-2 rounded-full ${styles.content
                              .replace("text-", "bg-")
                              .replace(
                                "-700",
                                "-500"
                              )} mt-2 mr-3 flex-shrink-0`}
                          ></div>
                          <p>{item}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Fallback for unstructured insights */}
      {!loading && !error && insights && parsedSections.length === 0 && (
        <div className="bg-gray-50 rounded-lg p-6">
          <div className="flex items-start">
            <Brain className="h-5 w-5 text-gray-600 mr-3 mt-0.5" />
            <div className="text-gray-700">
              <p className="leading-relaxed">
                {typeof insights === "string"
                  ? insights
                  : "No structured insights available"}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
