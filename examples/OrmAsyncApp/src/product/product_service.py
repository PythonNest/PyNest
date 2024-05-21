from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler

from .product_entity import Product as ProductEntity
from .product_model import Product


@Injectable
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
