from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import Order, OrderItem, Product
from app.schemas import OrderItemCreate

class InsufficientStockError(Exception):
    pass

class ProductNotFoundError(Exception):
    pass

class OrderNotFoundError(Exception):
    pass

async def add_item_to_order(
    db: AsyncSession,
    order_id: int,
    item_data: OrderItemCreate
) -> dict:
    order_result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = order_result.scalar_one_or_none()
    if not order:
        raise OrderNotFoundError(f"Р—Р°РєР°Р· {order_id} РЅРµ РЅР°Р№РґРµРЅ")
    
    product_result = await db.execute(
        select(Product).where(Product.id == item_data.product_id).with_for_update()
    )
    product = product_result.scalar_one_or_none()
    
    if not product:
        raise ProductNotFoundError(f"РўРѕРІР°СЂ {item_data.product_id} РЅРµ РЅР°Р№РґРµРЅ")
    
    existing_item_result = await db.execute(
        select(OrderItem).where(
            OrderItem.order_id == order_id,
            OrderItem.product_id == item_data.product_id
        )
    )
    existing_item = existing_item_result.scalar_one_or_none()
    
    if product.quantity < item_data.quantity:
        raise InsufficientStockError(
            f"РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ С‚РѕРІР°СЂР° '{product.name}' РЅР° СЃРєР»Р°РґРµ. "
            f"Р”РѕСЃС‚СѓРїРЅРѕ: {product.quantity}, С‚СЂРµР±СѓРµС‚СЃСЏ: {item_data.quantity}"
        )
    
    if existing_item:
        existing_item.quantity += item_data.quantity
        existing_item.price = product.price
        total_quantity = existing_item.quantity
    else:
        new_item = OrderItem(
            order_id=order_id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price=product.price
        )
        db.add(new_item)
        total_quantity = item_data.quantity
    
    await db.execute(
        update(Product)
        .where(Product.id == item_data.product_id)
        .values(quantity=Product.quantity - item_data.quantity)
    )
    
    await db.commit()
    
    return {
        "success": True,
        "message": "РўРѕРІР°СЂ РґРѕР±Р°РІР»РµРЅ РІ Р·Р°РєР°Р·",
        "order_id": order_id,
        "product_id": item_data.product_id,
        "quantity_added": item_data.quantity,
        "total_quantity": total_quantity
    }
