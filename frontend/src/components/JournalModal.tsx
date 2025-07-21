"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { X, Calendar, BookOpen } from "lucide-react";
import { apiClient } from "@/lib/api";
import { Trade } from "@/types";

interface JournalModalProps {
  isOpen: boolean;
  onClose: () => void;
  onJournalCreated: () => void;
  selectedTrade?: Trade | null;
}

interface JournalFormData {
  date: string;
  notes: string;
  trade_id?: string;
}

export default function JournalModal({
  isOpen,
  onClose,
  onJournalCreated,
  selectedTrade,
}: JournalModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<JournalFormData>({
    defaultValues: {
      date: new Date().toISOString().split("T")[0],
      notes: "",
      trade_id: selectedTrade?.id,
    },
  });

  const onSubmit = async (data: JournalFormData) => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.createJournalEntry({
        date: data.date,
        notes: data.notes,
        trade_id: data.trade_id || undefined,
      });

      if (response.success) {
        reset();
        onJournalCreated();
        onClose();
      } else {
        setError(response.error || "Failed to create journal entry");
      }
    } catch (err) {
      setError("An error occurred while creating the journal entry");
      console.error("Error creating journal entry:", err);
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
            <h2 className="text-xl font-semibold text-gray-900">
              Add Journal Entry
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {selectedTrade && (
            <div className="mb-4 p-3 bg-primary-50 border border-primary-200 rounded-lg">
              <p className="text-primary-700 text-sm">
                <strong>Selected Trade:</strong> {selectedTrade.ticker_symbol} -{" "}
                {selectedTrade.trading_type} - {selectedTrade.win_loss}
              </p>
            </div>
          )}

          {error && (
            <div className="mb-4 p-3 bg-danger-50 border border-danger-200 rounded-lg">
              <p className="text-danger-700 text-sm">{error}</p>
            </div>
          )}

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

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Journal Notes
              </label>
              <div className="relative">
                <BookOpen className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <textarea
                  {...register("notes", {
                    required: "Notes are required",
                    minLength: {
                      value: 10,
                      message: "Notes must be at least 10 characters",
                    },
                  })}
                  rows={6}
                  className="input-field pl-10 resize-none"
                  placeholder="Enter your trading notes, observations, lessons learned..."
                />
              </div>
              {errors.notes && (
                <p className="text-danger-600 text-sm mt-1">
                  {errors.notes.message}
                </p>
              )}
            </div>

            {/* Hidden trade_id field */}
            <input
              type="hidden"
              {...register("trade_id")}
              value={selectedTrade?.id || ""}
            />

            {/* Submit Button */}
            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Creating..." : "Save Journal Entry"}
              </button>
              <button type="button" onClick={onClose} className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
