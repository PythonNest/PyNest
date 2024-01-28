from nest.core import Controller, Get, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config import config


from .product_service import ProductService
from .product_model import Product


@Controller("product")
class ProductController:

    service: ProductService = Depends(ProductService)

    @Get("/")
    async def get_product(self, session: AsyncSession = Depends(config.get_db)):
        return await self.service.get_product(session)

    @Post("/")
    async def add_product(
        self, product: Product, session: AsyncSession = Depends(config.get_db)
    ):
        return await self.service.add_product(product, session)
