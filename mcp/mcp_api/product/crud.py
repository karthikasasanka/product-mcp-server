from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from mcp_api.product.schemas import ProductIn
from mcp_api.product.models import Product


async def create_product(db: AsyncSession, data: ProductIn) -> Product:
    row = Product(name=data.name, price=data.price, description=data.description)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def get_product(db: AsyncSession, product_id: int) -> Optional[Product]:
    row = await db.get(Product, product_id)
    return row


async def list_products(db: AsyncSession, skip: int = 0, limit: int = 100, recent_only: bool = False, name_prefix: str = "") -> List[Product]:
    from sqlalchemy import select, desc
    query = select(Product)
    
    # Filter by name prefix if provided
    if name_prefix and name_prefix.strip():
        query = query.filter(Product.name.ilike(f"{name_prefix}%"))
    
    if recent_only:
        # Order by ID in descending order to get the most recent products first
        query = query.order_by(desc(Product.id))
    
    result = await db.execute(query.offset(skip).limit(limit))
    rows = result.scalars().all()
    return rows


async def update_product(db: AsyncSession, product_id: int, data: ProductIn) -> Optional[Product]:
    row = await db.get(Product, product_id)
    if not row:
        return None
    if data.name is not None:
        row.name = data.name
    if data.price is not None:
        row.price = data.price
    if data.description is not None:
        row.description = data.description
    await db.commit()
    await db.refresh(row)
    return row


async def delete_product(db: AsyncSession, product_id: int) -> bool:
    row = await db.get(Product, product_id)
    if not row:
        return False
    await db.delete(row)
    await db.commit()
    return True


