"use client";

import React, { useState, useEffect } from "react";
import { X, TrendingUp, TrendingDown } from "lucide-react";
import { apiClient } from "@/lib/api";
import { format } from "date-fns";

interface Position {
  id: string;
  symbol: string;
  status: "OPEN" | "CLOSED";
  total_shares: number;
  buy_price: number | null;
  sell_price: number | null;
  buy_date: string | null;
  sell_date: string | null;
  pnl: number | null;
  created_at: string;
  updated_at: string;
}

interface Trade {
  id: string;
  date: string;
  ticker_symbol: string;
  number_of_shares: number;
  buy_price: number | null;
  sell_price: number | null;
  trading_type: string;
  status: string;
  transaction_type: string;
  shares_remaining: number;
}

interface PositionDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  position: Position | null;
}

export default function PositionDetailModal({
  isOpen,
  onClose,
  position,
}: PositionDetailModalProps) {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && position) {
      loadPositionDetails();
    }
  }, [isOpen, position]);

  const loadPositionDetails = async () => {
    if (!position) return;

    try {
      setLoading(true);
      const response = await apiClient.getPositionDetails(position.id);
      if (response.success) {
        setTrades(response.trades || []);
      }
    } catch (error) {
      console.error("Error loading position details:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !position) return null;

  const formatCurrency = (value: number | null) => {
    if (value === null) return "-";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat("en-US").format(value);
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "px-2 py-1 rounded-full text-xs font-medium";
    if (status === "OPEN") {
      return `${baseClasses} bg-green-100 text-green-800`;
    } else {
      return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const getTradeTypeBadge = (trade: Trade) => {
    const baseClasses = "px-2 py-1 rounded-full text-xs font-medium";
    if (trade.buy_price && !trade.sell_price) {
      return `${baseClasses} bg-blue-100 text-blue-800`;
    } else if (trade.sell_price) {
      return `${baseClasses} bg-red-100 text-red-800`;
    } else {
      return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const calculateTradePnL = (trade: Trade) => {
    if (trade.buy_price && trade.sell_price) {
      return (trade.sell_price - trade.buy_price) * trade.number_of_shares;
    }
    return null;
  };

  // Separate BUY and SELL trades
  const buyTrades = trades.filter(
    (trade) => trade.buy_price && !trade.sell_price
  );
  const sellTrades = trades.filter((trade) => trade.sell_price);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {position.symbol} Position Details
              </h2>
              <div className="flex items-center gap-4 mt-2">
                <span className={getStatusBadge(position.status)}>
                  {position.status}
                </span>
                <span className="text-sm text-gray-600">
                  {formatNumber(position.total_shares)} shares
                </span>
                {position.pnl !== null && (
                  <span
                    className={`text-sm font-medium ${
                      position.pnl >= 0 ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {formatCurrency(position.pnl)} P&L
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Position Summary */}
        <div className="p-6 bg-gray-50 border-b border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-600">Average Buy Price</div>
              <div className="text-lg font-semibold text-gray-900">
                {formatCurrency(position.buy_price)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600">Average Sell Price</div>
              <div className="text-lg font-semibold text-gray-900">
                {formatCurrency(position.sell_price)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600">Buy Date</div>
              <div className="text-lg font-semibold text-gray-900">
                {position.buy_date
                  ? format(new Date(position.buy_date), "MMM dd, yyyy")
                  : "-"}
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600">Sell Date</div>
              <div className="text-lg font-semibold text-gray-900">
                {position.sell_date
                  ? format(new Date(position.sell_date), "MMM dd, yyyy")
                  : "-"}
              </div>
            </div>
          </div>
        </div>

        {/* Trades Table */}
        <div className="p-6 overflow-y-auto max-h-96">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Individual Trades ({trades.length})
          </h3>

          {loading ? (
            <div className="text-center text-gray-500 py-8">
              Loading trades...
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Shares
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Buy Price
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Sell Price
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      P&L
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {trades.map((trade) => {
                    const tradePnL = calculateTradePnL(trade);
                    return (
                      <tr key={trade.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {format(new Date(trade.date), "MMM dd, yyyy")}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <span className={getTradeTypeBadge(trade)}>
                            {trade.buy_price && !trade.sell_price
                              ? "BUY"
                              : "SELL"}
                          </span>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {formatNumber(trade.number_of_shares)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {formatCurrency(trade.buy_price)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {formatCurrency(trade.sell_price)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm">
                          {tradePnL !== null ? (
                            <span
                              className={
                                tradePnL >= 0
                                  ? "text-green-600"
                                  : "text-red-600"
                              }
                            >
                              {formatCurrency(tradePnL)}
                            </span>
                          ) : (
                            <span className="text-gray-500">-</span>
                          )}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <span className={getStatusBadge(trade.status)}>
                            {trade.status}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
