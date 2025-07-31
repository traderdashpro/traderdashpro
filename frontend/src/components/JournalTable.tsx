"use client";

import React, { useState, useEffect } from "react";
import { Search, Filter, Trash2, Edit, Calendar, BookOpen } from "lucide-react";
import { apiClient } from "@/lib/api";
import { JournalEntry } from "@/types";
import { format } from "date-fns";

interface JournalTableProps {
  onJournalDeleted?: () => void;
}

export default function JournalTable({ onJournalDeleted }: JournalTableProps) {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filters, setFilters] = useState({
    entry_type: "",
    date_from: "",
    date_to: "",
  });

  useEffect(() => {
    loadJournalEntries();
  }, [filters]);

  const loadJournalEntries = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getJournalEntries(filters);
      if (response.success) {
        setEntries(response.entries || []);
      }
    } catch (error) {
      console.error("Error loading journal entries:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteEntry = async (entryId: string) => {
    if (!confirm("Are you sure you want to delete this journal entry?")) return;

    try {
      const response = await apiClient.deleteJournalEntry(entryId);
      if (response.success) {
        loadJournalEntries();
        onJournalDeleted?.();
      }
    } catch (error) {
      console.error("Error deleting journal entry:", error);
    }
  };

  const filteredEntries = entries.filter(
    (entry) =>
      entry.notes.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.entry_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
            placeholder="Search journal entries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10"
          />
        </div>

        <div className="flex gap-2">
          <select
            value={filters.entry_type}
            onChange={(e) =>
              setFilters({ ...filters, entry_type: e.target.value })
            }
            className="input-field"
          >
            <option value="">All Types</option>
            <option value="general">General</option>
            <option value="trade_specific">Trade Specific</option>
          </select>

          <input
            type="date"
            value={filters.date_from}
            onChange={(e) =>
              setFilters({ ...filters, date_from: e.target.value })
            }
            className="input-field"
            placeholder="From Date"
          />

          <input
            type="date"
            value={filters.date_to}
            onChange={(e) =>
              setFilters({ ...filters, date_to: e.target.value })
            }
            className="input-field"
            placeholder="To Date"
          />
        </div>
      </div>

      {/* Journal Entries Table */}
      <div className="card overflow-hidden">
        {filteredEntries.length === 0 ? (
          <div className="text-center py-8">
            <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No journal entries
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating your first journal entry.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Notes
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredEntries.map((entry) => (
                  <tr key={entry.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                        {format(new Date(entry.date), "MMM dd, yyyy")}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          entry.entry_type === "trade_specific"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-green-100 text-green-800"
                        }`}
                      >
                        {entry.entry_type === "trade_specific"
                          ? "Trade Specific"
                          : "General"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-xs truncate">{entry.notes}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {format(new Date(entry.created_at), "MMM dd, yyyy")}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleDeleteEntry(entry.id)}
                        className="text-red-600 hover:text-red-900 ml-4"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
