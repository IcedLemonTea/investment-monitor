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
