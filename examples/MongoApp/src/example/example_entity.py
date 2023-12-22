from beanie import Document
        
        
class Example(Document):
    title: str
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Example Title",
            }
        }
