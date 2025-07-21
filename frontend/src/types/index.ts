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
