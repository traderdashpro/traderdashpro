const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Trades API
  async getTrades(params?: {
    trading_type?: string;
    win_loss?: string;
    date_from?: string;
    date_to?: string;
  }): Promise<any> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) searchParams.append(key, value);
      });
    }

    const queryString = searchParams.toString();
    const endpoint = `/api/trades/${queryString ? `?${queryString}` : ""}`;

    return this.request(endpoint);
  }

  async createTrade(tradeData: {
    date: string;
    ticker_symbol: string;
    number_of_shares: number;
    buy_price: number;
    sell_price: number;
    trading_type: "Swing" | "Day";
  }): Promise<any> {
    return this.request("/api/trades/", {
      method: "POST",
      body: JSON.stringify(tradeData),
    });
  }

  async updateTrade(
    id: string,
    tradeData: Partial<{
      date: string;
      ticker_symbol: string;
      number_of_shares: number;
      buy_price: number;
      sell_price: number;
      trading_type: "Swing" | "Day";
    }>
  ): Promise<any> {
    return this.request(`/api/trades/${id}/`, {
      method: "PUT",
      body: JSON.stringify(tradeData),
    });
  }

  async deleteTrade(id: string): Promise<any> {
    return this.request(`/api/trades/${id}`, {
      method: "DELETE",
    });
  }

  // Journal API
  async getJournalEntries(params?: {
    trade_id?: string;
    entry_type?: string;
    date_from?: string;
    date_to?: string;
  }): Promise<any> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) searchParams.append(key, value);
      });
    }

    const queryString = searchParams.toString();
    const endpoint = `/api/journal/${queryString ? `?${queryString}` : ""}`;

    return this.request(endpoint);
  }

  async createJournalEntry(entryData: {
    date: string;
    notes: string;
    trade_id?: string;
  }): Promise<any> {
    return this.request("/api/journal/", {
      method: "POST",
      body: JSON.stringify(entryData),
    });
  }

  async updateJournalEntry(
    id: string,
    entryData: Partial<{
      date: string;
      notes: string;
      trade_id?: string;
    }>
  ): Promise<any> {
    return this.request(`/api/journal/${id}/`, {
      method: "PUT",
      body: JSON.stringify(entryData),
    });
  }

  async deleteJournalEntry(id: string): Promise<any> {
    return this.request(`/api/journal/${id}/`, {
      method: "DELETE",
    });
  }

  async getInsights(): Promise<any> {
    return this.request("/api/journal/insights/");
  }

  // Dashboard API - No trailing slashes for these endpoints
  async getDashboardStats(trading_type?: string): Promise<any> {
    const endpoint = trading_type
      ? `/api/dashboard/stats?trading_type=${trading_type}`
      : "/api/dashboard/stats";

    return this.request(endpoint);
  }

  async getChartData(trading_type?: string): Promise<any> {
    const endpoint = trading_type
      ? `/api/dashboard/chart?trading_type=${trading_type}`
      : "/api/dashboard/chart";

    return this.request(endpoint);
  }

  async getTradingTypeStats(): Promise<any> {
    return this.request("/api/dashboard/trading-type-stats");
  }
}

export const apiClient = new ApiClient();
