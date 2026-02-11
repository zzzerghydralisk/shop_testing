from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List
from app.schemas import ClientTotal, CategoryChildCount, TopProduct

class ReportService:
    
    @staticmethod
    async def get_client_totals(db: AsyncSession) -> List[ClientTotal]:
        query = text("""
            SELECT 
                c.id as client_id,
                c.name as client_name,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_sum
            FROM clients c
            LEFT JOIN orders o ON c.id = o.client_id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY c.id, c.name
            ORDER BY total_sum DESC
        """)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        return [
            ClientTotal(
                client_id=row.client_id,
                client_name=row.client_name,
                total_sum=row.total_sum
            )
            for row in rows
        ]
    
    @staticmethod
    async def get_category_child_counts(db: AsyncSession) -> List[CategoryChildCount]:
        query = text("""
            SELECT 
                c.id as category_id,
                c.name as category_name,
                c.level,
                COUNT(child.id) as child_count_first_level
            FROM categories c
            LEFT JOIN categories child ON child.parent_id = c.id
            GROUP BY c.id, c.name, c.level
            ORDER BY c.path
        """)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        return [
            CategoryChildCount(
                category_id=row.category_id,
                category_name=row.category_name,
                level=row.level,
                child_count_first_level=row.child_count_first_level
            )
            for row in rows
        ]
    
    @staticmethod
    async def get_top_products_last_month(db: AsyncSession) -> List[TopProduct]:
        query = text("""
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
            LIMIT 5
        """)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        return [
            TopProduct(
                product_name=row.product_name,
                category_level_1=row.category_level_1,
                total_sold=row.total_sold
            )
            for row in rows
        ]
    
    @staticmethod
    async def get_top_products_optimized(db: AsyncSession) -> List[TopProduct]:
        query = text("""
            SELECT 
                product_name,
                category_level_1,
                total_sold::int as total_sold
            FROM mv_top_products_monthly
            WHERE order_month = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
            ORDER BY total_sold DESC
            LIMIT 5
        """)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        return [
            TopProduct(
                product_name=row.product_name,
                category_level_1=row.category_level_1,
                total_sold=row.total_sold
            )
            for row in rows
        ]
