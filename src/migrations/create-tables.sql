CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(36) PRIMARY KEY,
    vendor VARCHAR(24) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL,
    brand VARCHAR(100) NOT NULL,
    availability VARCHAR(100) NOT NULL,
    release_year VARCHAR(20) NOT NULL,
    link VARCHAR(100) NOT NULL,
    last_synced_at DATE NOT NULL,
    created_at DATE NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS unique_products_vendor_sku_name ON products (
    vendor,
    sku,
    name
);