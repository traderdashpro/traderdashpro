"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { X, Calendar } from "lucide-react";
import { apiClient } from "@/lib/api";

interface TradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTradeCreated: () => void;
}

interface TradeFormData {
  date: string;
  ticker_symbol: string;
  number_of_shares: number;
  buy_price: number;
  sell_price: number;
  trading_type: "Swing" | "Day";
}

export default function TradeModal({
  isOpen,
  onClose,
  onTradeCreated,
}: TradeModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"import" | "manual">("import");
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [platform, setPlatform] = useState("thinkorswim");
  const [file, setFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    setUploading(true);
    setUploadResult(null);
    setUploadError(null);
    try {
      const formData = new FormData();
      formData.append("platform", platform);
      if (file) formData.append("file", file);

      // Use the authenticated API client for the upload
      const response = await apiClient.uploadStatement(formData);

      // The backend returns data directly on success, no 'success' field
      if (response && response.closed_trades_count !== undefined) {
        setUploadResult(
          `Successfully imported ${response.closed_trades_count} trades!`
        );
        setTimeout(() => {
          if (onTradeCreated) onTradeCreated();
          onClose();
        }, 500);
      } else {
        setUploadError(response.error || "Upload failed");
      }
    } catch (err: any) {
      setUploadError(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TradeFormData>({
    defaultValues: {
      date: new Date().toISOString().split("T")[0],
      trading_type: "Swing",
    },
  });

  const onSubmit = async (data: TradeFormData) => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.createTrade({
        ...data,
        ticker_symbol: data.ticker_symbol.toUpperCase(),
      });

      if (response.success) {
        reset();
        onTradeCreated();
        onClose();
      } else {
        setError(response.error || "Failed to create trade");
      }
    } catch (err) {
      setError("An error occurred while creating the trade");
      console.error("Error creating trade:", err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Add Trade</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b mb-4">
            <button
              className={`px-4 py-2 -mb-px border-b-2 font-medium ${
                activeTab === "import"
                  ? "border-primary-600 text-primary-700"
                  : "border-transparent text-gray-500"
              }`}
              onClick={() => setActiveTab("import")}
            >
              Import Trades
            </button>
            <button
              className={`px-4 py-2 -mb-px border-b-2 font-medium ${
                activeTab === "manual"
                  ? "border-primary-600 text-primary-700"
                  : "border-transparent text-gray-500"
              }`}
              onClick={() => setActiveTab("manual")}
            >
              Manual Entry
            </button>
          </div>

          {/* Import Trades Tab */}
          {activeTab === "import" && (
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Platform
                </label>
                <select
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                  className="input-field"
                >
                  <option value="thinkorswim">Thinkorswim</option>
                  {/* Add more platforms here in the future */}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  CSV File
                </label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="input-field"
                  required
                />
              </div>
              <button
                type="submit"
                className="btn-primary w-full"
                disabled={uploading || !file}
              >
                {uploading ? "Uploading..." : "Upload Statement"}
              </button>
              {uploadError && (
                <div className="p-3 bg-danger-50 border border-danger-200 rounded-lg text-danger-700 text-sm">
                  {uploadError}
                </div>
              )}
              {uploadResult && (
                <div className="p-3 bg-success-50 border border-success-200 rounded-lg text-success-700 text-sm">
                  {uploadResult}
                </div>
              )}
            </form>
          )}

          {/* Manual Entry Tab */}
          {activeTab === "manual" && (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="date"
                    {...register("date", { required: "Date is required" })}
                    className="input-field pl-10"
                  />
                </div>
                {errors.date && (
                  <p className="text-danger-600 text-sm mt-1">
                    {errors.date.message}
                  </p>
                )}
              </div>
              {/* Ticker Symbol */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ticker Symbol
                </label>
                <input
                  type="text"
                  {...register("ticker_symbol", {
                    required: "Ticker symbol is required",
                  })}
                  className="input-field"
                />
                {errors.ticker_symbol && (
                  <p className="text-danger-600 text-sm mt-1">
                    {errors.ticker_symbol.message}
                  </p>
                )}
              </div>
              {/* Number of Shares */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Number of Shares
                </label>
                <input
                  type="number"
                  {...register("number_of_shares", {
                    required: "Number of shares is required",
                    min: 1,
                  })}
                  className="input-field"
                />
                {errors.number_of_shares && (
                  <p className="text-danger-600 text-sm mt-1">
                    {errors.number_of_shares.message}
                  </p>
                )}
              </div>
              {/* Buy Price */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Buy Price
                </label>
                <input
                  type="number"
                  step="0.01"
                  {...register("buy_price", {
                    required: "Buy price is required",
                  })}
                  className="input-field"
                />
                {errors.buy_price && (
                  <p className="text-danger-600 text-sm mt-1">
                    {errors.buy_price.message}
                  </p>
                )}
              </div>
              {/* Sell Price */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sell Price
                </label>
                <input
                  type="number"
                  step="0.01"
                  {...register("sell_price", {
                    required: "Sell price is required",
                  })}
                  className="input-field"
                />
                {errors.sell_price && (
                  <p className="text-danger-600 text-sm mt-1">
                    {errors.sell_price.message}
                  </p>
                )}
              </div>
              {/* Trading Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Trading Type
                </label>
                <select
                  {...register("trading_type", {
                    required: "Trading type is required",
                  })}
                  className="input-field"
                >
                  <option value="">Select Type</option>
                  <option value="Swing">Swing</option>
                  <option value="Day">Day</option>
                </select>
                {errors.trading_type && (
                  <p className="text-danger-600 text-sm mt-1">
                    {errors.trading_type.message}
                  </p>
                )}
              </div>
              <button type="submit" className="btn-primary w-full">
                Add Trade
              </button>
              {error && (
                <div className="p-3 bg-danger-50 border border-danger-200 rounded-lg">
                  <p className="text-danger-700 text-sm">{error}</p>
                </div>
              )}
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
