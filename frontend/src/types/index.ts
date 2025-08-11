export interface Trade {
  id: string;
  date: string;
  ticker_symbol: string;
  number_of_shares: number;
  price_cost_basis: number;
  proceeds: number;
  buy_price: number;
  sell_price: number;
  trading_type: "Swing" | "Day";
  win_loss: "Win" | "Loss";
  created_at: string;
  updated_at: string;
}

export interface JournalEntry {
  id: string;
  date: string;
  notes: string;
  trade_id?: string;
  entry_type: "trade_specific" | "general";
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total_trades: number;
  win_count: number;
  loss_count: number;
  win_rate: number;
  total_profit_loss: number;
  avg_profit_loss: number;
  recent_profit_loss: number;
  recent_trades_count: number;
}

export interface ChartData {
  labels: string[];
  data: number[];
  backgroundColor?: string[];
}

export interface DashboardData {
  donut_chart: ChartData;
  line_chart: ChartData;
}

export interface TradingTypeStats {
  total_trades: number;
  win_count: number;
  loss_count: number;
  total_profit_loss: number;
  win_rate: number;
}

// Authentication Types
export interface User {
  id: string;
  email: string;
  is_confirmed: boolean;
  plan: "free" | "premium" | "pro";
  last_ai_insights_date?: string;
  next_ai_insights_date?: string;
  can_get_ai_insights: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  message: string;
  token?: string;
  user?: User;
  user_id?: string;
  email?: string;
  is_confirmed?: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupCredentials {
  email: string;
  password: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  signup: (credentials: SignupCredentials) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface TradesResponse extends ApiResponse<Trade[]> {
  trades?: Trade[];
}

export interface JournalResponse extends ApiResponse<JournalEntry[]> {
  entries?: JournalEntry[];
}

export interface StatsResponse extends ApiResponse<DashboardStats> {
  stats?: DashboardStats;
}

export interface ChartResponse extends ApiResponse<DashboardData> {
  donut_chart?: ChartData;
  line_chart?: ChartData;
}

export interface InsightsResponse extends ApiResponse<string> {
  insights?: string;
}

export interface AIInsights {
  key_patterns: string[];
  strengths: string[];
  areas_for_improvement: string[];
  emotional_state_analysis: string;
  trading_performance_insights: string;
  recommendations: string[];
}

export interface AIInsightsResponse extends ApiResponse<AIInsights> {
  insights?: AIInsights;
  plan?: string;
  can_get_insights?: boolean;
  last_insights_date?: string;
  next_available_date?: string;
  insights_created_at?: string;
}
