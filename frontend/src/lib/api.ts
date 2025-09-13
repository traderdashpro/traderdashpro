import {
  LoginCredentials,
  SignupCredentials,
  AuthResponse,
  User,
} from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";

export class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    // Load token from localStorage on initialization
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("auth_token");
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== "undefined") {
      if (token) {
        localStorage.setItem("auth_token", token);
      } else {
        localStorage.removeItem("auth_token");
      }
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    // Add authorization header if token exists
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      headers,
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(
        errorData.message || `HTTP error! status: ${response.status}`
      );
      (error as any).response = { data: errorData, status: response.status };
      throw error;
    }

    return response.json();
  }

  // Authentication API
  async signup(credentials: SignupCredentials): Promise<AuthResponse> {
    return this.request<AuthResponse>("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });

    // Store token if login is successful
    if (response.token) {
      this.setToken(response.token);
    }

    return response;
  }

  async logout(): Promise<void> {
    try {
      await this.request("/api/auth/logout", {
        method: "POST",
      });
    } catch (error) {
      // Ignore logout errors
    } finally {
      this.setToken(null);
    }
  }

  async getCurrentUser(): Promise<{ user: User }> {
    return this.request<{ user: User }>("/api/auth/me");
  }

  async changePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<AuthResponse> {
    return this.request<AuthResponse>("/api/auth/change-password", {
      method: "POST",
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
  }

  async confirmEmail(token: string): Promise<AuthResponse> {
    return this.request<AuthResponse>("/api/auth/confirm-email", {
      method: "POST",
      body: JSON.stringify({ token }),
    });
  }

  async resendConfirmation(email: string): Promise<AuthResponse> {
    return this.request<AuthResponse>("/api/auth/resend-confirmation", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  }

  // Trades API
  async getTrades(params?: {
    trading_type?: string;
    win_loss?: string;
    status?: string;
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
    sell_price?: number;
    trading_type: "Swing" | "Day";
    transaction_type?: string;
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
      transaction_type?: string;
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

  // Positions API
  async getPositions(params?: {
    status?: string;
    symbol?: string;
  }): Promise<any> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) searchParams.append(key, value);
      });
    }

    const queryString = searchParams.toString();
    const endpoint = `/api/trades/positions/${
      queryString ? `?${queryString}` : ""
    }`;

    return this.request(endpoint);
  }

  async getPositionDetails(positionId: string): Promise<any> {
    return this.request(`/api/trades/positions/${positionId}`);
  }

  // Journal API
  async getJournalEntries(params?: {
    trade_id?: string;
    entry_type?: string;
    date_from?: string;
    date_to?: string;
    search?: string;
    page?: number;
    per_page?: number;
  }): Promise<any> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
          searchParams.append(key, value.toString());
        }
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
    return this.request(`/api/journal/${id}`, {
      method: "DELETE",
    });
  }

  async getInsights(): Promise<any> {
    return this.request("/api/journal/insights");
  }

  async getStoredInsights(): Promise<any> {
    return this.request("/api/journal/stored-insights");
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

  async uploadStatement(formData: FormData): Promise<any> {
    const url = `${this.baseUrl}/api/dashboard/upload-statement`;

    const headers: Record<string, string> = {};

    // Add authorization header if token exists
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(
        errorData.message || `HTTP error! status: ${response.status}`
      );
      (error as any).response = { data: errorData, status: response.status };
      throw error;
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
