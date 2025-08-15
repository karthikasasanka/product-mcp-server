import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional

from mcp_api.product.schemas import ProductIn, Product
from mcp_api.product import crud
from mcp_api.datbase import get_db
from sqlalchemy.ext.asyncio import AsyncSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=Product, status_code=201, operation_id="product.create")
async def create(product: ProductIn, db: AsyncSession = Depends(get_db)) -> Product:
    logger.info(f"🚀 Creating product: {product}")
    try:
        row = await crud.create_product(db, product)
        logger.info(f"✅ Product created successfully: {row}")
        return row
    except Exception as e:
        logger.error(f"❌ Error creating product: {e}", exc_info=True)
        raise


@router.get("/{product_id}", response_model=Product, operation_id="product.get")
async def get(product_id: int, db: AsyncSession = Depends(get_db)) -> Product:
    logger.info(f"🔍 Getting product with ID: {product_id}")
    try:
        row = await crud.get_product(db, product_id)
        if not row:
            logger.warning(f"⚠️ Product not found with ID: {product_id}")
            raise HTTPException(status_code=404, detail="Product not found")
        logger.info(f"✅ Product retrieved successfully: {row}")
        return row
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting product: {e}", exc_info=True)
        raise


@router.get("", response_model=List[Product], operation_id="product.list")
async def list_(skip: int = Query(0, ge=0), limit: int = Query(100, gt=0, le=1000), recent_only: bool = Query(False), name_prefix: str = Query(default=""), db: AsyncSession = Depends(get_db)) -> List[Product]:
    logger.info(f"📋 Listing products (skip: {skip}, limit: {limit}, recent_only: {recent_only}, name_prefix: {name_prefix})")
    try:
        rows = await crud.list_products(db, skip=skip, limit=limit, recent_only=recent_only, name_prefix=name_prefix)
        logger.info(f"✅ Retrieved {len(rows)} products")
        return rows
    except Exception as e:
        logger.error(f"❌ Error listing products: {e}", exc_info=True)
        raise


@router.put("/{product_id}", response_model=Product, operation_id="product.update")
async def update(product_id: int, data: ProductIn, db: AsyncSession = Depends(get_db)) -> Product:
    logger.info(f"🔄 Updating product {product_id} with data: {data}")
    try:
        row = await crud.update_product(db, product_id, data)
        if not row:
            logger.warning(f"⚠️ Product not found for update with ID: {product_id}")
            raise HTTPException(status_code=404, detail="Product not found")
        logger.info(f"✅ Product updated successfully: {row}")
        return row
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating product: {e}", exc_info=True)
        raise


@router.delete("/{product_id}", operation_id="product.delete")
async def delete(product_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    logger.info(f"🗑️ Deleting product with ID: {product_id}")
    try:
        ok = await crud.delete_product(db, product_id)
        if not ok:
            logger.warning(f"⚠️ Product not found for deletion with ID: {product_id}")
            raise HTTPException(status_code=404, detail="Product not found")
        logger.info(f"✅ Product deleted successfully")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting product: {e}", exc_info=True)
        raise


