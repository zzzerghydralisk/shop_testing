from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas import (
    OrderItemCreate, 
    AddToOrderResponse,
    ClientTotal,
    CategoryChildCount,
    TopProduct
)
from app.services.order_service import (
    add_item_to_order,
    InsufficientStockError,
    ProductNotFoundError,
    OrderNotFoundError
)
from app.services.report_service import ReportService

router = APIRouter()

@router.post(
    "/orders/{order_id}/items",
    response_model=AddToOrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Р”РѕР±Р°РІРёС‚СЊ С‚РѕРІР°СЂ РІ Р·Р°РєР°Р·"
)
async def add_to_order(
    order_id: int,
    item: OrderItemCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await add_item_to_order(db, order_id, item)
        return result
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientStockError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Р’РЅСѓС‚СЂРµРЅРЅСЏСЏ РѕС€РёР±РєР°: {str(e)}")

@router.get(
    "/reports/client-totals",
    response_model=List[ClientTotal],
    summary="2.1 РЎСѓРјРјР° Р·Р°РєР°Р·РѕРІ РїРѕ РєР»РёРµРЅС‚Р°Рј"
)
async def get_client_totals(db: AsyncSession = Depends(get_db)):
    return await ReportService.get_client_totals(db)

@router.get(
    "/reports/category-child-counts",
    response_model=List[CategoryChildCount],
    summary="2.2 РљРѕР»РёС‡РµСЃС‚РІРѕ РґРѕС‡РµСЂРЅРёС… РєР°С‚РµРіРѕСЂРёР№"
)
async def get_category_child_counts(db: AsyncSession = Depends(get_db)):
    return await ReportService.get_category_child_counts(db)

@router.get(
    "/reports/top-products",
    response_model=List[TopProduct],
    summary="2.3.1 РўРѕРї-5 С‚РѕРІР°СЂРѕРІ Р·Р° РїРѕСЃР»РµРґРЅРёР№ РјРµСЃСЏС†"
)
async def get_top_products(db: AsyncSession = Depends(get_db)):
    return await ReportService.get_top_products_last_month(db)

@router.get(
    "/reports/top-products-optimized",
    response_model=List[TopProduct],
    summary="2.3.2 РўРѕРї-5 С‚РѕРІР°СЂРѕРІ (РѕРїС‚РёРјРёР·РёСЂРѕРІР°РЅРѕ)"
)
async def get_top_products_optimized(db: AsyncSession = Depends(get_db)):
    return await ReportService.get_top_products_optimized(db)

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "shop-api"}
