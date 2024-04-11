from beanie import Document


class Product(Document):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Example Name",
            }
        }
