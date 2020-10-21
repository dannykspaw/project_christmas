CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(36) PRIMARY KEY,
    vendor VARCHAR(24) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    price FLOAT NOT NULL,
    brand VARCHAR(100) NOT NULL,
    availability VARCHAR(20) NOT NULL,
    release_year VARCHAR(20) NOT NULL,
    link VARCHAR(200) NOT NULL,
    last_synced_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS unique_products_vendor_sku_name_link ON products (
    vendor,
    sku,
    name,
    link
);