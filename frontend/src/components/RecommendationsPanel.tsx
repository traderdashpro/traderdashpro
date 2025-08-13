"use client";

import React from "react";
import {
  BookOpen,
  Play,
  ExternalLink,
  TrendingUp,
  Target,
  Heart,
  AlertTriangle,
  Lightbulb,
} from "lucide-react";
import { AIInsights } from "@/types";

interface Recommendation {
  id: string;
  title: string;
  description: string;
  type: "video" | "book";
  url: string;
  thumbnail?: string;
  category:
    | "patterns"
    | "strengths"
    | "improvements"
    | "emotions"
    | "performance"
    | "recommendations";
}

interface RecommendationsPanelProps {
  insights: any;
}

export default function RecommendationsPanel({
  insights,
}: RecommendationsPanelProps) {
  // Generate recommendations based on AI insights
  const generateRecommendations = (insights: any): Recommendation[] => {
    const recommendations: Recommendation[] = [];

    // Use AI-generated learning resources if available
    if (insights?.learning_resources) {
      const { videos, books } = insights.learning_resources;

      // Add AI-generated video recommendations
      if (videos && Array.isArray(videos)) {
        videos.forEach((video: any, index: number) => {
          recommendations.push({
            id: `ai-video-${index}`,
            title: video.title || "Trading Video",
            description: video.description || "AI-recommended trading content",
            type: "video",
            url: `https://www.youtube.com/results?search_query=${encodeURIComponent(
              video.search_query || video.title
            )}`,
            category: video.category || "recommendations",
          });
        });
      }

      // Add AI-generated book recommendations
      if (books && Array.isArray(books)) {
        books.forEach((book: any, index: number) => {
          recommendations.push({
            id: `ai-book-${index}`,
            title: book.title || "Trading Book",
            description: book.description || "AI-recommended trading book",
            type: "book",
            url: `https://www.amazon.com/s?k=${encodeURIComponent(
              book.search_query || book.title
            )}`,
            category: book.category || "recommendations",
          });
        });
      }
    }

    // If we have AI recommendations, return them
    if (recommendations.length > 0) {
      return recommendations.slice(0, 6);
    }

    // Fallback to hardcoded recommendations based on insights
    // Key Patterns - recommend technical analysis and pattern recognition
    if (insights?.key_patterns && insights.key_patterns.length > 0) {
      recommendations.push(
        {
          id: "pattern-1",
          title: "Technical Analysis: Chart Patterns Masterclass",
          description: "Learn to identify and trade chart patterns effectively",
          type: "video",
          url: "https://www.youtube.com/watch?v=RuS7PZXC3Mk",
          category: "patterns",
        },
        {
          id: "pattern-2",
          title: "Technical Analysis of the Financial Markets",
          description: "Comprehensive guide to market analysis and patterns",
          type: "book",
          url: "https://www.amazon.com/Technical-Analysis-Financial-Markets-Comprehensive/dp/0735200661",
          category: "patterns",
        }
      );
    }

    // Strengths - recommend advanced strategies
    if (insights?.strengths && insights.strengths.length > 0) {
      recommendations.push(
        {
          id: "strength-1",
          title: "Advanced Trading Strategies for Experienced Traders",
          description: "Build on your strengths with advanced techniques",
          type: "video",
          url: "https://www.youtube.com/watch?v=8hGvQtUMNAY",
          category: "strengths",
        },
        {
          id: "strength-2",
          title: "Trading in the Zone",
          description: "Master the psychology of successful trading",
          type: "book",
          url: "https://www.amazon.com/Trading-Zone-Master-Market-Psychology/dp/0735201447",
          category: "strengths",
        }
      );
    }

    // Areas for Improvement - recommend educational content
    if (
      insights?.areas_for_improvement &&
      insights.areas_for_improvement.length > 0
    ) {
      recommendations.push(
        {
          id: "improvement-1",
          title: "Risk Management in Trading",
          description: "Essential risk management strategies for traders",
          type: "video",
          url: "https://www.youtube.com/watch?v=3nAIn-ZwX4E",
          category: "improvements",
        },
        {
          id: "improvement-2",
          title: "The Disciplined Trader",
          description: "Develop trading discipline and consistency",
          type: "book",
          url: "https://www.amazon.com/Disciplined-Trader-Developing-Winning-Attitude/dp/0132157578",
          category: "improvements",
        }
      );
    }

    // Emotional State - recommend psychology-focused content
    if (insights?.emotional_state_analysis) {
      recommendations.push(
        {
          id: "emotion-1",
          title: "Trading Psychology: Mastering Your Emotions",
          description: "Learn to control emotions while trading",
          type: "video",
          url: "https://www.youtube.com/watch?v=4R6CfV7ZuAQ",
          category: "emotions",
        },
        {
          id: "emotion-2",
          title: "The Psychology of Money",
          description:
            "Understanding the psychology behind financial decisions",
          type: "book",
          url: "https://www.amazon.com/Psychology-Money-Timeless-Lessons-Happiness/dp/0857197681",
          category: "emotions",
        }
      );
    }

    // Performance Insights - recommend optimization content
    if (insights?.trading_performance_insights) {
      recommendations.push(
        {
          id: "performance-1",
          title: "Trading Performance Optimization",
          description: "Optimize your trading strategy for better results",
          type: "video",
          url: "https://www.youtube.com/watch?v=9aHvO8Xei0Q",
          category: "performance",
        },
        {
          id: "performance-2",
          title: "Building Algorithmic Trading Systems",
          description: "Systematic approach to trading performance",
          type: "book",
          url: "https://www.amazon.com/Building-Algorithmic-Trading-Systems-Professional/dp/1118615184",
          category: "performance",
        }
      );
    }

    // General recommendations if no specific insights
    if (recommendations.length === 0) {
      recommendations.push(
        {
          id: "general-1",
          title: "Trading for Beginners",
          description: "Essential concepts for new traders",
          type: "video",
          url: "https://www.youtube.com/watch?v=RuS7PZXC3Mk",
          category: "recommendations",
        },
        {
          id: "general-2",
          title: "Market Wizards",
          description: "Interviews with top traders",
          type: "book",
          url: "https://www.amazon.com/Market-Wizards-Interviews-Top-Traders/dp/1592802974",
          category: "recommendations",
        }
      );
    }

    return recommendations.slice(0, 6); // Limit to 6 recommendations
  };

  const recommendations = generateRecommendations(insights);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "patterns":
        return <Target className="h-4 w-4" />;
      case "strengths":
        return <TrendingUp className="h-4 w-4" />;
      case "improvements":
        return <AlertTriangle className="h-4 w-4" />;
      case "emotions":
        return <Heart className="h-4 w-4" />;
      case "performance":
        return <TrendingUp className="h-4 w-4" />;
      default:
        return <Lightbulb className="h-4 w-4" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "patterns":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "strengths":
        return "bg-green-100 text-green-800 border-green-200";
      case "improvements":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "emotions":
        return "bg-pink-100 text-pink-800 border-pink-200";
      case "performance":
        return "bg-purple-100 text-purple-800 border-purple-200";
      default:
        return "bg-indigo-100 text-indigo-800 border-indigo-200";
    }
  };

  if (!insights) {
    // Show default recommendations when no insights are available
    const defaultRecommendations = [
      {
        id: "default-1",
        title: "Trading for Beginners",
        description: "Essential concepts for new traders",
        type: "video" as const,
        url: "https://www.youtube.com/watch?v=RuS7PZXC3Mk",
        category: "recommendations" as const,
      },
      {
        id: "default-2",
        title: "Market Wizards",
        description: "Interviews with top traders",
        type: "book" as const,
        url: "https://www.amazon.com/Market-Wizards-Interviews-Top-Traders/dp/1592802974",
        category: "recommendations" as const,
      },
      {
        id: "default-3",
        title: "Technical Analysis Fundamentals",
        description: "Learn chart patterns and technical indicators",
        type: "video" as const,
        url: "https://www.youtube.com/watch?v=8hGvQtUMNAY",
        category: "recommendations" as const,
      },
    ];

    return (
      <div className="card">
        <div className="flex items-center mb-6">
          <Lightbulb className="h-6 w-6 text-primary-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">
            Recommended Learning Resources
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {defaultRecommendations.map((rec) => (
            <div
              key={rec.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              {/* Thumbnail */}
              <div className="mb-3">
                {rec.type === "video" ? (
                  <div className="relative">
                    <div className="w-full h-32 bg-gradient-to-br from-red-500 to-red-600 rounded-lg flex items-center justify-center">
                      <Play className="h-8 w-8 text-white" />
                    </div>
                    <div className="absolute top-2 right-2">
                      <span className="bg-red-600 text-white text-xs px-2 py-1 rounded">
                        VIDEO
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="relative">
                    <div className="w-full h-32 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                      <BookOpen className="h-8 w-8 text-white" />
                    </div>
                    <div className="absolute top-2 right-2">
                      <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded">
                        BOOK
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* Category Badge */}
              <div className="mb-2">
                <span
                  className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getCategoryColor(
                    rec.category
                  )}`}
                >
                  {getCategoryIcon(rec.category)}
                  <span className="ml-1 capitalize">
                    {rec.category.replace("_", " ")}
                  </span>
                </span>
              </div>

              {/* Title */}
              <h4 className="font-medium text-gray-900 mb-2 line-clamp-2">
                {rec.title}
              </h4>

              {/* Description */}
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                {rec.description}
              </p>

              {/* Link */}
              <a
                href={rec.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                {rec.type === "video" ? "Watch Video" : "View Book"}
                <ExternalLink className="h-4 w-4 ml-1" />
              </a>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return null;
  }

  return (
    <div className="card">
      <div className="flex items-center mb-6">
        <Lightbulb className="h-6 w-6 text-primary-600 mr-2" />
        <h3 className="text-lg font-semibold text-gray-900">
          {insights?.learning_resources
            ? "AI-Generated Learning Resources"
            : "Recommended Learning Resources"}
        </h3>
        {insights?.learning_resources && (
          <span className="ml-2 px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full">
            AI-Powered
          </span>
        )}
        {!insights?.learning_resources && (
          <span className="ml-2 px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
            Fallback
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {recommendations.map((rec) => (
          <div
            key={rec.id}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            {/* Thumbnail */}
            <div className="mb-3">
              {rec.type === "video" ? (
                <div className="relative">
                  <div className="w-full h-32 bg-gradient-to-br from-red-500 to-red-600 rounded-lg flex items-center justify-center">
                    <Play className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute top-2 right-2">
                    <span className="bg-red-600 text-white text-xs px-2 py-1 rounded">
                      VIDEO
                    </span>
                  </div>
                </div>
              ) : (
                <div className="relative">
                  <div className="w-full h-32 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                    <BookOpen className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute top-2 right-2">
                    <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded">
                      BOOK
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Category Badge */}
            <div className="mb-2">
              <span
                className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getCategoryColor(
                  rec.category
                )}`}
              >
                {getCategoryIcon(rec.category)}
                <span className="ml-1 capitalize">
                  {rec.category.replace("_", " ")}
                </span>
              </span>
            </div>

            {/* Title */}
            <h4 className="font-medium text-gray-900 mb-2 line-clamp-2">
              {rec.title}
            </h4>

            {/* Description */}
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {rec.description}
            </p>

            {/* Link */}
            <a
              href={rec.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              {rec.type === "video" ? "Watch Video" : "View Book"}
              <ExternalLink className="h-4 w-4 ml-1" />
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
