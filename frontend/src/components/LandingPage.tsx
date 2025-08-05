"use client";

import React from "react";
import { 
  Upload, 
  BarChart3, 
  Brain, 
  Play, 
  Shield, 
  Smartphone, 
  Rocket, 
  Users,
  TrendingUp,
  DollarSign,
  ArrowRight
} from "lucide-react";
import Link from "next/link";

export const LandingPage: React.FC = () => {
  const features = [
    {
      icon: Upload,
      title: "Easy Import",
      description: "Upload your trading data from CSV, PDF, or Google Docs. Supports all major broker formats.",
    },
    {
      icon: BarChart3,
      title: "Visual Analytics",
      description: "Beautiful charts and graphs showing your win/loss ratio, P&L trends, and performance metrics.",
    },
    {
      icon: Brain,
      title: "AI Insights",
      description: "Get personalized recommendations and insights powered by ChatGPT to improve your trading strategy.",
    },
    {
      icon: Play,
      title: "Educational Videos",
      description: "Discover curated YouTube videos based on your performance analysis to help you improve specific areas.",
    },
    {
      icon: Shield,
      title: "Secure & Private",
      description: "Your trading data is encrypted and secure. We never share your personal information or trading details.",
      highlighted: true,
    },
    {
      icon: Smartphone,
      title: "Mobile Ready",
      description: "Access your trading dashboard from anywhere. Fully responsive design works on all devices.",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Navigation */}
      <nav className="bg-gray-900/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-white">TradeDashPro</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/auth"
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Login
              </Link>
              <Link
                href="/auth?mode=signup"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center"
              >
                Get Started
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="space-y-8">
              <h1 className="text-5xl lg:text-6xl font-bold text-blue-400 leading-tight">
                Master Your Trading Performance
              </h1>
              <p className="text-xl text-gray-300 leading-relaxed">
                Import your trading data, visualize your performance, and get AI-powered insights to improve your trading strategy. Take your trading to the next level with TradeDashPro.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  href="/auth?mode=signup"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors flex items-center justify-center"
                >
                  <Rocket className="mr-2 h-5 w-5" />
                  Get Started Free
                </Link>
                <Link
                  href="#features"
                  className="border border-gray-600 text-gray-300 hover:text-white hover:border-gray-500 px-8 py-4 rounded-lg text-lg font-semibold transition-colors flex items-center justify-center"
                >
                  <Play className="mr-2 h-5 w-5" />
                  Learn More
                </Link>
              </div>
              
              <div className="flex items-center text-gray-400">
                <Users className="mr-2 h-5 w-5" />
                <span className="text-sm">Join thousands of traders improving their performance</span>
              </div>
            </div>

            {/* Right Content - Dashboard Preview */}
            <div className="relative">
              <div className="bg-gray-800 rounded-xl p-6 shadow-2xl border border-gray-700">
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-400 text-sm font-medium">Win Rate</span>
                      <TrendingUp className="h-4 w-4 text-blue-400" />
                    </div>
                    <div className="text-2xl font-bold text-green-400">72.5%</div>
                  </div>
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-400 text-sm font-medium">Total P&L</span>
                      <DollarSign className="h-4 w-4 text-blue-400" />
                    </div>
                    <div className="text-2xl font-bold text-green-400">$8,420</div>
                  </div>
                </div>
                <div className="bg-blue-600 rounded-lg p-8 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-blue-500 rounded-lg flex items-center justify-center mx-auto mb-4">
                      <TrendingUp className="h-8 w-8 text-white" />
                    </div>
                    <span className="text-white font-medium">Performance Chart</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              Powerful Features for Traders
            </h2>
            <p className="text-xl text-gray-300">
              Everything you need to analyze and improve your trading performance
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className={`p-6 rounded-xl border transition-all duration-300 hover:scale-105 ${
                    feature.highlighted
                      ? "bg-gray-700 border-blue-500 shadow-lg shadow-blue-500/20"
                      : "bg-gray-900 border-gray-700 hover:border-gray-600"
                  }`}
                >
                  <div className="flex items-center mb-4">
                    <div className={`p-3 rounded-lg ${
                      feature.highlighted ? "bg-blue-500" : "bg-blue-600"
                    }`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gray-900">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Transform Your Trading?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Start tracking your performance today and get AI-powered insights to improve your trading strategy.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth?mode=signup"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors flex items-center justify-center"
            >
              <Rocket className="mr-2 h-5 w-5" />
              Start Free Trial
            </Link>
            <Link
              href="/auth"
              className="border border-gray-600 text-gray-300 hover:text-white hover:border-gray-500 px-8 py-4 rounded-lg text-lg font-semibold transition-colors"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 border-t border-gray-800 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-white mb-4">TradeDashPro</h3>
            <p className="text-gray-400 mb-6">
              The ultimate trading performance analysis platform
            </p>
            <div className="flex justify-center space-x-6 text-sm text-gray-500">
              <span>© 2024 TradeDashPro. All rights reserved.</span>
              <span>•</span>
              <span>Privacy Policy</span>
              <span>•</span>
              <span>Terms of Service</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}; 