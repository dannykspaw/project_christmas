CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(24) PRIMARY KEY,
    vendor VARCHAR(24) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    name VARCHAR(40) NOT NULL,
    price FLOAT NOT NULL,
    brand VARCHAR(40) NOT NULL,
    availability VARCHAR(10) NOT NULL,
    release_year VARCHAR(20) NOT NULL,
    vendor_id VARCHAR(20) NOT NULL,
    link VARCHAR(100) NOT NULL,
    last_synced_at DATE NOT NULL,
    created_at DATE NOT NULL
)