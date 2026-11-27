CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    date_of_sale TEXT NOT NULL,
    address TEXT NOT NULL,
    county TEXT NOT NULL,
    eircode TEXT,
    price INTEGER NOT NULL,
    not_full_market_price INTEGER NOT NULL DEFAULT 0
        CHECK (not_full_market_price IN (0, 1)),
    vat_exclusive INTEGER NOT NULL DEFAULT 0
        CHECK (vat_exclusive IN (0, 1)),
    description_of_property TEXT,
    property_size_description TEXT
);

CREATE INDEX IF NOT EXISTS idx_sales_county
ON sales(county);

CREATE INDEX IF NOT EXISTS idx_sales_date
ON sales(date_of_sale);

-- Additional indexes for Sprint 2 price aggregations

CREATE INDEX IF NOT EXISTS idx_sales_market_price
ON sales(price)
WHERE not_full_market_price = 0;

CREATE INDEX IF NOT EXISTS idx_sales_market_type_price
ON sales(description_of_property, price)
WHERE not_full_market_price = 0;

CREATE INDEX IF NOT EXISTS idx_sales_market_county_price
ON sales(county, price)
WHERE not_full_market_price = 0;

-- Sprint 3: Persistent AI commentary cache

CREATE TABLE IF NOT EXISTS commentary_cache (
    cache_key TEXT PRIMARY KEY,
    response_text TEXT NOT NULL,
    generated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
