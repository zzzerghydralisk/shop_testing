# Shop API

Тестовое задание - Backend Магазина - FastAPI + PostgreSQL + Docker

## Запуск

git clone https://github.com/zzzerghydralisk/shop-test.git
cd shop-test
docker-compose up --build

| Метод | URL                                      | Описание                        |
| ----- | ---------------------------------------- | ------------------------------- |
| GET   | `/api/v1/health`                         | Проверка работы                 |
| POST  | `/api/v1/orders/{id}/items`              | Добавить товар в заказ          |
| GET   | `/api/v1/reports/client-totals`          | Сумма заказов по клиентам (2.1) |
| GET   | `/api/v1/reports/category-child-counts`  | Дочерние категории (2.2)        |
| GET   | `/api/v1/reports/top-products`           | Топ-5 товаров (2.3.1)           |
| GET   | `/api/v1/reports/top-products-optimized` | Оптимизированная версия (2.3.2) |

---

| Пункт | Где в init.sql                                               | Строки   |
| ----- | ------------------------------------------------------------ | -------- |
| 2.1   | `CREATE VIEW client_order_totals`                            | ~120-130 |
| 2.2   | `CREATE VIEW category_child_count`                           | ~132-142 |
| 2.3.1 | `CREATE VIEW top_products_last_month`                        | ~144-180 |
| 2.3.2 | `CREATE MATERIALIZED VIEW mv_top_products_monthly` + индексы | ~182-210 |

-- 2.1 Сумма по клиентам
SELECT c.name, COALESCE(SUM(oi.quantity * oi.price), 0) 
FROM clients c 
LEFT JOIN orders o ON c.id = o.client_id 
LEFT JOIN order_items oi ON o.id = oi.order_id 
GROUP BY c.id, c.name;

-- 2.2 Дочерние категории
SELECT c.id, c.name, COUNT(child.id) 
FROM categories c 
LEFT JOIN categories child ON child.parent_id = c.id 
GROUP BY c.id, c.name;

-- 2.3.1 Топ-5 товаров (через RECURSIVE CTE)
-- 2.3.2 Оптимизация: Materialized View + индексы

---

# Проверка работы API
curl http://localhost:8000/api/v1/health

# 2.1 Сумма заказов по клиентам
curl http://localhost:8000/api/v1/reports/client-totals

# 2.2 Дочерние категории
curl http://localhost:8000/api/v1/reports/category-child-counts

# 2.3.1 Топ-5 товаров за месяц
curl http://localhost:8000/api/v1/reports/top-products

# 2.3.2 Оптимизированная версия
curl http://localhost:8000/api/v1/reports/top-products-optimized

# 3. Добавить товар в заказ (успех)
curl -X POST http://localhost:8000/api/v1/orders/1/items \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 1}'

# 3. Добавить товар (ошибка - недостаточно на складе)
curl -X POST http://localhost:8000/api/v1/orders/1/items \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 999}'

# 3. Добавить товар (увеличение количества существующей позиции)
curl -X POST http://localhost:8000/api/v1/orders/1/items \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'

