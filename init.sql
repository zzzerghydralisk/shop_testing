-- init.sql
-- Схема БД для тестового задания

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    path VARCHAR(1000) NOT NULL,
    level INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL,
    UNIQUE(order_id, product_id)
);

CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_path ON categories(path);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_orders_created ON orders(created_at);
CREATE INDEX idx_orders_client ON orders(client_id);

INSERT INTO categories (id, name, parent_id, path, level) VALUES
(1, 'Электроника', NULL, '1', 0),
(2, 'Компьютеры', 1, '1.2', 1),
(3, 'Ноутбуки', 2, '1.2.3', 2),
(4, 'Смартфоны', 1, '1.4', 1),
(5, 'Бытовая техника', NULL, '5', 0),
(6, 'Холодильники', 5, '5.6', 1),
(7, 'Микроволновки', 5, '5.7', 1);

INSERT INTO products (name, category_id, quantity, price) VALUES
('MacBook Pro 16', 3, 10, 250000.00),
('MacBook Air', 3, 15, 120000.00),
('Dell XPS 15', 3, 8, 180000.00),
('iPhone 15 Pro', 4, 20, 120000.00),
('Samsung Galaxy S24', 4, 25, 95000.00),
('Xiaomi 14', 4, 30, 60000.00),
('Bosch Series 4', 6, 5, 45000.00),
('Samsung RB30', 6, 7, 52000.00),
('LG NeoChef', 7, 12, 15000.00),
('Samsung MS23', 7, 15, 12000.00),
('Sony WH-1000XM5', 1, 20, 35000.00),
('AirPods Pro 2', 1, 25, 25000.00);

INSERT INTO clients (name, address) VALUES
('Иванов Иван Иванович', 'г. Москва, ул. Ленина, д. 1'),
('Петров Петр Петрович', 'г. Санкт-Петербург, Невский пр., д. 10'),
('Сидоров Сидор Сидорович', 'г. Казань, ул. Баумана, д. 5'),
('Алексеев Алексей Алексеевич', 'г. Новосибирск, Красный пр., д. 15'),
('Дмитриев Дмитрий Дмитриевич', 'г. Екатеринбург, ул. Ленина, д. 20');

INSERT INTO orders (id, client_id, created_at) VALUES
(1, 1, NOW() - INTERVAL '5 days'),
(2, 2, NOW() - INTERVAL '10 days'),
(3, 1, NOW() - INTERVAL '15 days'),
(4, 3, NOW() - INTERVAL '25 days');

INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
(1, 1, 1, 250000.00),
(1, 4, 2, 120000.00),
(2, 2, 1, 120000.00),
(2, 5, 1, 95000.00),
(2, 9, 1, 15000.00),
(3, 3, 2, 180000.00),
(3, 6, 3, 60000.00),
(4, 7, 1, 45000.00);

CREATE OR REPLACE VIEW client_order_totals AS
SELECT 
    c.id as client_id,
    c.name as client_name,
    COALESCE(SUM(oi.quantity * oi.price), 0) as total_sum
FROM clients c
LEFT JOIN orders o ON c.id = o.client_id
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY c.id, c.name;

CREATE OR REPLACE VIEW category_child_count AS
SELECT 
    c.id as category_id,
    c.name as category_name,
    c.level,
    COUNT(child.id) as child_count_first_level
FROM categories c
LEFT JOIN categories child ON child.parent_id = c.id
GROUP BY c.id, c.name, c.level;

CREATE OR REPLACE VIEW top_products_last_month AS
WITH RECURSIVE category_tree AS (
    SELECT 
        c.id as cat_id,
        c.name as cat_name,
        c.id as root_id,
        c.name as root_name,
        c.level
    FROM categories c
    WHERE c.parent_id IS NULL
    UNION ALL
    SELECT 
        c.id,
        c.name,
        ct.root_id,
        ct.root_name,
        c.level
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.cat_id
)
SELECT 
    p.name as product_name,
    ct.root_name as category_level_1,
    SUM(oi.quantity)::int as total_sold
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
JOIN category_tree ct ON p.category_id = ct.cat_id
WHERE o.created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
   AND o.created_at < DATE_TRUNC('month', CURRENT_DATE)
GROUP BY p.id, p.name, ct.root_name
ORDER BY total_sold DESC
LIMIT 5;

CREATE MATERIALIZED VIEW mv_top_products_monthly AS
WITH RECURSIVE category_tree AS (
    SELECT id, name, id as root_id, name as root_name
    FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, ct.root_id, ct.root_name
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT 
    p.id as product_id,
    p.name as product_name,
    ct.root_name as category_level_1,
    DATE_TRUNC('month', o.created_at) as order_month,
    SUM(oi.quantity) as total_sold,
    SUM(oi.quantity * oi.price) as total_revenue
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
JOIN category_tree ct ON p.category_id = ct.id
GROUP BY p.id, p.name, ct.root_name, DATE_TRUNC('month', o.created_at);

CREATE INDEX idx_mv_top_products_month ON mv_top_products_monthly(order_month, total_sold DESC);

CREATE OR REPLACE FUNCTION refresh_top_products_mv()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_products_monthly;
END;
$$ LANGUAGE plpgsql;
