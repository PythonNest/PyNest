from beanie import Document


class User(Document):
    title: str

    class Config:
        schema_extra = {"example": {"title": "Example Title",}}
