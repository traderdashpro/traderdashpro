"use client";

import React, { useState, useEffect } from "react";
import {
  Search,
  Filter,
  Trash2,
  Edit,
  Calendar,
  BookOpen,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { JournalEntry } from "@/types";
import { format } from "date-fns";
import { useRouter, useSearchParams } from "next/navigation";

interface JournalTableProps {
  onJournalDeleted?: () => void;
}

export default function JournalTable({ onJournalDeleted }: JournalTableProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = "/journal"; // Adjust this to your actual journal page path

  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [paginationLoading, setPaginationLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedRowId, setExpandedRowId] = useState<string | null>(null);
  const [expandedAll, setExpandedAll] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [entriesPerPage, setEntriesPerPage] = useState(10);
  const [totalEntries, setTotalEntries] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [filters, setFilters] = useState({
    entry_type: "",
    date_from: "",
    date_to: "",
  });

  // URL synchronization
  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());
    const page = parseInt(params.get("page") || "1");
    const perPage = parseInt(params.get("per_page") || "10");
    const search = params.get("search") || "";
    const entryType = params.get("entry_type") || "";
    const dateFrom = params.get("date_from") || "";
    const dateTo = params.get("date_to") || "";

    setCurrentPage(page);
    setEntriesPerPage(perPage);
    setSearchTerm(search);
    setFilters({
      entry_type: entryType,
      date_from: dateFrom,
      date_to: dateTo,
    });
  }, [searchParams]);

  // Reset expanded row when changing pages or filters
  useEffect(() => {
    setExpandedRowId(null);
    setExpandedAll(false);
  }, [currentPage, filters, searchTerm]);

  useEffect(() => {
    loadJournalEntries();
  }, [currentPage, entriesPerPage, filters, searchTerm]);

  // Update URL with new parameters
  const updateURL = (updates: Record<string, string | number>) => {
    const params = new URLSearchParams(searchParams.toString());
    Object.entries(updates).forEach(([key, value]) => {
      if (value && value !== "") {
        params.set(key, value.toString());
      } else {
        params.delete(key);
      }
    });
    router.push(`${pathname}?${params.toString()}`);
  };

  const loadJournalEntries = async () => {
    try {
      setPaginationLoading(true);
      const params = {
        page: currentPage,
        per_page: entriesPerPage,
        search: searchTerm,
        ...filters,
      };

      const response = await apiClient.getJournalEntries(params);
      if (response.success) {
        setEntries(response.entries || []);
        setTotalEntries(response.pagination?.total_count || 0);
        setTotalPages(response.pagination?.total_pages || 0);
      }
    } catch (error) {
      console.error("Error loading journal entries:", error);
    } finally {
      setPaginationLoading(false);
      setLoading(false);
    }
  };

  // Accordion functions
  const handleRowClick = (entryId: string) => {
    if (expandedAll) {
      // If all are expanded, clicking a row should collapse all
      setExpandedAll(false);
      setExpandedRowId(null);
    } else {
      // Normal single row expansion
      setExpandedRowId(expandedRowId === entryId ? null : entryId);
    }
  };

  const expandAll = () => {
    if (entries.length > 0) {
      setExpandedAll(true);
      setExpandedRowId(null); // Clear single row expansion
    }
  };

  const collapseAll = () => {
    setExpandedAll(false);
    setExpandedRowId(null);
  };

  // Search highlighting function
  const highlightSearchTerms = (text: string, searchTerm: string) => {
    if (!searchTerm) return text;
    const regex = new RegExp(`(${searchTerm})`, "gi");
    return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
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

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    setCurrentPage(1); // Reset to first page when searching
    updateURL({ search: value, page: 1 });
  };

  // Handle filter changes
  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setCurrentPage(1); // Reset to first page when filtering
    updateURL({ [key]: value, page: 1 });
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
            placeholder="Search journal entries..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="input-field pl-10"
          />
        </div>

        <div className="flex gap-2">
          <select
            value={filters.entry_type}
            onChange={(e) => handleFilterChange("entry_type", e.target.value)}
            className="input-field"
          >
            <option value="">All Types</option>
            <option value="general">General</option>
            <option value="trade_specific">Trade Specific</option>
          </select>

          <input
            type="date"
            value={filters.date_from}
            onChange={(e) => handleFilterChange("date_from", e.target.value)}
            className="input-field"
            placeholder="From Date"
          />

          <input
            type="date"
            value={filters.date_to}
            onChange={(e) => handleFilterChange("date_to", e.target.value)}
            className="input-field"
            placeholder="To Date"
          />
        </div>
      </div>

      {/* Controls Section */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex gap-2">
          <button
            onClick={expandAll}
            disabled={paginationLoading || entries.length === 0}
            className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Expand All
          </button>
          <button
            onClick={collapseAll}
            disabled={paginationLoading || (!expandedRowId && !expandedAll)}
            className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Collapse All
          </button>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            {totalEntries} entries total
          </span>
          <select
            value={entriesPerPage}
            onChange={(e) => {
              setEntriesPerPage(Number(e.target.value));
              setCurrentPage(1);
              updateURL({ per_page: e.target.value, page: 1 });
            }}
            disabled={paginationLoading}
            className="input-field"
          >
            <option value={10}>10 per page</option>
            <option value={25}>25 per page</option>
            <option value={50}>50 per page</option>
          </select>
        </div>
      </div>

      {/* Journal Entries Table */}
      <div className="card overflow-hidden">
        {paginationLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : entries.length === 0 ? (
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
                {entries.map((entry) => (
                  <React.Fragment key={entry.id}>
                    <tr
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => handleRowClick(entry.id)}
                    >
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
                        <div className="flex items-center justify-between">
                          <div className="max-w-xs truncate">{entry.notes}</div>
                          <ChevronDown
                            className={`h-4 w-4 transition-transform ${
                              expandedRowId === entry.id || expandedAll
                                ? "rotate-180"
                                : ""
                            }`}
                          />
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {format(new Date(entry.created_at), "MMM dd, yyyy")}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteEntry(entry.id);
                          }}
                          className="text-red-600 hover:text-red-900 ml-4"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                    {(expandedRowId === entry.id || expandedAll) && (
                      <tr className="bg-gray-50">
                        <td colSpan={5} className="px-6 py-4">
                          <div
                            className="whitespace-pre-wrap text-sm text-gray-700"
                            dangerouslySetInnerHTML={{
                              __html: highlightSearchTerms(
                                entry.notes,
                                searchTerm
                              ),
                            }}
                          />
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination Controls */}
      {entries.length > 0 && (
        <div className="flex justify-between items-center mt-4">
          <div className="text-sm text-gray-600">
            Showing {(currentPage - 1) * entriesPerPage + 1} to{" "}
            {Math.min(currentPage * entriesPerPage, totalEntries)} of{" "}
            {totalEntries} entries
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => {
                setCurrentPage(currentPage - 1);
                updateURL({ page: currentPage - 1 });
              }}
              disabled={currentPage === 1 || paginationLoading}
              className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              Previous
            </button>

            <span className="px-3 py-2 text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </span>

            <button
              onClick={() => {
                setCurrentPage(currentPage + 1);
                updateURL({ page: currentPage + 1 });
              }}
              disabled={currentPage === totalPages || paginationLoading}
              className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
