"use client";

import React, { useState, useEffect } from "react";
import { Doughnut, Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";
import { apiClient } from "@/lib/api";
import { DashboardStats, ChartData } from "@/types";
import { TrendingUp, TrendingDown, DollarSign, Target } from "lucide-react";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [chartData, setChartData] = useState<any>(null);
  const [tradingType, setTradingType] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, [tradingType]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsResponse, chartResponse] = await Promise.all([
        apiClient.getDashboardStats(
          tradingType === "all" ? undefined : tradingType
        ),
        apiClient.getChartData(tradingType === "all" ? undefined : tradingType),
      ]);

      if (statsResponse.success) {
        setStats(statsResponse.stats);
      }

      if (chartResponse.success) {
        setChartData(chartResponse);
      }
    } catch (error) {
      console.error("Error loading dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const donutChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom" as const,
      },
    },
  };

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        // No min/max, let Chart.js auto-scale
      },
    },
  };

  // Prepare daily P&L data for the line chart
  let dailyChartData = { labels: [], data: [] };
  if (chartData && chartData.line_chart) {
    dailyChartData.labels = chartData.line_chart.labels;
    dailyChartData.data = chartData.line_chart.data;
  }

  // Debug: log the data passed to the chart
  console.log("Daily Chart Data", dailyChartData);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Trading Dashboard</h1>

        {/* Trading Type Toggle */}
        <div className="flex bg-gray-200 rounded-lg p-1">
          <button
            onClick={() => setTradingType("all")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              tradingType === "all"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            All Trades
          </button>
          <button
            onClick={() => setTradingType("Swing")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              tradingType === "Swing"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Swing
          </button>
          <button
            onClick={() => setTradingType("Day")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              tradingType === "Day"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Day
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-success-100 rounded-lg">
                <Target className="h-6 w-6 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Win Rate</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.win_rate}%
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-primary-100 rounded-lg">
                <DollarSign className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total P&L</p>
                <p
                  className={`text-2xl font-bold ${
                    stats.total_profit_loss >= 0
                      ? "text-success-600"
                      : "text-danger-600"
                  }`}
                >
                  ${stats.total_profit_loss.toLocaleString()}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-success-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Wins</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.win_count}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-danger-100 rounded-lg">
                <TrendingDown className="h-6 w-6 text-danger-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Losses</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.loss_count}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      {chartData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Win/Loss Donut Chart */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Win/Loss Distribution
            </h3>
            <div className="h-64">
              <Doughnut
                data={{
                  labels: chartData.donut_chart.labels,
                  datasets: [
                    {
                      data: chartData.donut_chart.data,
                      backgroundColor: chartData.donut_chart.backgroundColor,
                      borderWidth: 0,
                    },
                  ],
                }}
                options={donutChartOptions}
              />
            </div>
          </div>

          {/* Daily P&L Line Chart */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Daily Profit/Loss
            </h3>
            <div className="h-64">
              <Line
                data={{
                  labels: dailyChartData.labels,
                  datasets: [
                    {
                      label: "Profit/Loss",
                      data: dailyChartData.data,
                      borderColor: "#3b82f6",
                      backgroundColor: "rgba(59, 130, 246, 0.1)",
                      tension: 0.4,
                    },
                  ],
                }}
                options={lineChartOptions}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
