CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY,
  source TEXT NOT NULL,
  generated_at TEXT NOT NULL,
  market_session TEXT,
  base_currency TEXT NOT NULL,
  net_liquidation REAL,
  daily_pnl REAL,
  unrealized_pnl REAL,
  realized_pnl REAL,
  margin_value REAL,
  raw_hash TEXT
);

CREATE TABLE IF NOT EXISTS positions (
  snapshot_id INTEGER NOT NULL,
  ticker TEXT NOT NULL,
  conid TEXT,
  asset_class TEXT,
  currency TEXT,
  units REAL,
  unit_price REAL,
  market_value REAL,
  daily_pnl REAL,
  unrealized_pnl REAL,
  FOREIGN KEY(snapshot_id) REFERENCES snapshots(id)
);

CREATE TABLE IF NOT EXISTS flex_account_values (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,
  account_id TEXT NOT NULL,
  name TEXT NOT NULL,
  currency TEXT,
  section TEXT,
  value REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS flex_dividends (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,
  account_id TEXT NOT NULL,
  symbol TEXT,
  description TEXT,
  type TEXT,
  currency TEXT,
  amount REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS flex_fees (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,
  account_id TEXT NOT NULL,
  symbol TEXT,
  description TEXT,
  type TEXT,
  currency TEXT,
  amount REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS flex_realized_pnl (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,
  account_id TEXT NOT NULL,
  symbol TEXT,
  description TEXT,
  currency TEXT,
  realized_pnl REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS flex_trades (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,
  account_id TEXT NOT NULL,
  symbol TEXT,
  description TEXT,
  asset_class TEXT,
  currency TEXT,
  quantity REAL NOT NULL,
  price REAL NOT NULL,
  proceeds REAL NOT NULL,
  commission REAL NOT NULL,
  realized_pnl REAL NOT NULL
);
