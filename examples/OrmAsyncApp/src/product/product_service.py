from .product_model import Product
from .product_entity import Product as ProductEntity
from nest.core.decorators import async_db_request_handler

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ProductService:
    @async_db_request_handler
    async def add_product(self, product: Product, session: AsyncSession):
        new_product = ProductEntity(**product.dict())
        session.add(new_product)
        await session.commit()
        return new_product.id

    @async_db_request_handler
    async def get_product(self, session: AsyncSession):
        query = select(ProductEntity)
        result = await session.execute(query)
        return result.scalars().all()
