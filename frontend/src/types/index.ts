export interface PricePoint {
  timestamp: string;
  price: number;
}

export interface WatchItem {
  item_code: string;
  keyword: string;
  title: string;
  url: string;
  image: string | null;
  current_price: number;
  price_history: PricePoint[];
  notify: boolean;
  drop_rate_threshold: number;
  notify_to: string | null;
  last_checked: string | null;
}

export interface AddItemRequest {
  keyword: string;
  notify?: boolean;
  drop_rate_threshold?: number;
  notify_to?: string | null;
}

export interface UpdateItemRequest {
  notify?: boolean;
  drop_rate_threshold?: number;
  notify_to?: string | null;
}

export interface CheckResult {
  item_code: string;
  checked: boolean;
  notified: boolean;
  message: string;
}

export interface CheckSummary {
  checked_at: string;
  checked_count: number;
  notified_count: number;
  results: CheckResult[];
}
