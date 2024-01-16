from beanie import Document


class Product(Document):
    title: str

    class Config:
        schema_extra = {"example": {"title": "Example Title",}}
