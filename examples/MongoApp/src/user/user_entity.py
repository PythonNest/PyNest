from beanie import Document


class User(Document):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Example Name",
            }
        }
