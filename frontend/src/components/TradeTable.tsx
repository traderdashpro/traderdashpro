"use client";

import React, { useState, useEffect } from "react";
import { Search, Filter, Trash2, Edit } from "lucide-react";
import { apiClient } from "@/lib/api";
import { Trade } from "@/types";
import { format } from "date-fns";

interface TradeTableProps {
  onTradeSelected?: (trade: Trade) => void;
  onTradeDeleted?: () => void;
}

export default function TradeTable({
  onTradeSelected,
  onTradeDeleted,
}: TradeTableProps) {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filters, setFilters] = useState({
    trading_type: "",
    win_loss: "",
    status: "",
    date_from: "",
    date_to: "",
  });

  useEffect(() => {
    loadTrades();
  }, [filters]);

  const loadTrades = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getTrades(filters);
      if (response.success) {
        setTrades(response.trades || []);
      }
    } catch (error) {
      console.error("Error loading trades:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTrade = async (tradeId: string) => {
    if (!confirm("Are you sure you want to delete this trade?")) return;

    try {
      const response = await apiClient.deleteTrade(tradeId);
      if (response.success) {
        loadTrades();
        onTradeDeleted?.();
      }
    } catch (error) {
      console.error("Error deleting trade:", error);
    }
  };

  const filteredTrades = trades.filter(
    (trade) =>
      trade.ticker_symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      trade.trading_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (trade.win_loss &&
        trade.win_loss.toLowerCase().includes(searchTerm.toLowerCase())) ||
      trade.status.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const calculateProfitLoss = (trade: Trade) => {
    // For open positions, return null to show dash
    if (trade.status === "OPEN") {
      return null;
    }
    return trade.proceeds - trade.price_cost_basis;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search trades..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10"
          />
        </div>

        <div className="flex gap-2">
          <select
            value={filters.trading_type}
            onChange={(e) =>
              setFilters({ ...filters, trading_type: e.target.value })
            }
            className="input-field"
          >
            <option value="">All Types</option>
            <option value="Swing">Swing</option>
            <option value="Day">Day</option>
          </select>

          <select
            value={filters.win_loss}
            onChange={(e) =>
              setFilters({ ...filters, win_loss: e.target.value })
            }
            className="input-field"
          >
            <option value="">All Results</option>
            <option value="Win">Win</option>
            <option value="Loss">Loss</option>
            <option value="Pending">Pending</option>
          </select>

          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="input-field"
          >
            <option value="">All Status</option>
            <option value="OPEN">Open</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>
      </div>

      {/* Trades Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Symbol
                </th>
                <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Shares
                </th>
                <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Buy
                </th>
                <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sell
                </th>
                <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  P&L
                </th>
                <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredTrades.map((trade) => {
                const profitLoss = calculateProfitLoss(trade);
                return (
                  <tr key={trade.id} className="hover:bg-gray-50">
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                      {format(new Date(trade.date), "MMM dd")}
                    </td>
                    <td className="px-2 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {trade.ticker_symbol}
                    </td>
                    <td className="px-2 py-4 whitespace-nowrap text-sm text-gray-900">
                      {trade.number_of_shares.toLocaleString()}
                    </td>
                    <td className="px-2 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${trade.buy_price?.toFixed(2) ?? "-"}
                    </td>
                    <td className="px-2 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${trade.sell_price?.toFixed(2) ?? "-"}
                    </td>
                    <td
                      className={`px-2 py-4 whitespace-nowrap text-sm font-medium ${
                        profitLoss === null
                          ? "text-gray-500"
                          : profitLoss >= 0
                          ? "text-success-600"
                          : "text-danger-600"
                      }`}
                    >
                      {profitLoss === null ? "-" : `$${profitLoss.toFixed(2)}`}
                    </td>
                    <td className="px-2 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          trade.trading_type === "Swing"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-green-100 text-green-800"
                        }`}
                      >
                        {trade.trading_type}
                      </span>
                    </td>
                    <td className="px-2 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          trade.status === "OPEN"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {trade.status}
                      </span>
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => onTradeSelected?.(trade)}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteTrade(trade.id)}
                          className="text-danger-600 hover:text-danger-900"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filteredTrades.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No trades found</p>
          </div>
        )}
      </div>
    </div>
  );
}
