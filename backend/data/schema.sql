PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS watch_items (
  item_code TEXT PRIMARY KEY,
  keyword TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  image TEXT,
  current_price INTEGER NOT NULL,
  notify INTEGER NOT NULL DEFAULT 1,
  drop_rate_threshold REAL NOT NULL DEFAULT 0.05,
  notify_to TEXT,
  last_checked TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS price_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_code TEXT NOT NULL,
  checked_at TEXT NOT NULL,
  price INTEGER NOT NULL,
  FOREIGN KEY (item_code) REFERENCES watch_items(item_code) ON DELETE CASCADE,
  UNIQUE(item_code, checked_at, price)
);

CREATE INDEX IF NOT EXISTS idx_price_history_item_code_checked_at
  ON price_history(item_code, checked_at DESC);

CREATE TABLE IF NOT EXISTS notification_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_code TEXT NOT NULL,
  notified_at TEXT NOT NULL,
  recipient TEXT,
  previous_price INTEGER NOT NULL,
  current_price INTEGER NOT NULL,
  drop_rate REAL NOT NULL,
  success INTEGER NOT NULL,
  message TEXT,
  FOREIGN KEY (item_code) REFERENCES watch_items(item_code) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notification_logs_item_code_notified_at
  ON notification_logs(item_code, notified_at DESC);
