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
