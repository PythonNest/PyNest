from sqlalchemy.ext.asyncio import AsyncSession

from nest.core import Controller, Depends, Get, Post

from ..config import config
from .product_model import Product
from .product_service import ProductService


@Controller("product")
class ProductController:
    def __init__(self, service: ProductService):
        self.service = service

    @Get("/")
    async def get_product(self, session: AsyncSession = Depends(config.get_db)):
        return await self.service.get_product(session)

    @Post("/")
    async def add_product(
        self, product: Product, session: AsyncSession = Depends(config.get_db)
    ):
        return await self.service.add_product(product, session)
