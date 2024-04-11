from beanie import Document


class Example(Document):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Example Name",
            }
        }
